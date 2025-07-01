"""
提示词管理模块

集中管理各种AI模型的提示词模板
"""

from .llm_prompts import LLMPrompts
from .disposal_recommendation_prompts import DisposalRecommendationPrompts
from .creative_renovation_prompts import CreativeRenovationPrompts
from .recycling_location_prompts import RecyclingLocationPrompts

# 二手平台搜索提示词
from .secondhand_search_prompts import SecondhandSearchPrompts

__all__ = [
    "BilibiliSearchPrompts",
    "CreativeRenovationPrompts", 
    "DisposalRecommendationPrompts",
    "LLMPrompts",
    "RecyclingLocationPrompts",
    "SecondhandSearchPrompts"
] 