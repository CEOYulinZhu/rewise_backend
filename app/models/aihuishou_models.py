"""
爱回收搜索API相关数据模型

包含产品信息、搜索结果、价格统计等数据结构
"""

from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


class AihuishouProduct(BaseModel):
    """爱回收产品信息"""
    id: int = Field(..., description="产品ID")
    name: str = Field(..., description="产品名称")
    max_price: int = Field(..., description="最高回收价格")
    image_url: str = Field(..., description="产品图片URL")
    category_id: Optional[int] = Field(None, description="分类ID")
    brand_id: Optional[int] = Field(None, description="品牌ID")
    biz_type: Optional[int] = Field(None, description="业务类型")
    type: Optional[int] = Field(None, description="产品类型")
    is_environmental_recycling: Optional[bool] = Field(None, description="是否环保回收")
    link: Optional[str] = Field(None, description="产品链接")
    marketing_tag_text: Optional[str] = Field(None, description="营销标签文本")

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        return {
            "id": self.id,
            "name": self.name,
            "max_price": self.max_price,
            "image_url": self.image_url,
            "category_id": self.category_id,
            "brand_id": self.brand_id,
            "biz_type": self.biz_type,
            "type": self.type,
            "is_environmental_recycling": self.is_environmental_recycling,
            "link": self.link,
            "marketing_tag_text": self.marketing_tag_text
        }


class AihuishouPriceStats(BaseModel):
    """爱回收价格统计信息"""
    min_price: int = Field(..., description="最低价格")
    max_price: int = Field(..., description="最高价格")
    average_price: float = Field(..., description="平均价格")
    total_products: int = Field(..., description="产品总数")
    price_range: str = Field(..., description="价格区间描述")
    
    @classmethod
    def calculate_from_products(cls, products: List[AihuishouProduct]) -> 'AihuishouPriceStats':
        """从产品列表计算价格统计"""
        if not products:
            return cls(
                min_price=0,
                max_price=0,
                average_price=0.0,
                total_products=0,
                price_range="无产品数据"
            )
        
        prices = [product.max_price for product in products]
        min_price = min(prices)
        max_price = max(prices)
        average_price = sum(prices) / len(prices)
        
        price_range = f"¥{min_price} - ¥{max_price}"
        
        return cls(
            min_price=min_price,
            max_price=max_price,
            average_price=round(average_price, 2),
            total_products=len(products),
            price_range=price_range
        )


class AihuishouSearchRequest(BaseModel):
    """爱回收搜索请求参数"""
    keyword: str = Field(..., description="搜索关键词")
    scene: str = Field(default="RECYCLE", description="搜索场景")
    city_id: int = Field(default=103, description="城市ID，默认广州")
    biz_types: List[int] = Field(
        default_factory=lambda: [1, 2, 3, 4, 5, 8, 9, 10, 13, 7, 12, 14, 15, 16, 17, 1000],
        description="业务类型列表"
    )
    page_size: int = Field(default=20, description="每页记录数")
    page_index: int = Field(default=0, description="页码索引")

    def to_request_body(self) -> Dict[str, Any]:
        """转换为请求体格式"""
        return {
            "keyword": self.keyword,
            "scene": self.scene,
            "cityId": self.city_id,
            "bizTypes": self.biz_types,
            "pageSize": self.page_size,
            "pageIndex": self.page_index
        }


class AihuishouSearchResponse(BaseModel):
    """爱回收搜索响应"""
    code: int = Field(..., description="响应状态码")
    result_message: str = Field(default="", description="响应消息")
    data: List[AihuishouProduct] = Field(default_factory=list, description="产品数据列表")
    page: Optional[int] = Field(None, description="当前页码")
    page_size: Optional[int] = Field(None, description="每页大小")
    total_count: Optional[int] = Field(None, description="总记录数")
    
    # 计算的统计信息
    price_stats: Optional[AihuishouPriceStats] = Field(None, description="价格统计信息")
    
    @property
    def is_success(self) -> bool:
        """判断请求是否成功"""
        return self.code == 0
    
    @property
    def product_count(self) -> int:
        """获取产品数量"""
        return len(self.data)
    
    def calculate_price_stats(self) -> None:
        """计算价格统计信息"""
        self.price_stats = AihuishouPriceStats.calculate_from_products(self.data)
    
    @classmethod
    def from_api_response(cls, api_data: Dict[str, Any]) -> 'AihuishouSearchResponse':
        """从API响应数据创建对象"""
        # 解析产品数据
        products = []
        if "data" in api_data and isinstance(api_data["data"], list):
            for item in api_data["data"]:
                try:
                    product = AihuishouProduct(
                        id=item["id"],
                        name=item["name"],
                        max_price=item["maxPrice"],
                        image_url=item["imageUrl"],
                        category_id=item.get("categoryId"),
                        brand_id=item.get("brandId"),
                        biz_type=item.get("bizType"),
                        type=item.get("type"),
                        is_environmental_recycling=item.get("isEnvironmentalRecycling"),
                        link=item.get("link"),
                        marketing_tag_text=item.get("marketingTagText")
                    )
                    products.append(product)
                except Exception as e:
                    # 忽略解析失败的产品，但记录警告
                    continue
        
        # 创建响应对象
        response = cls(
            code=api_data.get("code", -1),
            result_message=api_data.get("resultMessage", ""),
            data=products,
            page=api_data.get("page"),
            page_size=api_data.get("pageSize"),
            total_count=api_data.get("totalCount")
        )
        
        # 计算价格统计
        response.calculate_price_stats()
        
        return response


class AihuishouSearchDataConverter:
    """爱回收搜索数据转换器"""
    
    @staticmethod
    def to_simplified_format(response: AihuishouSearchResponse) -> Dict[str, Any]:
        """转换为简化格式"""
        result = {
            "success": response.is_success,
            "total_products": response.product_count,
            "products": []
        }
        
        # 只保留关键字段
        for product in response.data:
            simplified_product = {
                "name": product.name,
                "max_price": product.max_price,
                "image_url": product.image_url
            }
            result["products"].append(simplified_product)
        
        # 添加价格统计
        if response.price_stats:
            result["price_stats"] = {
                "min_price": response.price_stats.min_price,
                "max_price": response.price_stats.max_price,
                "average_price": response.price_stats.average_price,
                "price_range": response.price_stats.price_range
            }
        
        return result
    
    @staticmethod
    def to_detailed_format(response: AihuishouSearchResponse) -> Dict[str, Any]:
        """转换为详细格式"""
        result = {
            "success": response.is_success,
            "code": response.code,
            "message": response.result_message,
            "pagination": {
                "page": response.page,
                "page_size": response.page_size,
                "total_count": response.total_count,
                "current_count": response.product_count
            },
            "products": [product.to_dict() for product in response.data]
        }
        
        if response.price_stats:
            result["price_stats"] = response.price_stats.dict()
        
        return result 