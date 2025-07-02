"""
RAG服务模块

基于ChromaDB的检索增强生成服务
"""

from .platform_recommendation_service import PlatformRecommendationRAGService

__all__ = [
    "PlatformRecommendationRAGService"
]