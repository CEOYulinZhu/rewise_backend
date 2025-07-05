"""
数据模型模块

包含所有SQLAlchemy数据模型和Pydantic模式
"""

from .creative_coordinator_models import (
    RenovationStep,
    RenovationSummary, 
    RenovationPlan,
    VideoInfo,
    CoordinatorResponse,
    CoordinatorDataConverter
)

from .disposal_recommendation_models import (
    DisposalPathRecommendation,
    OverallRecommendation,
    DisposalRecommendations,
    DisposalRecommendationResponse,
    DisposalRecommendationDataConverter
)

from .amap_models import (
    AmapPhoto,
    AmapPOI,
    AmapSearchResponse,
    AmapSearchRequest
)

from .recycling_location_models import (
    RecyclingLocationResponse,
    RecyclingLocationDataConverter
)

from .recycling_coordinator_models import (
    RecyclingCoordinatorResponse,
    RecyclingCoordinatorDataConverter
)

from .aihuishou_models import (
    AihuishouProduct,
    AihuishouPriceStats,
    AihuishouSearchRequest,
    AihuishouSearchResponse,
    AihuishouSearchDataConverter
)

from .xianyu_models import (
    XianyuProduct,
    XianyuPriceStats,
    XianyuSearchRequest,
    XianyuSearchResponse,
    XianyuSearchDataConverter
)

from .task import (
    ProcessingTask,
    RecyclingChannel,
    OnlineRecyclingPlatform,
    TaskCreate,
    TaskResponse,
    TaskStatus,
    ProcessingResult
)

from .secondhand_search_models import (
    SecondhandPlatformProduct,
    XianyuSimplifiedProduct,
    AihuishouSimplifiedProduct,
    PlatformPriceStats,
    SecondhandSearchKeywords,
    SecondhandSearchRequest,
    SecondhandSearchResult,
    SecondhandSearchDataConverter
)

from .content_generation_models import (
    ContentGenerationResult,
    ContentGenerationResponse,
    ContentGenerationDataConverter
)

from .processing_master_models import (
    ProcessingStep,
    ProcessingStepStatus,
    ProcessingMasterRequest,
    ProcessingMasterResponse,
    ProcessingAnalysisMetadata,
    ProcessingAgentSummary,
    ProcessingMetadata,
    DisposalSolution,
    CreativeSolution,
    RecyclingSolution,
    SecondhandSolution,
    ProcessingMasterDataConverter
)

__all__ = [
    # 创意改造协调器模型
    "RenovationStep",
    "RenovationSummary", 
    "RenovationPlan",
    "VideoInfo",
    "CoordinatorResponse",
    "CoordinatorDataConverter",
    
    # 处置推荐模型
    "DisposalPathRecommendation",
    "OverallRecommendation", 
    "DisposalRecommendations",
    "DisposalRecommendationResponse",
    "DisposalRecommendationDataConverter",
    
    # 高德地图模型
    "AmapPhoto",
    "AmapPOI",
    "AmapSearchResponse",
    "AmapSearchRequest",
    
    # 回收地点推荐模型
    "RecyclingLocationResponse",
    "RecyclingLocationDataConverter",
    
    # 回收捐赠总协调器模型
    "RecyclingCoordinatorResponse",
    "RecyclingCoordinatorDataConverter",
    
    # 爱回收搜索模型
    "AihuishouProduct",
    "AihuishouPriceStats",
    "AihuishouSearchRequest",
    "AihuishouSearchResponse",
    "AihuishouSearchDataConverter",
    
    # 闲鱼搜索模型
    "XianyuProduct",
    "XianyuPriceStats",
    "XianyuSearchRequest",
    "XianyuSearchResponse",
    "XianyuSearchDataConverter",
    
    # 任务相关模型
    "ProcessingTask",
    "RecyclingChannel",
    "OnlineRecyclingPlatform",
    "TaskCreate",
    "TaskResponse",
    "TaskStatus",
    "ProcessingResult",
    
    # 二手平台搜索相关模型
    "SecondhandPlatformProduct",
    "XianyuSimplifiedProduct",
    "AihuishouSimplifiedProduct",
    "PlatformPriceStats",
    "SecondhandSearchKeywords",
    "SecondhandSearchRequest",
    "SecondhandSearchResult",
    "SecondhandSearchDataConverter",
    
    # 文案生成相关模型
    "ContentGenerationResult",
    "ContentGenerationResponse",
    "ContentGenerationDataConverter",
    
    # 总处理协调器相关模型
    "ProcessingStep",
    "ProcessingStepStatus",
    "ProcessingMasterRequest",
    "ProcessingMasterResponse",
    "ProcessingAnalysisMetadata",
    "ProcessingAgentSummary",
    "ProcessingMetadata",
    "DisposalSolution",
    "CreativeSolution",
    "RecyclingSolution",
    "SecondhandSolution",
    "ProcessingMasterDataConverter"
] 