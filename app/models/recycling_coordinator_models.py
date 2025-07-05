"""
回收捐赠总协调器数据模型

定义回收捐赠总协调器Agent返回的结构化数据模型，
整合回收地点推荐和平台推荐的结果
"""

from dataclasses import dataclass
from typing import Optional, Dict, Any

from app.models.platform_recommendation_agent_models import PlatformRecommendationResponse
from app.models.recycling_location_models import RecyclingLocationResponse


@dataclass
class RecyclingCoordinatorResponse:
    """回收捐赠总协调器完整响应数据模型"""
    success: bool                                                        # 操作是否成功
    source: str = "recycling_coordinator"                               # 数据来源标识
    analysis_result: Optional[Dict[str, Any]] = None                    # 输入的分析结果
    
    # 地点推荐结果
    location_recommendation: Optional[RecyclingLocationResponse] = None  # 回收地点推荐结果
    
    # 平台推荐结果  
    platform_recommendation: Optional[PlatformRecommendationResponse] = None  # 平台推荐结果
    
    # 协调器元数据
    processing_metadata: Optional[Dict[str, Any]] = None                # 处理元数据
    
    # 错误信息
    error: Optional[str] = None                                         # 错误信息（失败时）
    
    def __post_init__(self):
        """数据验证"""
        if self.success:
            if not self.location_recommendation and not self.platform_recommendation:
                raise ValueError("成功响应必须至少包含地点推荐或平台推荐结果")
    
    def has_location_recommendations(self) -> bool:
        """检查是否有有效的地点推荐"""
        return (self.location_recommendation is not None and 
                self.location_recommendation.success and 
                len(self.location_recommendation.locations) > 0)
    
    def has_platform_recommendations(self) -> bool:
        """检查是否有有效的平台推荐"""
        return (self.platform_recommendation is not None and 
                self.platform_recommendation.success and 
                self.platform_recommendation.ai_recommendations is not None)
    
    def get_recycling_type(self) -> Optional[str]:
        """获取分析得出的回收类型"""
        if self.location_recommendation:
            return self.location_recommendation.recycling_type
        return None
    
    def get_top_platform_recommendation(self):
        """获取最高评分的平台推荐"""
        if self.platform_recommendation:
            return self.platform_recommendation.get_top_recommendation()
        return None
    
    def get_nearby_locations(self, max_distance_meters: int = 10000):
        """获取指定距离内的回收地点"""
        if self.location_recommendation:
            return self.location_recommendation.get_nearby_locations(max_distance_meters)
        return []
    
    def get_processing_summary(self) -> Dict[str, Any]:
        """获取处理摘要信息"""
        summary = {
            "success": self.success,
            "has_locations": self.has_location_recommendations(),
            "has_platforms": self.has_platform_recommendations(),
            "recycling_type": self.get_recycling_type(),
        }
        
        if self.has_location_recommendations():
            summary["location_count"] = len(self.location_recommendation.locations)
            summary["nearby_location_count"] = len(self.get_nearby_locations())
        
        if self.has_platform_recommendations():
            summary["platform_count"] = len(self.platform_recommendation.ai_recommendations.recommendations)
            top_platform = self.get_top_platform_recommendation()
            if top_platform:
                summary["top_platform"] = {
                    "name": top_platform.platform_name,
                    "score": top_platform.suitability_score
                }
        
        if self.processing_metadata:
            summary.update(self.processing_metadata)
        
        return summary
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式（用于JSON序列化）"""
        result = {
            "success": self.success,
            "source": self.source,
            "processing_summary": self.get_processing_summary(),
            "error": self.error
        }
        
        if self.analysis_result:
            result["analysis_result"] = self.analysis_result
        
        if self.location_recommendation:
            result["location_recommendation"] = self.location_recommendation.to_dict()
        
        if self.platform_recommendation:
            result["platform_recommendation"] = {
                "success": self.platform_recommendation.success,
                "ai_recommendations": (
                    self.platform_recommendation.ai_recommendations.dict() 
                    if self.platform_recommendation.ai_recommendations else None
                ),
                "platform_details": self.platform_recommendation.platform_details,
                "rag_metadata": self.platform_recommendation.rag_metadata,
                "error": self.platform_recommendation.error
            }
        
        if self.processing_metadata:
            result["processing_metadata"] = self.processing_metadata
        
        return result


class RecyclingCoordinatorDataConverter:
    """回收捐赠总协调器数据转换器"""
    
    @staticmethod
    def create_response(
        success: bool,
        analysis_result: Optional[Dict[str, Any]] = None,
        location_recommendation: Optional[RecyclingLocationResponse] = None,
        platform_recommendation: Optional[PlatformRecommendationResponse] = None,
        processing_metadata: Optional[Dict[str, Any]] = None,
        error: Optional[str] = None
    ) -> RecyclingCoordinatorResponse:
        """创建回收捐赠总协调器响应对象
        
        Args:
            success: 操作是否成功
            analysis_result: 输入的分析结果
            location_recommendation: 回收地点推荐结果
            platform_recommendation: 平台推荐结果  
            processing_metadata: 处理元数据
            error: 错误信息
            
        Returns:
            RecyclingCoordinatorResponse对象
        """
        return RecyclingCoordinatorResponse(
            success=success,
            analysis_result=analysis_result,
            location_recommendation=location_recommendation,
            platform_recommendation=platform_recommendation,
            processing_metadata=processing_metadata,
            error=error
        )
    
    @staticmethod
    def create_processing_metadata(
        enable_parallel: bool,
        location_success: bool,
        platform_success: bool,
        location_error: Optional[str] = None,
        platform_error: Optional[str] = None,
        processing_time_seconds: Optional[float] = None
    ) -> Dict[str, Any]:
        """创建处理元数据
        
        Args:
            enable_parallel: 是否启用并行处理
            location_success: 地点推荐是否成功
            platform_success: 平台推荐是否成功
            location_error: 地点推荐错误信息
            platform_error: 平台推荐错误信息
            processing_time_seconds: 处理总耗时（秒）
            
        Returns:
            处理元数据字典
        """
        metadata = {
            "processing_mode": "parallel" if enable_parallel else "sequential",
            "location_recommendation": {
                "success": location_success,
                "error": location_error
            },
            "platform_recommendation": {
                "success": platform_success, 
                "error": platform_error
            }
        }
        
        if processing_time_seconds is not None:
            metadata["processing_time_seconds"] = round(processing_time_seconds, 2)
        
        return metadata 