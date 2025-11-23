# -*- coding: utf-8 -*-
"""Models module - 数据模型和角色定义"""
from models.roles import (
    BaseRole,
    Werewolf,
    Villager,
    Seer,
    Witch,
    Hunter,
    RoleFactory,
)
from models.schemas import (
    DiscussionModel,
    WitchResurrectModel,
    get_vote_model,
    get_poison_model,
    get_seer_model,
    get_hunter_model,
)

__all__ = [
    # Roles
    "BaseRole",
    "Werewolf",
    "Villager",
    "Seer",
    "Witch",
    "Hunter",
    "RoleFactory",
    # Schemas
    "DiscussionModel",
    "WitchResurrectModel",
    "get_vote_model",
    "get_poison_model",
    "get_seer_model",
    "get_hunter_model",
]
