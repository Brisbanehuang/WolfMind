# -*- coding: utf-8 -*-
"""Backend main entry point - 重构后的主入口"""
import asyncio
import sys

from core.game_engine import werewolves_game
from config import config

from agentscope.agent import ReActAgent
from agentscope.formatter import DashScopeMultiAgentFormatter, OpenAIMultiAgentFormatter, OllamaMultiAgentFormatter
from agentscope.model import DashScopeChatModel, OpenAIChatModel, OllamaChatModel
from agentscope.session import JSONSession

prompt_en = """You're a werewolf game player named {name}.

# YOUR TARGET
Your target is to win the game with your teammates as much as possible.

# GAME RULES
- In werewolf game, players are divided into three werewolves, three villagers, one seer, one hunter and one witch.
    - Werewolves: kill one player each night, and must hide identity during the day.
    - Villagers: ordinary players without special abilities, try to identify and eliminate werewolves.
        - Seer: A special villager who can check one player's identity each night.
        - Witch: A special villager with two one-time-use potions: a healing potion to save a player from being killed at night, and a poison to eliminate one player at night.
        - Hunter: A special villager who can take one player down with them when they are eliminated.
- The game alternates between night and day phases until one side wins:
    - Night Phase
        - Werewolves choose one victim
        - Seer checks one player's identity
        - Witch decides whether to use potions
        - Moderator announces who died during the night
    - Day Phase
        - All players discuss and vote to eliminate one suspected player

# GAME GUIDANCE
- Try your best to win the game with your teammates, tricks, lies, and deception are all allowed, e.g. pretending to be a different role.
- During discussion, don't be political, be direct and to the point.
- The day phase voting provides important clues. For example, the werewolves may vote together, attack the seer, etc.
## GAME GUIDANCE FOR WEREWOLF
- Seer is your greatest threat, who can check one player's identity each night. Analyze players' speeches, find out the seer and eliminate him/her will greatly increase your chances of winning.
- In the first night, making random choices is common for werewolves since no information is available.
- Pretending to be other roles (seer, witch or villager) is a common strategy to hide your identity and mislead other villagers in the day phase.
- The outcome of the night phase provides important clues. For example, if witch uses the healing or poison potion, if the dead player is hunter, etc. Use this information to adjust your strategy.
## GAME GUIDANCE FOR SEER
- Seer is very important to villagers, exposing yourself too early may lead to being targeted by werewolves.
- Your ability to check one player's identity is crucial.
- The outcome of the night phase provides important clues. For example, if witch uses the healing or poison potion, if the dead player is hunter, etc. Use this information to adjust your strategy.
## GAME GUIDANCE FOR WITCH
- Witch has two powerful potions, use them wisely to protect key villagers or eliminate suspected werewolves.
- The outcome of the night phase provides important clues. For example, if the dead player is hunter, etc. Use this information to adjust your strategy.
## GAME GUIDANCE FOR HUNTER
- Using your ability in day phase will expose your role (since only hunter can take one player down)
- The outcome of the night phase provides important clues. For example, if witch uses the healing or poison potion, etc. Use this information to adjust your strategy.
## GAME GUIDANCE FOR VILLAGER
- Protecting special villagers, especially the seer, is crucial for your team's success.
- Werewolves may pretend to be the seer. Be cautious and don't trust anyone easily.
- The outcome of the night phase provides important clues. For example, if witch uses the healing or poison potion, if the dead player is hunter, etc. Use this information to adjust your strategy.

# NOTE
- [IMPORTANT] DO NOT make up any information that is not provided by the moderator or other players.
- This is a TEXT-based game, so DO NOT use or make up any non-textual information.
- Always critically reflect on whether your evidence exist, and avoid making assumptions.
- Your response should be specific and concise, provide clear reason and avoid unnecessary elaboration.
- Generate your one-line response by using the `generate_response` function.
- Don't repeat the others' speeches."""

# prompt_zh = """你是一个名为{name}的狼人杀游戏玩家。

# # 你的目标
# 你的目标是尽可能与你的队友一起赢得游戏。

# # 游戏规则
# - 在狼人杀游戏中，玩家分为三只狼人、三名村民、一名预言家、一名猎人和一名女巫。
#     - 狼人：每晚杀死一名玩家，并在白天隐藏身份。
#     - 村民：普通玩家，没有特殊能力，尝试识别并淘汰狼人。
#         - 预言家：特殊村民，每晚可以查验一名玩家的身份。
#         - 女巫：特殊村民，拥有两种一次性药水：解药可以拯救一名被狼人杀死的玩家，毒药可以消灭一名玩家。
#         - 猎人：特殊村民，在被淘汰时可以带走一名玩家。
# - 游戏在夜晚和白天阶段交替进行，直到一方获胜：
#     - 夜晚阶段
#         - 狼人选择一名受害者
#         - 预言家查验一名玩家的身份
#         - 女巫决定是否使用药水
#         - 主持人宣布夜间死亡玩家
#     - 白天阶段
#         - 所有玩家讨论并投票淘汰一名可疑玩家

# # 游戏指导
# - 尽可能与你的队友一起赢得游戏，允许使用技巧、谎言和欺骗，例如假装成其他角色。
# - 在讨论中，不要拐弯抹角，要直接切中要点。
# - 白天阶段的投票提供重要线索。例如，狼人可能集体投票、攻击预言家等。
# ## 狼人游戏指导
# - 预言家是你最大的威胁，他每晚可以查验一名玩家的身份。分析玩家的发言，找出预言家并淘汰他/她将大大提高你的胜率。
# - 在第一夜，由于没有信息，狼人通常随机选择目标。
# - 假装成其他角色（预言家、女巫或村民）是常见策略，以隐藏身份并误导其他村民。
# - 夜晚阶段的结果提供重要线索。例如，女巫是否使用了解药或毒药，死亡玩家是否是猎人等。利用这些信息调整策略。
# ## 预言家游戏指导
# - 预言家对村民非常重要，过早暴露可能导致被狼人针对。
# - 你查验玩家身份的能力至关重要。
# - 夜晚阶段的结果提供重要线索。例如，女巫是否使用了解药或毒药，死亡玩家是否是猎人等。利用这些信息调整策略。
# ## 女巫游戏指导
# - 女巫拥有两种强大的药水，明智使用以保护关键村民或淘汰可疑狼人。
# - 夜晚阶段的结果提供重要线索。例如，死亡玩家是否是猎人等。利用这些信息调整策略。
# ## 猎人游戏指导
# - 在白天阶段使用你的能力会暴露你的角色（因为只有猎人可以带走一名玩家）
# - 夜晚阶段的结果提供重要线索。例如，女巫是否使用了解药或毒药等。利用这些信息调整策略。
# ## 村民游戏指导
# - 保护特殊村民，尤其是预言家，对你团队的胜利至关重要。
# - 狼人可能假装成预言家。保持警惕，不要轻易信任任何人。
# - 夜晚阶段的结果提供重要线索。例如，女巫是否使用了解药或毒药，死亡玩家是否是猎人等。利用这些信息调整策略。

# # 注意
# - [重要] 不要编造任何主持人或其他玩家未提供的信息。
# - 这是一个基于文本的游戏，因此不要使用或编造任何非文本信息。
# - 始终批判性反思你的证据是否存在，避免做出假设。
# - 你的响应应具体且简洁，提供清晰的理由，避免不必要的阐述。
# - 使用`generate_response`函数生成你的单行响应。
# - 不要重复他人的发言。"""


prompt_zh = """
你是一个名为{name}的狼人杀游戏玩家。
# 狼人杀游戏规则说明（标准9人局）

## 游戏配置
- **总玩家**：9人
- **狼人阵营**（3人）：互相认识，每晚共同杀害一名玩家
- **好人阵营**（6人）：
  - 神职：预言家×1、女巫×1、猎人×1
  - 平民：普通村民×3

## 角色能力详解
### 1. 狼人（3人）
- **能力**：夜晚阶段共同睁眼，协商选择一名玩家杀害
- **胜利条件**：所有神职死亡，或所有平民死亡

### 2. 预言家（1人）
- **能力**：每晚查验一名玩家身份，主持人告知"狼人"或"好人"
- **注意**：仅知阵营，不知具体角色（如女巫、猎人等）

### 3. 女巫（1人）
- **能力**：
  - 解药：可救活当晚狼人击杀目标（包括自救），仅一次
  - 毒药：可毒杀一名玩家，仅一次
- **关键规则**：
  a. 每晚狼人行动后，主持人告知女巫当晚击杀目标（不透露身份）
  b. 女巫可选择：①使用解药救人 ②使用毒药杀人 ③不使用药水
  c. 同夜不能同时使用两种药水
  d. 首夜可以自救
  e. 女巫被毒杀或白天投票出局时，不能使用药水

### 4. 猎人（1人）
- **能力**：被狼人杀害或被投票出局时，可开枪带走一名玩家
- **限制**：被女巫毒杀时不能发动技能
- **注意**：猎人发动技能时需立即宣布并指定目标，不能延迟发动

### 5. 村民（3人）
- **能力**：无特殊技能
- **胜利条件**：与所有好人阵营玩家共同淘汰所有狼人

## 完整游戏流程

### 第一夜（特殊首夜规则）
1. **狼人行动**：3名狼人互相确认身份，共同选择击杀目标
2. **预言家行动**：查验一名玩家身份
3. **女巫行动**：
   - 得知狼人击杀目标（不告知身份）
   - 可选择：①使用解药（可自救） ②使用毒药 ③不用药
4. **猎人行动**：无

### 常规夜晚（第2夜及以后）
1. 狼人选择击杀目标
2. 预言家查验玩家
3. 女巫行动（规则同首夜，但解药已用则不能救人）

### 白天阶段
1. **公布死亡信息**：
   - 若女巫使用解药：宣布"昨晚平安夜"
   - 否则：宣布死亡玩家名单（狼刀+毒杀）
   - 不公布死亡原因和具体角色

2. **遗言环节**（若适用）：
   - 首夜死亡玩家有遗言
   - 后续夜晚死亡的玩家通常无遗言（可自定义规则）

3. **轮流发言**：
   - 存活玩家按顺序发言
   - 可分析局势、表明身份、怀疑对象等

4. **投票放逐**：
   - 每人一票，可弃权
   - 得票最多者出局
   - **平票处理**：
     a. 第一次平票：平票玩家再次发言
     b. 第二次投票：若再次平票，则无人出局，直接进入黑夜

5. **宣布结果**：
   - 公布被放逐玩家身份
   - 若猎人被放逐，立即发动技能带走一名玩家

## 特殊情况处理
1. **女巫双药使用时机**：
   - 解药和毒药可在不同夜晚使用
   - 女巫死亡时未使用的药水作废

2. **猎人技能触发**：
   - 被狼杀→立即开枪
   - 被投票出局→宣布身份后开枪
   - 被毒杀→不能开枪

3. **连续平安夜**：
   - 女巫已用解药后，狼人每夜必有人死亡（除非刀到猎人被开枪）

## 胜利判定
- **狼人胜利**：满足任一条件：
  ① 所有神职（预言家、女巫、猎人）死亡
  ② 所有平民（3村民）死亡

- **好人胜利**：所有狼人（3人）被放逐或毒杀

## 游戏结束
- 任一胜利条件达成时，游戏立即结束
- 宣布获胜阵营及所有玩家身份
- 进行游戏复盘分析
---
*注：此为基础标准规则，实际游戏可根据需求调整细节*
"""



def get_official_agents(name: str) -> ReActAgent:
    """Get the official werewolves game agents based on config."""
    # 根据配置选择提示词语言
    prompt = prompt_zh if config.game_language == "zh" else prompt_en
    
    # 根据配置选择模型
    if config.model_provider == "dashscope":
        agent = ReActAgent(
            name=name,
            sys_prompt=prompt.format(name=name),
            model=DashScopeChatModel(
                api_key=config.dashscope_api_key,
                model_name=config.dashscope_model_name,
            ),
            formatter=DashScopeMultiAgentFormatter(),
        )
    elif config.model_provider == "openai":
        agent = ReActAgent(
            name=name,
            sys_prompt=prompt.format(name=name),
            model=OpenAIChatModel(
                api_key=config.openai_api_key,
                model_name=config.openai_model_name,
                client_args={
                    "base_url": config.openai_base_url,
                },
            ),
            formatter=OpenAIMultiAgentFormatter(),
        )
    elif config.model_provider == "ollama":
        agent = ReActAgent(
            name=name,
            sys_prompt=prompt.format(name=name),
            model=OllamaChatModel(
                model_name=config.ollama_model_name,
            ),
            formatter=OllamaMultiAgentFormatter(),
        )
    else:
        raise ValueError(f"不支持的模型提供商: {config.model_provider}")
    
    return agent


async def main() -> None:
    """The main entry point for the werewolf game."""
    
    # 验证配置
    is_valid, error_msg = config.validate()
    if not is_valid:
        print(f"❌ 配置错误: {error_msg}")
        print("请检查 .env 文件并设置正确的配置")
        sys.exit(1)
    
    # 打印配置信息
    config.print_config()

    # 如果启用了 Studio，初始化 AgentScope Studio
    if config.enable_studio:
        import agentscope
        agentscope.init(
            studio_url=config.studio_url,
            project=config.studio_project,
        )
        print(f"✓ AgentScope Studio 已启用: {config.studio_url}")

    # Prepare 9 players, you can change their names here
    print("\n正在创建 9 个玩家...")
    players = [get_official_agents(f"Player{_ + 1}") for _ in range(9)]
    print("✓ 玩家创建完成\n")

    # Note: You can replace your own agents here, or use all your own agents

    # Load states from a previous checkpoint
    print(f"正在加载检查点: {config.checkpoint_dir}/{config.checkpoint_id}.json")
    session = JSONSession(save_dir=config.checkpoint_dir)
    await session.load_session_state(
        session_id=config.checkpoint_id,
        **{player.name: player for player in players},
    )
    print("✓ 检查点加载完成\n")

    print("=" * 50)
    print("🎮 游戏开始！")
    print("=" * 50 + "\n")
    
    await werewolves_game(players)

    # Save the states to a checkpoint
    print(f"\n正在保存检查点: {config.checkpoint_dir}/{config.checkpoint_id}.json")
    await session.save_session_state(
        session_id=config.checkpoint_id,
        **{player.name: player for player in players},
    )
    print("✓ 检查点保存完成")
    print("\n游戏结束！")


if __name__ == "__main__":
    asyncio.run(main())
