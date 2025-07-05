"""
二手交易平台推荐模型

定义平台信息、用户数据、检索结果等数据结构
"""

from typing import Optional, List, Dict, Any

from pydantic import BaseModel, Field


class UserDataModel(BaseModel):
    """用户数据模型"""
    registered_users: Optional[str] = Field(None, description="注册用户数")
    monthly_active_users: Optional[str] = Field(None, description="月活用户数")
    cumulative_users: Optional[str] = Field(None, description="累计用户数")
    daily_new_users: Optional[str] = Field(None, description="日新增用户数")
    transaction_volume: Optional[str] = Field(None, description="交易量")
    recycled_books: Optional[str] = Field(None, description="回收书籍数（特定平台）")
    note: Optional[str] = Field(None, description="特殊说明")


class RatingModel(BaseModel):
    """评分模型"""
    app_store: Optional[float] = Field(None, description="App Store评分")
    yingyongbao: Optional[float] = Field(None, description="应用宝评分")
    kuan: Optional[float] = Field(None, description="酷安评分")


class SecondhandPlatformModel(BaseModel):
    """二手交易平台模型"""
    platform_icon: str = Field(..., description="平台图标")
    platform_name: str = Field(..., description="平台名称")
    description: str = Field(..., description="平台描述")
    focus_categories: List[str] = Field(..., description="主要品类")
    tags: List[str] = Field(..., description="平台特色标签")
    user_data: UserDataModel = Field(..., description="用户数据")
    rating: RatingModel = Field(..., description="平台评分")
    transaction_model: str = Field(..., description="交易模式")


class ItemAnalysisModel(BaseModel):
    """物品分析结果模型"""
    category: str = Field(..., description="物品类别", example="电子产品")
    sub_category: Optional[str] = Field(None, description="子类别", example="智能手机")
    brand: Optional[str] = Field(None, description="品牌", example="苹果")
    condition: Optional[str] = Field(None, description="物品状况", example="九成新")
    material: Optional[str] = Field(None, description="材质", example="金属和玻璃")
    color: Optional[str] = Field(None, description="颜色", example="黑色")
    keywords: List[str] = Field(..., description="关键词列表", example=["iPhone", "智能手机", "黑色", "苹果"])
    description: str = Field(..., description="物品描述", example="一台黑色的苹果iPhone手机，具体型号未知。")
    estimated_age: Optional[str] = Field(None, description="估计使用时间", example="未知")
    special_features: Optional[str] = Field(None, description="特殊功能", example="未知")


class RAGSearchRequest(BaseModel):
    """RAG搜索请求模型"""
    item_analysis: ItemAnalysisModel = Field(..., description="物品分析结果")
    max_results: Optional[int] = Field(5, description="最大返回结果数", ge=1, le=20)
    similarity_threshold: Optional[float] = Field(0.1, description="相似度阈值", ge=0.0, le=1.0)


class RAGSearchResponse(BaseModel):
    """RAG搜索响应模型"""
    results: List[Dict[str, Any]] = Field(..., description="搜索结果")
    search_metadata: Dict[str, Any] = Field(..., description="搜索元数据") 