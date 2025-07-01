"""
闲鱼搜索API相关数据模型

包含产品信息、搜索结果、价格统计等数据结构
"""

from typing import List, Optional, Dict, Any, Union
from pydantic import BaseModel, Field
import re


class XianyuProduct(BaseModel):
    """闲鱼产品信息"""
    item_id: str = Field(..., description="商品ID")
    title: str = Field(..., description="商品标题")
    user_nick: str = Field(..., description="卖家昵称")
    price: Union[int, float] = Field(..., description="商品价格")
    pic_url: str = Field(..., description="商品图片URL")
    area: Optional[str] = Field(None, description="所在地区")
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        return {
            "item_id": self.item_id,
            "title": self.title,
            "user_nick": self.user_nick,
            "price": self.price,
            "pic_url": self.pic_url,
            "area": self.area
        }


class XianyuPriceStats(BaseModel):
    """闲鱼价格统计信息"""
    min_price: float = Field(..., description="最低价格")
    max_price: float = Field(..., description="最高价格")
    average_price: float = Field(..., description="平均价格")
    total_products: int = Field(..., description="产品总数")
    price_range: str = Field(..., description="价格区间描述")
    
    @classmethod
    def calculate_from_products(cls, products: List[XianyuProduct]) -> 'XianyuPriceStats':
        """从产品列表计算价格统计"""
        if not products:
            return cls(
                min_price=0.0,
                max_price=0.0,
                average_price=0.0,
                total_products=0,
                price_range="无产品数据"
            )
        
        prices = [float(product.price) for product in products]
        min_price = min(prices)
        max_price = max(prices)
        average_price = sum(prices) / len(prices)
        
        price_range = f"¥{min_price:.2f} - ¥{max_price:.2f}"
        
        return cls(
            min_price=min_price,
            max_price=max_price,
            average_price=round(average_price, 2),
            total_products=len(products),
            price_range=price_range
        )


class XianyuSearchRequest(BaseModel):
    """闲鱼搜索请求参数"""
    keyword: str = Field(..., description="搜索关键词")
    page_number: int = Field(default=1, description="页码")
    rows_per_page: int = Field(default=30, description="每页记录数")
    platform: str = Field(default="pc", description="平台类型")
    search_req_from_page: str = Field(default="xyHome", description="搜索来源页面")
    biz_from: str = Field(default="home", description="业务来源")
    search_tab_type: str = Field(default="SEARCH_TAB_MAIN", description="搜索标签类型")
    sort_field: str = Field(default="", description="排序字段")
    sort_value: str = Field(default="", description="排序值")
    prop_value_str: str = Field(default="", description="属性值字符串")

    def to_api_data(self) -> Dict[str, Any]:
        """转换为API数据格式"""
        return {
            "keyword": self.keyword,
            "pageNumber": self.page_number,
            "rowsPerPage": self.rows_per_page,
            "plateform": self.platform,  # 注意：原API中是plateform而非platform
            "searchReqFromPage": self.search_req_from_page,
            "bizFrom": self.biz_from,
            "searchTabType": self.search_tab_type,
            "sortField": self.sort_field,
            "sortValue": self.sort_value,
            "propValueStr": self.prop_value_str
        }

    def to_request_body(self) -> str:
        """转换为请求体格式（URL编码）"""
        import urllib.parse
        
        data = self.to_api_data()
        
        # 转换为JSON字符串然后URL编码
        import json
        json_str = json.dumps(data, ensure_ascii=False)
        return f"data={urllib.parse.quote(json_str)}"


class XianyuSearchResponse(BaseModel):
    """闲鱼搜索响应"""
    api: Optional[str] = Field(None, description="API名称")
    success: bool = Field(default=False, description="请求是否成功")
    data: List[XianyuProduct] = Field(default_factory=list, description="产品数据列表")
    total_count: Optional[int] = Field(None, description="总记录数")
    error_message: Optional[str] = Field(None, description="错误信息")
    
    # 计算的统计信息
    price_stats: Optional[XianyuPriceStats] = Field(None, description="价格统计信息")
    
    @property
    def product_count(self) -> int:
        """获取产品数量"""
        return len(self.data)
    
    def calculate_price_stats(self) -> None:
        """计算价格统计信息"""
        self.price_stats = XianyuPriceStats.calculate_from_products(self.data)
    
    @classmethod
    def from_api_response(cls, api_data: Dict[str, Any]) -> 'XianyuSearchResponse':
        """从API响应数据创建对象"""
        products = []
        success = False
        error_message = None
        
        try:
            # 检查API响应结构
            if "data" in api_data and "resultList" in api_data["data"]:
                result_list = api_data["data"]["resultList"]
                
                for item in result_list:
                    try:
                        # 解析产品数据
                        if ("data" in item and 
                            "item" in item["data"] and 
                            "main" in item["data"]["item"] and
                            "exContent" in item["data"]["item"]["main"]):
                            
                            ex_content = item["data"]["item"]["main"]["exContent"]
                            detail_params = ex_content.get("detailParams", {})
                            
                            # 提取价格 - 可能是字符串或数字
                            price_value = detail_params.get("soldPrice", "0")
                            try:
                                price = float(price_value) if price_value else 0.0
                            except (ValueError, TypeError):
                                # 尝试从字符串中提取数字
                                price_match = re.search(r'[\d.]+', str(price_value))
                                price = float(price_match.group()) if price_match else 0.0
                            
                            product = XianyuProduct(
                                item_id=detail_params.get("itemId", ""),
                                title=detail_params.get("title", ""),
                                user_nick=detail_params.get("userNick", ""),
                                price=price,
                                pic_url=ex_content.get("picUrl", ""),
                                area=ex_content.get("area", "")
                            )
                            
                            # 只添加有效价格的产品
                            if price > 0:
                                products.append(product)
                                
                    except Exception as e:
                        # 忽略解析失败的单个产品
                        continue
                
                success = len(products) > 0
                
            else:
                error_message = "API响应格式不正确"
                
        except Exception as e:
            error_message = f"解析API响应失败: {str(e)}"
        
        # 创建响应对象
        response = cls(
            api=api_data.get("api"),
            success=success,
            data=products,
            error_message=error_message
        )
        
        # 计算价格统计
        if products:
            response.calculate_price_stats()
        
        return response


class XianyuSearchDataConverter:
    """闲鱼搜索数据转换器"""
    
    @staticmethod
    def to_simplified_format(response: XianyuSearchResponse) -> Dict[str, Any]:
        """转换为简化格式"""
        result = {
            "success": response.success,
            "total_products": response.product_count,
            "products": []
        }
        
        # 只保留关键字段
        for product in response.data:
            simplified_product = {
                "title": product.title,
                "user_nick": product.user_nick,
                "price": product.price,
                "pic_url": product.pic_url,
                "area": product.area
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
        
        # 添加错误信息（如果有）
        if response.error_message:
            result["error_message"] = response.error_message
        
        return result
    
    @staticmethod
    def to_detailed_format(response: XianyuSearchResponse) -> Dict[str, Any]:
        """转换为详细格式"""
        result = {
            "success": response.success,
            "api": response.api,
            "total_products": response.product_count,
            "products": [product.to_dict() for product in response.data]
        }
        
        # 添加价格统计
        if response.price_stats:
            result["price_stats"] = {
                "min_price": response.price_stats.min_price,
                "max_price": response.price_stats.max_price,
                "average_price": response.price_stats.average_price,
                "total_products": response.price_stats.total_products,
                "price_range": response.price_stats.price_range
            }
        
        # 添加错误信息（如果有）
        if response.error_message:
            result["error_message"] = response.error_message
        
        return result 