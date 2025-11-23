# -*- coding: utf-8 -*-
"""测试导入是否正常"""

print("测试导入模块...")

try:
    from config import config
    print("✓ config 导入成功")
except Exception as e:
    print(f"✗ config 导入失败: {e}")

try:
    from models.roles import RoleFactory, Werewolf, Villager, Seer, Witch, Hunter
    print("✓ roles 导入成功")
except Exception as e:
    print(f"✗ roles 导入失败: {e}")

try:
    from core.utils import Players, EchoAgent, majority_vote, names_to_str
    print("✓ utils 导入成功")
except Exception as e:
    print(f"✗ utils 导入失败: {e}")

try:
    from models.schemas import DiscussionModel, get_vote_model
    print("✓ schemas 导入成功")
except Exception as e:
    print(f"✗ schemas 导入失败: {e}")

try:
    from prompts import EnglishPrompts, ChinesePrompts
    print("✓ prompts 导入成功")
except Exception as e:
    print(f"✗ prompts 导入失败: {e}")

try:
    from core.game_engine import werewolves_game
    print("✓ game_engine 导入成功")
except Exception as e:
    print(f"✗ game_engine 导入失败: {e}")

print("\n所有模块导入测试完成！")
