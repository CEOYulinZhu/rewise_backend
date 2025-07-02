"""
平台推荐Agent数据模型

定义平台推荐Agent的输入输出数据结构
"""

from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field, validator


class PlatformRecommendationItem(BaseModel):
    """单个平台推荐项"""
    
    platform_name: str = Field(..., description="平台名称")
    suitability_score: float = Field(..., ge=0, le=10, description="适合度评分(0-10)")
    pros: List[str] = Field(..., min_items=1, max_items=3, description="优势列表(1-3个)")
    cons: List[str] = Field(..., min_items=1, max_items=2, description="劣势列表(1-2个)")
    recommendation_reason: str = Field(..., description="推荐理由说明")
    
    @validator('pros')
    def validate_pros(cls, v):
        for item in v:
            if len(item) > 20:
                raise ValueError("优势描述不能超过20个字符")
        return v
    
    @validator('cons')
    def validate_cons(cls, v):
        for item in v:
            if len(item) > 20:
                raise ValueError("劣势描述不能超过20个字符")
        return v


class PlatformRecommendationResult(BaseModel):
    """AI推荐结果"""
    
    recommendations: List[PlatformRecommendationItem] = Field(..., min_items=1, max_items=3)
    
    def get_platform_names(self) -> List[str]:
        """获取推荐的平台名称列表"""
        return [rec.platform_name for rec in self.recommendations]


class PlatformRecommendationResponse(BaseModel):
    """平台推荐Agent响应"""
    
    success: bool = Field(..., description="推荐是否成功")
    source: str = Field(default="platform_recommendation_agent", description="数据来源")
    analysis_result: Optional[Dict[str, Any]] = Field(None, description="输入的分析结果")
    
    # AI推荐结果
    ai_recommendations: Optional[PlatformRecommendationResult] = Field(None, description="AI推荐结果")
    
    # 完整平台数据
    platform_details: Optional[List[Dict[str, Any]]] = Field(None, description="推荐平台的完整数据")
    
    # 检索元数据
    rag_metadata: Optional[Dict[str, Any]] = Field(None, description="RAG检索元数据")
    
    # AI原始响应
    ai_raw_response: Optional[str] = Field(None, description="AI模型的原始响应内容")
    
    # 错误信息
    error: Optional[str] = Field(None, description="错误信息")
    
    def get_top_recommendation(self) -> Optional[PlatformRecommendationItem]:
        """获取最高评分的推荐"""
        if not self.ai_recommendations or not self.ai_recommendations.recommendations:
            return None
        return max(self.ai_recommendations.recommendations, key=lambda x: x.suitability_score)


class PlatformRecommendationDataConverter:
    """数据转换工具类"""
    
    @staticmethod
    def create_response(
        success: bool,
        analysis_result: Optional[Dict[str, Any]] = None,
        ai_recommendations: Optional[Dict[str, Any]] = None,
        platform_details: Optional[List[Dict[str, Any]]] = None,
        rag_metadata: Optional[Dict[str, Any]] = None,
        ai_raw_response: Optional[str] = None,
        error: Optional[str] = None
    ) -> PlatformRecommendationResponse:
        """创建标准化响应"""
        
        ai_rec_obj = None
        if ai_recommendations:
            try:
                ai_rec_obj = PlatformRecommendationResult(**ai_recommendations)
            except Exception as e:
                error = f"AI推荐结果格式错误: {e}"
                success = False
        
        return PlatformRecommendationResponse(
            success=success,
            analysis_result=analysis_result,
            ai_recommendations=ai_rec_obj,
            platform_details=platform_details,
            rag_metadata=rag_metadata,
            ai_raw_response=ai_raw_response,
            error=error
        ) 