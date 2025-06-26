"""
提示词管理模块

集中管理各种AI模型的提示词模板
"""

from .llm_prompts import LLMPrompts
from .disposal_recommendation_prompts import DisposalRecommendationPrompts
from .creative_renovation_prompts import CreativeRenovationPrompts

__all__ = ["LLMPrompts", "DisposalRecommendationPrompts", "CreativeRenovationPrompts"] 