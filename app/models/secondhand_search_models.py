"""
二手平台搜索Agent相关数据模型

包含闲鱼和爱回收平台的简化数据结构，以及统一的搜索结果封装
"""

from typing import List, Optional, Dict, Any, Union

from pydantic import BaseModel, Field


class SecondhandPlatformProduct(BaseModel):
    """二手平台通用产品信息基类"""
    platform: str = Field(..., description="平台名称：xianyu/aihuishou")
    title: str = Field(..., description="商品标题/名称")
    price: Union[int, float] = Field(..., description="价格")
    image_url: str = Field(..., description="商品图片URL")
    
    class Config:
        extra = "allow"  # 允许额外字段


class XianyuSimplifiedProduct(SecondhandPlatformProduct):
    """闲鱼简化产品信息"""
    platform: str = Field(default="xianyu", description="平台名称")
    title: str = Field(..., description="商品标题")
    user_nick: str = Field(..., description="卖家昵称")
    price: Union[int, float] = Field(..., description="商品价格")
    pic_url: str = Field(..., description="商品图片URL")
    area: Optional[str] = Field(None, description="所在地区")
    
    @property
    def image_url(self) -> str:
        """统一图片URL字段名"""
        return self.pic_url
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        return {
            "platform": self.platform,
            "title": self.title,
            "user_nick": self.user_nick,
            "price": self.price,
            "pic_url": self.pic_url,
            "area": self.area
        }


class AihuishouSimplifiedProduct(SecondhandPlatformProduct):
    """爱回收简化产品信息"""
    platform: str = Field(default="aihuishou", description="平台名称")
    name: str = Field(..., description="产品名称")
    max_price: int = Field(..., description="最高回收价格")
    image_url: str = Field(..., description="产品图片URL")
    
    @property
    def title(self) -> str:
        """统一标题字段名"""
        return self.name
    
    @property
    def price(self) -> int:
        """统一价格字段名"""
        return self.max_price
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        return {
            "platform": self.platform,
            "name": self.name,
            "max_price": self.max_price,
            "image_url": self.image_url
        }


class PlatformPriceStats(BaseModel):
    """平台价格统计信息"""
    platform: str = Field(..., description="平台名称")
    min_price: Union[int, float] = Field(..., description="最低价格")
    max_price: Union[int, float] = Field(..., description="最高价格")
    average_price: float = Field(..., description="平均价格")
    product_count: int = Field(..., description="产品数量")
    price_range: str = Field(..., description="价格区间描述")


class SecondhandSearchKeywords(BaseModel):
    """二手平台搜索关键词"""
    keywords: List[str] = Field(..., description="搜索关键词列表")
    search_intent: str = Field(..., description="搜索意图说明")
    platform_suggestions: Dict[str, List[str]] = Field(
        default_factory=dict,
        description="各平台的特定关键词建议"
    )


class SecondhandSearchRequest(BaseModel):
    """二手平台搜索请求"""
    analysis_result: Dict[str, Any] = Field(..., description="物品分析结果")
    max_results_per_platform: int = Field(default=10, description="每个平台最大返回结果数")
    include_xianyu: bool = Field(default=True, description="是否包含闲鱼搜索")
    include_aihuishou: bool = Field(default=True, description="是否包含爱回收搜索")


class SecondhandSearchResult(BaseModel):
    """二手平台搜索结果"""
    success: bool = Field(..., description="搜索是否成功")
    keywords: Optional[SecondhandSearchKeywords] = Field(None, description="使用的搜索关键词")
    
    # 闲鱼结果
    xianyu_success: bool = Field(default=False, description="闲鱼搜索是否成功")
    xianyu_products: List[XianyuSimplifiedProduct] = Field(
        default_factory=list,
        description="闲鱼产品列表"
    )
    xianyu_stats: Optional[PlatformPriceStats] = Field(None, description="闲鱼价格统计")
    xianyu_error: Optional[str] = Field(None, description="闲鱼搜索错误信息")
    
    # 爱回收结果
    aihuishou_success: bool = Field(default=False, description="爱回收搜索是否成功")
    aihuishou_products: List[AihuishouSimplifiedProduct] = Field(
        default_factory=list,
        description="爱回收产品列表"
    )
    aihuishou_stats: Optional[PlatformPriceStats] = Field(None, description="爱回收价格统计")
    aihuishou_error: Optional[str] = Field(None, description="爱回收搜索错误信息")
    
    # 汇总信息
    total_products: int = Field(default=0, description="总产品数量")
    error_message: Optional[str] = Field(None, description="总体错误信息")
    
    def calculate_totals(self) -> None:
        """计算汇总信息"""
        self.total_products = len(self.xianyu_products) + len(self.aihuishou_products)
        self.success = self.xianyu_success or self.aihuishou_success
    
    @classmethod
    def from_platform_results(
        cls,
        keywords: SecondhandSearchKeywords,
        xianyu_result: Optional[Dict[str, Any]] = None,
        aihuishou_result: Optional[Dict[str, Any]] = None
    ) -> 'SecondhandSearchResult':
        """从平台搜索结果创建对象"""
        result = cls(success=False, keywords=keywords)
        
        # 处理闲鱼结果
        if xianyu_result:
            try:
                if xianyu_result.get("success", False):
                    result.xianyu_success = True
                    # 转换产品数据
                    for product_data in xianyu_result.get("products", []):
                        product = XianyuSimplifiedProduct(
                            title=product_data.get("title", ""),
                            user_nick=product_data.get("user_nick", ""),
                            price=product_data.get("price", 0),
                            pic_url=product_data.get("pic_url", ""),
                            area=product_data.get("area")
                        )
                        result.xianyu_products.append(product)
                    
                    # 转换价格统计
                    if "price_stats" in xianyu_result:
                        stats = xianyu_result["price_stats"]
                        result.xianyu_stats = PlatformPriceStats(
                            platform="xianyu",
                            min_price=stats.get("min_price", 0),
                            max_price=stats.get("max_price", 0),
                            average_price=stats.get("average_price", 0),
                            product_count=len(result.xianyu_products),
                            price_range=stats.get("price_range", "")
                        )
                else:
                    result.xianyu_error = xianyu_result.get("error_message", "闲鱼搜索失败")
            except Exception as e:
                result.xianyu_error = f"闲鱼结果解析失败: {str(e)}"
        
        # 处理爱回收结果
        if aihuishou_result:
            try:
                if aihuishou_result.get("success", False):
                    result.aihuishou_success = True
                    # 转换产品数据
                    for product_data in aihuishou_result.get("products", []):
                        product = AihuishouSimplifiedProduct(
                            name=product_data.get("name", ""),
                            max_price=product_data.get("max_price", 0),
                            image_url=product_data.get("image_url", "")
                        )
                        result.aihuishou_products.append(product)
                    
                    # 转换价格统计
                    if "price_stats" in aihuishou_result:
                        stats = aihuishou_result["price_stats"]
                        result.aihuishou_stats = PlatformPriceStats(
                            platform="aihuishou",
                            min_price=stats.get("min_price", 0),
                            max_price=stats.get("max_price", 0),
                            average_price=stats.get("average_price", 0),
                            product_count=len(result.aihuishou_products),
                            price_range=stats.get("price_range", "")
                        )
                else:
                    result.aihuishou_error = aihuishou_result.get("error", "爱回收搜索失败")
            except Exception as e:
                result.aihuishou_error = f"爱回收结果解析失败: {str(e)}"
        
        # 计算汇总信息
        result.calculate_totals()
        
        return result


class SecondhandSearchDataConverter:
    """二手平台搜索数据转换器"""
    
    @staticmethod
    def to_unified_format(result: SecondhandSearchResult) -> Dict[str, Any]:
        """转换为统一格式"""
        unified_products = []
        
        # 添加闲鱼产品
        for product in result.xianyu_products:
            unified_products.append({
                "platform": "闲鱼",
                "title": product.title,
                "seller": product.user_nick,
                "price": product.price,
                "image_url": product.pic_url,
                "location": product.area,
                "platform_type": "C2C"  # 个人对个人
            })
        
        # 添加爱回收产品
        for product in result.aihuishou_products:
            unified_products.append({
                "platform": "爱回收",
                "title": product.name,
                "seller": "爱回收官方",
                "price": product.max_price,
                "image_url": product.image_url,
                "location": "全国",
                "platform_type": "B2C"  # 商家对个人
            })
        
        return {
            "success": result.success,
            "total_products": result.total_products,
            "products": unified_products,
            "platform_stats": {
                "xianyu": {
                    "success": result.xianyu_success,
                    "product_count": len(result.xianyu_products),
                    "price_stats": result.xianyu_stats.dict() if result.xianyu_stats else None,
                    "error": result.xianyu_error
                },
                "aihuishou": {
                    "success": result.aihuishou_success,
                    "product_count": len(result.aihuishou_products),
                    "price_stats": result.aihuishou_stats.dict() if result.aihuishou_stats else None,
                    "error": result.aihuishou_error
                }
            },
            "keywords": {
                "keywords": result.keywords.keywords if result.keywords else [],
                "search_intent": result.keywords.search_intent if result.keywords else "",
                "platform_suggestions": result.keywords.platform_suggestions if result.keywords else {}
            }
        }
    
    @staticmethod
    def to_simplified_format(result: SecondhandSearchResult) -> Dict[str, Any]:
        """转换为简化格式"""
        return {
            "success": result.success,
            "total_products": result.total_products,
            "xianyu_count": len(result.xianyu_products),
            "aihuishou_count": len(result.aihuishou_products),
            "keywords": result.keywords.keywords if result.keywords else [],
            "search_intent": result.keywords.search_intent if result.keywords else "",
            "platforms": {
                "xianyu": result.xianyu_success,
                "aihuishou": result.aihuishou_success
            },
            "price_summary": {
                "xianyu_range": result.xianyu_stats.price_range if result.xianyu_stats else "无数据",
                "aihuishou_range": result.aihuishou_stats.price_range if result.aihuishou_stats else "无数据"
            }
        } 