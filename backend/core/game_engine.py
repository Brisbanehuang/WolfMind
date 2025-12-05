# -*- coding: utf-8 -*-
# pylint: disable=too-many-branches, too-many-statements, no-name-in-module
"""A werewolf game implemented by agentscope."""
from typing import Any
from datetime import datetime
from agentscope.message._message_base import Msg
import numpy as np

from config import config
from core.utils import (
    majority_vote,
    names_to_str,
    EchoAgent,
    MAX_GAME_ROUND,
    MAX_DISCUSSION_ROUND,
    Players,
    Prompts,
)
from core.game_logger import GameLogger
from models.schemas import (
    DiscussionModel,
    get_vote_model,
)
from models.roles import (
    RoleFactory,
    Werewolf,
    Villager,
    Seer,
    Witch,
    Hunter,
)

from agentscope.agent import ReActAgent
from agentscope.pipeline import (
    MsgHub,
    sequential_pipeline,
    fanout_pipeline,
)


moderator = EchoAgent()


async def werewolves_game(agents: list[ReActAgent]) -> None:
    """The main entry of the werewolf game

    Args:
        agents (`list[ReActAgent]`):
            A list of 9 agents.
    """
    assert len(agents) == 9, "The werewolf game needs exactly 9 players."

    # 初始化游戏日志
    game_id = datetime.now().strftime("%Y%m%d_%H%M%S")
    logger = GameLogger(game_id)

    # Init the players' status
    players = Players()

    # If the witch has healing and poison potion
    healing, poison = True, True

    # If it's the first day, the dead can leave a message
    first_day = True

    # Broadcast the game begin message
    async with MsgHub(participants=agents) as greeting_hub:
        await greeting_hub.broadcast(
            await moderator(
                Prompts.to_all_new_game.format(names_to_str(agents)),
            ),
        )

    # Assign roles to the agents
    roles = ["werewolf"] * 3 + ["villager"] * 3 + ["seer", "witch", "hunter"]
    np.random.shuffle(agents)
    np.random.shuffle(roles)

    for agent, role_name in zip(agents, roles):
        # 创建角色对象
        role_obj = RoleFactory.create_role(agent, role_name)

        # Tell the agent its role
        await agent.observe(
            await moderator(
                f"[{agent.name} ONLY] {agent.name}, your role is {role_name}.",
            ),
        )
        players.add_player(agent, role_name, role_obj)

    # Printing the roles
    players.print_roles()

    # 记录玩家列表到日志
    players_info = [(name, role)
                    for name, role in players.name_to_role.items()]
    logger.log_players(players_info)

    # GAME BEGIN!
    for round_num in range(1, MAX_GAME_ROUND + 1):
        # 开始新回合
        logger.start_round(round_num)
        # Create a MsgHub for all players to broadcast messages
        alive_agents = [role.agent for role in players.current_alive]
        async with MsgHub(
            participants=alive_agents,
            enable_auto_broadcast=False,  # manual broadcast only
            name="alive_players",
        ) as alive_players_hub:
            # Night phase
            logger.start_night()
            await alive_players_hub.broadcast(
                await moderator(Prompts.to_all_night),
            )
            killed_player, poisoned_player, shot_player = None, None, None

            # Werewolves discuss
            werewolf_agents = [w.agent for w in players.werewolves]
            async with MsgHub(
                werewolf_agents,
                enable_auto_broadcast=True,
                announcement=await moderator(
                    Prompts.to_wolves_discussion.format(
                        names_to_str(werewolf_agents),
                        names_to_str(players.current_alive),
                    ),
                ),
                name="werewolves",
            ) as werewolves_hub:
                # Discussion
                n_werewolves = len(players.werewolves)
                for _ in range(1, MAX_DISCUSSION_ROUND * n_werewolves + 1):
                    werewolf = players.werewolves[_ % n_werewolves]
                    res = await werewolf.discuss_with_team(
                        await moderator(""),
                    )
                    # 记录狼人讨论
                    speech = res.metadata.get("speech", "")
                    behavior = res.metadata.get("behavior", "")
                    if speech or behavior:
                        log_content = f"[{behavior}] {speech}" if behavior else speech
                        logger.log_message("狼人讨论", log_content, werewolf.name)
                    elif res.content:
                        logger.log_message("狼人讨论", res.content, werewolf.name)
                    if _ % n_werewolves == 0 and res.metadata.get(
                        "reach_agreement",
                    ):
                        break

                # Werewolves vote
                # Disable auto broadcast to avoid following other's votes
                werewolves_hub.set_auto_broadcast(False)
                vote_prompt = await moderator(content=Prompts.to_wolves_vote)
                msgs_vote = []
                for werewolf in players.werewolves:
                    msg = await werewolf.team_vote(vote_prompt, players.current_alive)
                    msgs_vote.append(msg)
                    # 记录狼人投票
                    target = msg.metadata.get("vote")
                    if target:
                        logger.log_vote(werewolf.name, target, "狼人投票")

                killed_player, votes = majority_vote(
                    [_.metadata.get("vote") for _ in msgs_vote],
                )
                # 记录狼人投票结果
                logger.log_vote_result(killed_player, votes, "狼人投票结果")

                # Postpone the broadcast of voting
                await werewolves_hub.broadcast(
                    [
                        *msgs_vote,
                        await moderator(
                            Prompts.to_wolves_res.format(votes, killed_player),
                        ),
                    ],
                )

            # Witch's turn
            await alive_players_hub.broadcast(
                await moderator(Prompts.to_all_witch_turn),
            )
            for witch in players.witch:
                game_state = {
                    "killed_player": killed_player,
                    "alive_players": players.current_alive,
                    "moderator": moderator,
                }

                result = await witch.night_action(game_state)

                # Log resurrect speech
                r_speech = result.get("resurrect_speech")
                r_behavior = result.get("resurrect_behavior")
                if r_speech or r_behavior:
                    log_content = f"[{r_behavior}] {r_speech}" if r_behavior else r_speech
                    logger.log_message("女巫行动(解药)", log_content, witch.name)

                # Log poison speech
                p_speech = result.get("poison_speech")
                p_behavior = result.get("poison_behavior")
                if p_speech or p_behavior:
                    log_content = f"[{p_behavior}] {p_speech}" if p_behavior else p_speech
                    logger.log_message("女巫行动(毒药)", log_content, witch.name)

                # 处理解药
                if result.get("resurrect"):
                    logger.log_action("女巫行动", f"使用解药救了 {killed_player}")
                    killed_player = None

                # 处理毒药
                if result.get("poison"):
                    poisoned_player = result.get("poison")
                    logger.log_action("女巫行动", f"使用毒药毒杀了 {poisoned_player}")

            # Seer's turn
            await alive_players_hub.broadcast(
                await moderator(Prompts.to_all_seer_turn),
            )
            for seer in players.seer:
                game_state = {
                    "alive_players": players.current_alive,
                    "moderator": moderator,
                    "name_to_role": players.name_to_role,
                }

                result = await seer.night_action(game_state)

                # Log speech/behavior
                speech = result.get("speech")
                behavior = result.get("behavior")
                if speech or behavior:
                    log_content = f"[{behavior}] {speech}" if behavior else speech
                    logger.log_message("预言家行动", log_content, seer.name)

                # 记录预言家查验
                if result and result.get("action") == "check":
                    checked_player = result.get("target")
                    role_result = result.get("result")
                    if checked_player and role_result:
                        logger.log_action(
                            "预言家查验", f"查验 {checked_player}, 结果: {role_result}")

            # Hunter's turn
            for hunter in players.hunter:
                # If killed and not by witch's poison
                if (
                    killed_player == hunter.name
                    and poisoned_player != hunter.name
                ):
                    shot_player = await hunter.shoot(players.current_alive, moderator)
                    if shot_player:
                        logger.log_action(
                            "猎人开枪", f"猎人 {hunter.name} 开枪击杀了 {shot_player}")

            # Update alive players
            dead_tonight = [killed_player, poisoned_player, shot_player]
            # 记录夜晚死亡
            logger.log_death("夜晚死亡", [p for p in dead_tonight if p])
            players.update_players(dead_tonight)

            # Day phase
            logger.start_day()
            if len([_ for _ in dead_tonight if _]) > 0:
                announcement = f"天亮了，请所有玩家睁眼。昨晚 {names_to_str([_ for _ in dead_tonight if _])} 被淘汰。"
                logger.log_announcement(announcement)
                await alive_players_hub.broadcast(
                    await moderator(
                        Prompts.to_all_day.format(
                            names_to_str([_ for _ in dead_tonight if _]),
                        ),
                    ),
                )

                # The killed player leave a last message in first night
                if killed_player and first_day:
                    msg_moderator = await moderator(
                        Prompts.to_dead_player.format(killed_player),
                    )
                    await alive_players_hub.broadcast(msg_moderator)
                    # Leave a message
                    role_obj = players.name_to_role_obj[killed_player]
                    last_msg = await role_obj.leave_last_words(msg_moderator)

                    speech = last_msg.metadata.get("speech", "")
                    behavior = last_msg.metadata.get("behavior", "")
                    if speech or behavior:
                        log_content = f"[{behavior}] {speech}" if behavior else speech
                        logger.log_last_words(killed_player, log_content)
                    elif last_msg.content:
                        logger.log_last_words(killed_player, last_msg.content)

                    await alive_players_hub.broadcast(last_msg)

            else:
                logger.log_announcement("天亮了，请所有玩家睁眼。昨晚平安夜，无人被淘汰。")
                await alive_players_hub.broadcast(
                    await moderator(Prompts.to_all_peace),
                )

            # Check winning
            res = players.check_winning()
            if res:
                logger.log_announcement(f"游戏结束: {res}")
                await moderator(res)
                logger.close()
                break

            # Discussion
            await alive_players_hub.broadcast(
                await moderator(
                    Prompts.to_all_discuss.format(
                        names=names_to_str(players.current_alive),
                    ),
                ),
            )
            # Open the auto broadcast to enable discussion
            alive_players_hub.set_auto_broadcast(True)
            # 更新存活智能体列表
            current_alive_agents = [
                role.agent for role in players.current_alive]

            # 使用 sequential_pipeline 进行讨论，并记录每个玩家的发言
            discussion_msgs = []
            for role in players.current_alive:
                msg = await role.day_discussion(await moderator(""))
                discussion_msgs.append(msg)

                speech = msg.metadata.get("speech", "")
                behavior = msg.metadata.get("behavior", "")
                if speech or behavior:
                    log_content = f"[{behavior}] {speech}" if behavior else speech
                    logger.log_message("白天讨论", log_content, role.name)
                elif msg.content:
                    logger.log_message("白天讨论", msg.content, role.name)

            # Disable auto broadcast to avoid leaking info
            alive_players_hub.set_auto_broadcast(False)

            # Voting
            vote_prompt = await moderator(
                Prompts.to_all_vote.format(
                    names_to_str(players.current_alive),
                ),
            )
            msgs_vote = []
            for role in players.current_alive:
                msg = await role.vote(vote_prompt, players.current_alive)
                msgs_vote.append(msg)
                # 记录投票
                target = msg.metadata.get("vote")
                if target:
                    logger.log_vote(role.name, target, "投票")

            voted_player, votes = majority_vote(
                [_.metadata.get("vote") for _ in msgs_vote],
            )
            # 记录投票结果
            if voted_player:
                logger.log_vote_result(voted_player, votes, "投票结果", "被投出")

            # Broadcast the voting messages together to avoid influencing
            # each other
            voting_msgs = [
                *msgs_vote,
                await moderator(
                    Prompts.to_all_res.format(votes, voted_player),
                ),
            ]

            # Leave a message if voted
            if voted_player:
                prompt_msg = await moderator(
                    Prompts.to_dead_player.format(voted_player),
                )
                role_obj = players.name_to_role_obj[voted_player]
                last_msg = await role_obj.leave_last_words(prompt_msg)

                speech = last_msg.metadata.get("speech", "")
                behavior = last_msg.metadata.get("behavior", "")
                if speech or behavior:
                    log_content = f"[{behavior}] {speech}" if behavior else speech
                    logger.log_last_words(voted_player, log_content)
                elif last_msg.content:
                    logger.log_last_words(voted_player, last_msg.content)

                voting_msgs.extend([prompt_msg, last_msg])

            await alive_players_hub.broadcast(voting_msgs)

            # If the voted player is the hunter, he can shoot someone
            shot_player = None
            for hunter in players.hunter:
                if voted_player == hunter.name:
                    shot_player = await hunter.shoot(players.current_alive, moderator)
                    if shot_player:
                        logger.log_action(
                            "猎人开枪", f"猎人 {hunter.name} 开枪击杀了 {shot_player}")
                        await alive_players_hub.broadcast(
                            await moderator(
                                Prompts.to_all_hunter_shoot.format(
                                    shot_player,
                                ),
                            ),
                        )

            # Update alive players
            dead_today = [voted_player, shot_player]
            # 记录白天死亡
            logger.log_death("白天死亡", [p for p in dead_today if p])
            players.update_players(dead_today)

            # Check winning
            res = players.check_winning()
            if res:
                logger.log_announcement(f"游戏结束: {res}")
                async with MsgHub(players.all_players) as all_players_hub:
                    res_msg = await moderator(res)
                    await all_players_hub.broadcast(res_msg)
                logger.close()
                break

        # The day ends
        first_day = False

    # Game over, each player reflects
    await fanout_pipeline(
        agents=agents,
        msg=await moderator[Any, Any, Msg](Prompts.to_all_reflect),
    )

    # 确保日志文件关闭
    logger.close()
