"""
爱回收搜索服务

提供基于爱回收API的产品搜索功能，包括价格统计分析
"""

import json
from typing import Optional, Dict, Any

import aiohttp
from tenacity import retry, stop_after_attempt, wait_exponential

from app.core.logger import app_logger
from app.models.aihuishou_models import (
    AihuishouSearchRequest,
    AihuishouSearchResponse,
    AihuishouProduct,
    AihuishouPriceStats,
    AihuishouSearchDataConverter
)


class AihuishouService:
    """爱回收搜索服务类"""
    
    def __init__(self):
        # API基础配置
        self.base_url = "https://dubai.aihuishou.com/dubai-gateway/recycle-products/search-v9"
        self.timeout = 30  # 超时时间（秒）
        self.max_retries = 3  # 最大重试次数
        
        # 请求头配置（基于示例代码）
        self.headers = {
            "accept": "application/json, text/plain, */*",
            "accept-language": "zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6",
            "ahs-app-id": "10002",
            "ahs-app-version": "7.15.5",
            "ahs-device-id": "197baf39ec11eb9-0fd2a11d6d7e598-4c657b58-1638720-197baf39ec2217f",
            "ahs-session-id": "4a68af24-1301-44a0-a46f-976727c83b85",
            "ahs-sign": "f2bc155b340d64c0d2e1adecbfad4f76",
            "ahs-timestamp": "1751283437",
            "ahs-token": "",
            "cache-control": "no-cache",
            "content-type": "application/json;charset=UTF-8",
            "pragma": "no-cache",
            "priority": "u=1, i",
            "sec-fetch-dest": "empty",
            "sec-fetch-mode": "cors",
            "sec-fetch-site": "same-site",
            "x-requested-with": "axios",
            "x-version": "undefined",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        }
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=8),
        reraise=True
    )
    async def _make_request(self, search_request: AihuishouSearchRequest) -> Dict[str, Any]:
        """发起HTTP请求到爱回收API"""
        request_body = search_request.to_request_body()
        
        async with aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=self.timeout)
        ) as session:
            try:
                app_logger.info(f"发起爱回收API请求: {search_request.keyword}")
                app_logger.debug(f"请求体: {json.dumps(request_body, ensure_ascii=False)}")
                
                async with session.post(
                    self.base_url,
                    headers=self.headers,
                    json=request_body
                ) as response:
                    if response.status != 200:
                        raise aiohttp.ClientResponseError(
                            request_info=response.request_info,
                            history=response.history,
                            status=response.status,
                            message=f"爱回收API请求失败: HTTP {response.status}"
                        )
                    
                    data = await response.json()
                    app_logger.info(
                        f"爱回收API响应: code={data.get('code')}, "
                        f"产品数量={len(data.get('data', []))}"
                    )
                    
                    return data
                    
            except aiohttp.ClientError as e:
                app_logger.error(f"爱回收API请求错误: {e}")
                raise
            except Exception as e:
                app_logger.error(f"爱回收API请求异常: {e}")
                raise
    
    async def search_products(
        self,
        keyword: str,
        city_id: int = 103,
        page_size: int = 20,
        page_index: int = 0
    ) -> AihuishouSearchResponse:
        """
        搜索爱回收产品
        
        Args:
            keyword: 搜索关键词
            city_id: 城市ID，默认103（广州）
            page_size: 每页记录数，默认20
            page_index: 页码索引，默认0
        
        Returns:
            AihuishouSearchResponse: 搜索结果
        
        Raises:
            ValueError: 参数错误
            aiohttp.ClientError: 网络请求错误
        """
        # 验证参数
        if not keyword or not keyword.strip():
            raise ValueError("搜索关键词不能为空")
        
        if page_size < 1 or page_size > 50:
            raise ValueError("page_size参数范围应为1-50")
        
        if page_index < 0:
            raise ValueError("page_index参数应大于等于0")
        
        # 构建搜索请求
        search_request = AihuishouSearchRequest(
            keyword=keyword.strip(),
            city_id=city_id,
            page_size=page_size,
            page_index=page_index
        )
        
        try:
            # 发起API请求
            api_data = await self._make_request(search_request)
            
            # 解析响应数据
            response = AihuishouSearchResponse.from_api_response(api_data)
            
            app_logger.info(
                f"爱回收搜索完成: 关键词='{keyword}', "
                f"找到{response.product_count}个产品"
            )
            
            if response.price_stats:
                app_logger.info(
                    f"价格统计: {response.price_stats.price_range}, "
                    f"平均价格=¥{response.price_stats.average_price}"
                )
            
            return response
            
        except Exception as e:
            app_logger.error(f"爱回收产品搜索失败: {e}")
            raise
    
    async def search_with_price_analysis(
        self,
        keyword: str,
        city_id: int = 103,
        page_size: int = 20
    ) -> Dict[str, Any]:
        """
        搜索产品并进行价格分析
        
        Args:
            keyword: 搜索关键词
            city_id: 城市ID
            page_size: 每页记录数
        
        Returns:
            包含产品信息和价格分析的字典
        """
        try:
            # 执行搜索
            response = await self.search_products(
                keyword=keyword,
                city_id=city_id,
                page_size=page_size
            )
            
            # 转换为简化格式
            result = AihuishouSearchDataConverter.to_simplified_format(response)
            
            # 添加详细的价格分析
            if response.price_stats and response.product_count > 0:
                prices = [product.max_price for product in response.data]
                
                # 价格分布分析
                price_distribution = self._analyze_price_distribution(prices)
                
                result["price_analysis"] = {
                    "basic_stats": result["price_stats"],
                    "distribution": price_distribution,
                    "recommendations": self._generate_price_recommendations(response.price_stats)
                }
            
            return result
            
        except Exception as e:
            app_logger.error(f"价格分析搜索失败: {e}")
            return {
                "success": False,
                "error": str(e),
                "total_products": 0,
                "products": [],
                "price_stats": None,
                "price_analysis": None
            }
    
    def _analyze_price_distribution(self, prices: list) -> Dict[str, Any]:
        """分析价格分布"""
        if not prices:
            return {}
        
        # 价格区间统计
        price_ranges = {
            "0-500": 0,
            "500-1000": 0,
            "1000-2000": 0,
            "2000-5000": 0,
            "5000+": 0
        }
        
        for price in prices:
            if price <= 500:
                price_ranges["0-500"] += 1
            elif price <= 1000:
                price_ranges["500-1000"] += 1
            elif price <= 2000:
                price_ranges["1000-2000"] += 1
            elif price <= 5000:
                price_ranges["2000-5000"] += 1
            else:
                price_ranges["5000+"] += 1
        
        # 计算中位数
        sorted_prices = sorted(prices)
        n = len(sorted_prices)
        median = (sorted_prices[n//2] + sorted_prices[(n-1)//2]) / 2
        
        return {
            "price_ranges": price_ranges,
            "median_price": round(median, 2),
            "price_variance": round(self._calculate_variance(prices), 2),
            "total_items": len(prices)
        }
    
    def _calculate_variance(self, prices: list) -> float:
        """计算价格方差"""
        if not prices:
            return 0.0
        
        mean = sum(prices) / len(prices)
        variance = sum((x - mean) ** 2 for x in prices) / len(prices)
        return variance
    
    def _generate_price_recommendations(self, price_stats: AihuishouPriceStats) -> Dict[str, str]:
        """生成价格建议"""
        recommendations = {}
        
        # 基于平均价格的建议
        if price_stats.average_price < 500:
            recommendations["selling_advice"] = "该类型产品回收价值较低，建议考虑创意改造或捐赠"
        elif price_stats.average_price < 1500:
            recommendations["selling_advice"] = "该类型产品有一定回收价值，可以考虑出售"
        else:
            recommendations["selling_advice"] = "该类型产品回收价值较高，建议优先考虑出售"
        
        # 基于价格区间的建议
        price_gap = price_stats.max_price - price_stats.min_price
        if price_gap > price_stats.average_price:
            recommendations["condition_advice"] = "产品状况对价格影响较大，建议详细描述物品状况"
        else:
            recommendations["condition_advice"] = "该类型产品价格相对稳定"
        
        return recommendations


# 全局服务实例
aihuishou_service = AihuishouService()


async def search_aihuishou_products(
    keyword: str,
    city_id: int = 103,
    page_size: int = 20,
    include_price_analysis: bool = True
) -> Dict[str, Any]:
    """
    搜索爱回收产品的便捷函数
    
    Args:
        keyword: 搜索关键词
        city_id: 城市ID
        page_size: 每页记录数
        include_price_analysis: 是否包含价格分析
    
    Returns:
        搜索结果字典
    """
    if include_price_analysis:
        return await aihuishou_service.search_with_price_analysis(
            keyword=keyword,
            city_id=city_id,
            page_size=page_size
        )
    else:
        response = await aihuishou_service.search_products(
            keyword=keyword,
            city_id=city_id,
            page_size=page_size
        )
        return AihuishouSearchDataConverter.to_simplified_format(response) 