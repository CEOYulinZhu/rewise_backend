"""
总处理协调器数据模型

定义总Agent的请求、响应和处理步骤数据结构，
整合四大Agent的响应，去除重复字段
"""

from typing import Dict, Any, Optional, List
from enum import Enum
from pydantic import BaseModel, Field

# 导入四大Agent的响应模型
from app.models.disposal_recommendation_models import DisposalRecommendationResponse
from app.models.creative_coordinator_models import CoordinatorResponse
from app.models.recycling_coordinator_models import RecyclingCoordinatorResponse
from app.models.secondhand_coordinator_models import SecondhandTradingResponse


class ProcessingStepStatus(str, Enum):
    """处理步骤状态"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


class ProcessingStep(BaseModel):
    """处理步骤"""
    step_name: str = Field(..., description="步骤名称")
    step_title: str = Field(..., description="步骤标题")
    description: str = Field(..., description="步骤描述")
    status: ProcessingStepStatus = Field(..., description="步骤状态")
    result: Optional[Dict[str, Any]] = Field(None, description="步骤结果")
    error: Optional[str] = Field(None, description="错误信息")
    metadata: Optional[Dict[str, Any]] = Field(None, description="步骤元数据")
    timestamp: Optional[float] = Field(None, description="时间戳")


class ProcessingMasterRequest(BaseModel):
    """总处理协调器请求"""
    image_url: Optional[str] = Field(None, description="图片URL或本地路径")
    text_description: Optional[str] = Field(None, description="文字描述")
    user_location: Optional[Dict[str, float]] = Field(None, description="用户位置 {lat: 纬度, lon: 经度}")
    
    # 处理选项
    enable_parallel: bool = Field(default=True, description="是否启用并行处理")
    max_results_per_platform: int = Field(default=10, description="每个平台最大返回结果数")
    
    class Config:
        schema_extra = {
            "example": {
                "image_url": "data/uploads/item_photo.jpg",
                "text_description": "一台使用两年的iPhone 12，黑色，功能正常",
                "user_location": {"lat": 39.906823, "lon": 116.447303},
                "enable_parallel": True,
                "max_results_per_platform": 10
            }
        }


class ProcessingAnalysisMetadata(BaseModel):
    """分析元数据"""
    source: str = Field(..., description="分析来源: text_only|image_only|merged")
    has_conflicts: bool = Field(default=False, description="是否有冲突")
    conflicts_summary: Optional[str] = Field(None, description="冲突摘要")


class ProcessingAgentSummary(BaseModel):
    """Agent执行摘要"""
    disposal_recommendation: bool = Field(..., description="处置推荐Agent是否执行成功")
    creative_coordination: bool = Field(..., description="创意改造Agent是否执行成功")
    recycling_coordination: bool = Field(..., description="回收协调Agent是否执行成功")
    secondhand_coordination: bool = Field(..., description="二手交易Agent是否执行成功")
    total_successful: int = Field(..., description="成功执行的Agent数量")


class ProcessingMetadata(BaseModel):
    """处理元数据"""
    processing_time_seconds: float = Field(..., description="总处理时间（秒）")
    agents_executed: ProcessingAgentSummary = Field(..., description="Agent执行情况")
    analysis_metadata: Optional[ProcessingAnalysisMetadata] = Field(None, description="分析元数据")


class DisposalSolution(BaseModel):
    """处置方案（去除重复的analysis_result）"""
    success: bool = Field(..., description="是否成功")
    recommendations: Optional[Dict[str, Any]] = Field(None, description="推荐结果")
    recommendation_source: Optional[str] = Field(None, description="推荐来源")
    error: Optional[str] = Field(None, description="错误信息")


class CreativeSolution(BaseModel):
    """创意改造方案（去除重复的analysis_result）"""
    success: bool = Field(..., description="是否成功")
    renovation_plan: Optional[Dict[str, Any]] = Field(None, description="改造计划")
    videos: Optional[List[Dict[str, Any]]] = Field(None, description="相关视频")
    keywords: Optional[List[str]] = Field(None, description="搜索关键字")
    search_intent: Optional[str] = Field(None, description="搜索意图")
    error: Optional[str] = Field(None, description="错误信息")


class RecyclingSolution(BaseModel):
    """回收方案（去除重复的analysis_result）"""
    success: bool = Field(..., description="是否成功")
    processing_summary: Optional[Dict[str, Any]] = Field(None, description="处理摘要")
    location_recommendation: Optional[Dict[str, Any]] = Field(None, description="地点推荐")
    platform_recommendation: Optional[Dict[str, Any]] = Field(None, description="平台推荐")
    error: Optional[str] = Field(None, description="错误信息")


class SecondhandSolution(BaseModel):
    """二手交易方案（去除重复的analysis_result）"""
    success: bool = Field(..., description="是否成功")
    search_result: Optional[Dict[str, Any]] = Field(None, description="搜索结果")
    content_result: Optional[Dict[str, Any]] = Field(None, description="内容生成结果")
    processing_metadata: Optional[Dict[str, Any]] = Field(None, description="处理元数据")
    error: Optional[str] = Field(None, description="错误信息")


class ProcessingMasterResponse(BaseModel):
    """总处理协调器响应（统一格式，去除重复字段）"""
    success: bool = Field(..., description="处理是否成功")
    source: str = Field(default="processing_master", description="数据来源")
    
    # 核心分析结果（全局唯一，不重复）
    analysis_result: Dict[str, Any] = Field(..., description="物品分析结果")
    
    # 四大解决方案（已去除重复的analysis_result）
    disposal_solution: Optional[DisposalSolution] = Field(None, description="处置推荐方案")
    creative_solution: Optional[CreativeSolution] = Field(None, description="创意改造方案")
    recycling_solution: Optional[RecyclingSolution] = Field(None, description="回收方案")
    secondhand_solution: Optional[SecondhandSolution] = Field(None, description="二手交易方案")
    
    # 处理元数据和摘要
    processing_metadata: ProcessingMetadata = Field(..., description="处理元数据")
    
    # 错误信息
    error: Optional[str] = Field(None, description="全局错误信息")
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        return self.dict(exclude_none=True)
    
    def get_successful_solutions(self) -> List[str]:
        """获取成功的解决方案列表"""
        successful = []
        if self.disposal_solution and self.disposal_solution.success:
            successful.append("disposal_recommendation")
        if self.creative_solution and self.creative_solution.success:
            successful.append("creative_coordination")
        if self.recycling_solution and self.recycling_solution.success:
            successful.append("recycling_coordination")
        if self.secondhand_solution and self.secondhand_solution.success:
            successful.append("secondhand_coordination")
        return successful
    
    def get_primary_recommendation(self) -> Optional[str]:
        """获取主要推荐方案"""
        if self.disposal_solution and self.disposal_solution.recommendations:
            overall_rec = self.disposal_solution.recommendations.get("overall_recommendation", {})
            return overall_rec.get("primary_choice")
        return None


class ProcessingMasterDataConverter:
    """总处理协调器数据转换器"""
    
    @staticmethod
    def create_response(
        success: bool,
        analysis_result: Dict[str, Any],
        disposal_recommendation: Optional[DisposalRecommendationResponse] = None,
        creative_coordination: Optional[CoordinatorResponse] = None,
        recycling_coordination: Optional[RecyclingCoordinatorResponse] = None,
        secondhand_coordination: Optional[SecondhandTradingResponse] = None,
        processing_time_seconds: float = 0.0,
        error: Optional[str] = None
    ) -> ProcessingMasterResponse:
        """创建统一的总处理协调器响应对象（去除重复字段）"""
        
        # 提取分析元数据（不修改原始数据）
        analysis_metadata = None
        if analysis_result and "_merge_metadata" in analysis_result:
            merge_meta = analysis_result.get("_merge_metadata", {})
            analysis_metadata = ProcessingAnalysisMetadata(
                source=merge_meta.get("source", "unknown"),
                has_conflicts=merge_meta.get("has_conflicts", False),
                conflicts_summary=merge_meta.get("conflicts_summary")
            )
            # 创建副本并移除元数据
            analysis_result = analysis_result.copy()
            analysis_result.pop("_merge_metadata", None)
        
        # 转换处置推荐（去除重复的analysis_result）
        disposal_solution = None
        if disposal_recommendation:
            disposal_data = disposal_recommendation.to_dict()
            disposal_data.pop("analysis_result", None)  # 移除重复字段
            disposal_solution = DisposalSolution(
                success=disposal_data.get("success", False),
                recommendations=disposal_data.get("recommendations"),
                recommendation_source=disposal_data.get("recommendation_source"),
                error=disposal_data.get("error")
            )
        
        # 转换创意改造（去除重复的analysis_result）
        creative_solution = None
        if creative_coordination:
            creative_data = creative_coordination.to_dict()
            creative_data.pop("analysis_result", None)  # 移除重复字段
            creative_solution = CreativeSolution(
                success=creative_data.get("success", False),
                renovation_plan=creative_data.get("renovation_plan"),
                videos=creative_data.get("videos"),
                keywords=creative_data.get("keywords"),  # 搜索关键字
                search_intent=creative_data.get("search_intent"),  # 搜索意图
                error=creative_data.get("error")
            )
        
        # 转换回收方案（去除重复的analysis_result）
        recycling_solution = None
        if recycling_coordination:
            recycling_data = recycling_coordination.to_dict()
            # 移除嵌套的analysis_result
            if "location_recommendation" in recycling_data:
                recycling_data["location_recommendation"].pop("analysis_result", None)
            recycling_solution = RecyclingSolution(
                success=recycling_data.get("success", False),
                processing_summary=recycling_data.get("processing_summary"),
                location_recommendation=recycling_data.get("location_recommendation"),
                platform_recommendation=recycling_data.get("platform_recommendation"),
                error=recycling_data.get("error")
            )
        
        # 转换二手交易（去除重复的analysis_result）
        secondhand_solution = None
        if secondhand_coordination:
            secondhand_data = secondhand_coordination.to_dict()
            # 移除嵌套的analysis_result
            if "search_result" in secondhand_data:
                secondhand_data["search_result"].pop("analysis_result", None)
            if "content_result" in secondhand_data:
                secondhand_data["content_result"].pop("analysis_result", None)
            secondhand_solution = SecondhandSolution(
                success=secondhand_data.get("success", False),
                search_result=secondhand_data.get("search_result"),
                content_result=secondhand_data.get("content_result"),
                processing_metadata=secondhand_data.get("processing_metadata"),
                error=secondhand_data.get("error")
            )
        
        # 创建Agent执行摘要
        agents_executed = ProcessingAgentSummary(
            disposal_recommendation=disposal_solution is not None and disposal_solution.success,
            creative_coordination=creative_solution is not None and creative_solution.success,
            recycling_coordination=recycling_solution is not None and recycling_solution.success,
            secondhand_coordination=secondhand_solution is not None and secondhand_solution.success,
            total_successful=sum([
                1 for solution in [disposal_solution, creative_solution, recycling_solution, secondhand_solution]
                if solution is not None and solution.success
            ])
        )
        
        # 创建处理元数据
        processing_metadata = ProcessingMetadata(
            processing_time_seconds=processing_time_seconds,
            agents_executed=agents_executed,
            analysis_metadata=analysis_metadata
        )
        
        # 创建响应对象
        return ProcessingMasterResponse(
            success=success,
            analysis_result=analysis_result,
            disposal_solution=disposal_solution,
            creative_solution=creative_solution,
            recycling_solution=recycling_solution,
            secondhand_solution=secondhand_solution,
            processing_metadata=processing_metadata,
            error=error
        )
    
    @staticmethod
    def create_request(
        image_url: Optional[str] = None,
        text_description: Optional[str] = None,
        user_location: Optional[Dict[str, float]] = None,
        enable_parallel: bool = True,
        max_results_per_platform: int = 10
    ) -> ProcessingMasterRequest:
        """创建总处理协调器请求对象"""
        return ProcessingMasterRequest(
            image_url=image_url,
            text_description=text_description,
            user_location=user_location,
            enable_parallel=enable_parallel,
            max_results_per_platform=max_results_per_platform
        ) 