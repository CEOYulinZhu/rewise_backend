"""
高德地图搜索服务

提供基于高德地图API的周边POI搜索功能
"""

from typing import List, Optional

import aiohttp
from tenacity import retry, stop_after_attempt, wait_exponential

from app.core.config import get_settings
from app.core.logger import app_logger
from app.models.amap_models import (
    AmapSearchRequest,
    AmapSearchResponse,
    AmapPOI,
    AmapPhoto
)
from app.utils.poi_filter import filter_recycling_pois, is_valid_recycling_keyword
from app.utils.distance_utils import calculate_distance_from_location, format_distance

settings = get_settings()


class AmapService:
    """高德地图服务类"""
    
    def __init__(self):
        self.api_key = settings.amap_api_key
        self.base_url = settings.amap_api_base_url
        self.timeout = settings.amap_timeout
        self.max_retries = settings.amap_max_retries
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=10),
        reraise=True
    )
    async def _make_request(self, params: dict) -> dict:
        """发起HTTP请求到高德地图API"""
        async with aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=self.timeout)
        ) as session:
            try:
                async with session.get(self.base_url, params=params) as response:
                    if response.status != 200:
                        raise aiohttp.ClientResponseError(
                            request_info=response.request_info,
                            history=response.history,
                            status=response.status,
                            message=f"高德地图API请求失败: HTTP {response.status}"
                        )
                    
                    data = await response.json()
                    app_logger.info(f"高德地图API响应: status={data.get('status')}, count={data.get('count')}")
                    
                    # 调试：打印第一个POI的详细结构（如果存在）
                    if data.get('pois') and len(data['pois']) > 0:
                        first_poi = data['pois'][0]
                        app_logger.debug(f"第一个POI的数据结构: {first_poi}")
                        if 'business' in first_poi:
                            app_logger.debug(f"第一个POI的business字段: {first_poi['business']}")
                    
                    return data
                    
            except aiohttp.ClientError as e:
                app_logger.error(f"高德地图API请求错误: {e}")
                raise
            except Exception as e:
                app_logger.error(f"高德地图API请求异常: {e}")
                raise
    
    def _parse_poi_data(self, poi_data: dict, user_location: Optional[str] = None) -> AmapPOI:
        """解析POI数据"""
        # 解析图片信息
        photos = []
        if "photos" in poi_data and poi_data["photos"]:
            for photo_data in poi_data["photos"]:
                photo = AmapPhoto(
                    title=photo_data.get("title"),
                    url=photo_data.get("url")
                )
                photos.append(photo)
        
        # 解析商业信息（这些字段在business对象内）
        business_info = poi_data.get("business", {}) if isinstance(poi_data.get("business"), dict) else {}
        
        # 提取营业时间和联系信息
        opentime_today = business_info.get("opentime_today") or poi_data.get("opentime_today")
        opentime_week = business_info.get("opentime_week") or poi_data.get("opentime_week")
        tel = business_info.get("tel") or poi_data.get("tel")
        
        # 计算距离（如果提供了用户位置）
        distance_meters = None
        distance_formatted = None
        
        if user_location:
            try:
                poi_location = poi_data["location"]
                distance_meters = calculate_distance_from_location(user_location, poi_location)
                distance_formatted = format_distance(distance_meters)
                app_logger.debug(f"POI {poi_data['name']} 距离用户 {distance_formatted}")
            except Exception as e:
                app_logger.warning(f"计算POI距离失败: {e}")
        
        # 创建POI对象
        poi = AmapPOI(
            id=poi_data["id"],
            name=poi_data["name"],
            location=poi_data["location"],
            type=poi_data["type"],
            typecode=poi_data["typecode"],
            address=poi_data["address"],
            pname=poi_data["pname"],
            cityname=poi_data["cityname"],
            adname=poi_data["adname"],
            pcode=poi_data["pcode"],
            citycode=poi_data["citycode"],
            adcode=poi_data["adcode"],
            opentime_today=opentime_today,
            opentime_week=opentime_week,
            tel=tel,
            photos=photos if photos else None,
            distance_meters=distance_meters,
            distance_formatted=distance_formatted
        )
        
        return poi
    
    async def search_around(
        self,
        location: str,
        keywords: Optional[str] = None,
        radius: int = 5000,
        page_size: int = 10,
        page_num: int = 1
    ) -> AmapSearchResponse:
        """
        搜索周边POI
        
        Args:
            location: 中心点坐标，格式为"经度,纬度"
            keywords: 搜索关键词
            radius: 搜索半径（米），范围0-50000
            page_size: 每页记录数，范围1-25
            page_num: 当前页数
        
        Returns:
            AmapSearchResponse: 搜索结果
        
        Raises:
            ValueError: 参数错误
            aiohttp.ClientError: 网络请求错误
        """
        # 验证参数
        if not location:
            raise ValueError("location参数不能为空")
        
        if radius < 0 or radius > 50000:
            raise ValueError("radius参数范围应为0-50000")
        
        if page_size < 1 or page_size > 25:
            raise ValueError("page_size参数范围应为1-25")
        
        if page_num < 1:
            raise ValueError("page_num参数应大于0")
        
        # 构建请求参数
        search_request = AmapSearchRequest(
            location=location,
            keywords=keywords,
            radius=radius,
            page_size=page_size,
            page_num=page_num
        )
        
        params = search_request.to_params_dict(self.api_key)
        
        try:
            # 发起API请求
            data = await self._make_request(params)
            
            # 解析响应数据
            pois = []
            if "pois" in data and data["pois"]:
                for poi_data in data["pois"]:
                    try:
                        poi = self._parse_poi_data(poi_data, user_location=location)
                        pois.append(poi)
                    except Exception as e:
                        app_logger.warning(f"解析POI数据失败: {e}, poi_data: {poi_data}")
                        continue
            
            response = AmapSearchResponse(
                status=data["status"],
                info=data["info"],
                infocode=data["infocode"],
                count=data["count"],
                pois=pois
            )
            
            if not response.is_success:
                app_logger.warning(f"高德地图API返回错误: {response.info}")
            
            return response
            
        except Exception as e:
            app_logger.error(f"搜索周边POI失败: {e}")
            raise
    
    async def search_by_keyword(
        self,
        location: str,
        keywords: str,
        radius: int = 50000,
        page_size: int = 20,
        enable_filter: bool = True,
        sort_by_distance: bool = True
    ) -> List[AmapPOI]:
        """
        根据关键词搜索周边POI（简化接口）
        
        Args:
            location: 中心点坐标，格式为"经度,纬度"
            keywords: 搜索关键词
            radius: 搜索半径（米）
            page_size: 每页记录数
            enable_filter: 是否启用关键词筛选
            sort_by_distance: 是否按距离排序
        
        Returns:
            List[AmapPOI]: POI列表（默认按距离排序）
        """
        if not keywords:
            raise ValueError("keywords参数不能为空")
        
        response = await self.search_around(
            location=location,
            keywords=keywords,
            radius=radius,
            page_size=page_size
        )
        
        if response.is_success:
            pois = response.pois
            
            # 如果启用筛选且关键词是支持的回收类型，则进行筛选
            if enable_filter and is_valid_recycling_keyword(keywords):
                app_logger.info(f"对关键词'{keywords}'的搜索结果进行筛选")
                pois = filter_recycling_pois(pois, keywords, strict_mode=True)
            
            # 按距离排序（如果启用）
            if sort_by_distance:
                pois = self._sort_pois_by_distance(pois)
            
            return pois
        else:
            app_logger.warning(f"搜索失败: {response.info}")
            return []
    
    async def get_poi_details(
        self,
        location: str,
        poi_id: str
    ) -> Optional[AmapPOI]:
        """
        获取特定POI的详细信息
        
        Args:
            location: 中心点坐标
            poi_id: POI唯一标识
        
        Returns:
            Optional[AmapPOI]: POI详细信息，未找到时返回None
        """
        # 通过搜索获取POI详情（高德地图周边搜索API的限制）
        response = await self.search_around(
            location=location,
            page_size=25  # 增加搜索数量以提高找到目标POI的概率
        )
        
        if response.is_success:
            for poi in response.pois:
                if poi.id == poi_id:
                    return poi
        
        return None

    def _sort_pois_by_distance(self, pois: List[AmapPOI]) -> List[AmapPOI]:
        """
        按距离对POI列表进行排序，距离近的排在前面
        
        Args:
            pois: POI列表
        
        Returns:
            List[AmapPOI]: 按距离排序的POI列表
        """
        if not pois:
            return pois
        
        # 过滤出有距离信息的POI，并按距离排序
        pois_with_distance = [poi for poi in pois if poi.distance_meters is not None]
        pois_without_distance = [poi for poi in pois if poi.distance_meters is None]
        
        # 按距离升序排序（距离近的在前）
        pois_with_distance.sort(key=lambda poi: poi.distance_meters)
        
        app_logger.info(
            f"POI距离排序完成: 有距离信息{len(pois_with_distance)}个, "
            f"无距离信息{len(pois_without_distance)}个"
        )
        
        # 显示前3个POI的距离信息（调试用）
        if pois_with_distance:
            app_logger.debug("前3个POI的距离信息:")
            for i, poi in enumerate(pois_with_distance[:3], 1):
                app_logger.debug(f"  {i}. {poi.name} - {poi.distance_formatted}")
        
        # 有距离信息的POI排在前面，无距离信息的排在后面
        return pois_with_distance + pois_without_distance


# 全局服务实例
amap_service = AmapService()


async def search_nearby_places(
    location: str,
    keywords: Optional[str] = None,
    radius: int = 5000,
    page_size: int = 10,
    enable_filter: bool = True,
    sort_by_distance: bool = True
) -> List[AmapPOI]:
    """
    搜索附近地点的便捷函数
    
    Args:
        location: 中心点坐标，格式为"经度,纬度"
        keywords: 搜索关键词
        radius: 搜索半径（米）
        page_size: 每页记录数
        enable_filter: 是否启用关键词筛选
        sort_by_distance: 是否按距离排序
    
    Returns:
        List[AmapPOI]: POI列表（默认按距离排序）
    """
    if keywords:
        return await amap_service.search_by_keyword(
            location=location,
            keywords=keywords,
            radius=radius,
            page_size=page_size,
            enable_filter=enable_filter,
            sort_by_distance=sort_by_distance
        )
    else:
        response = await amap_service.search_around(
            location=location,
            radius=radius,
            page_size=page_size
        )
        if response.is_success:
            # 对无关键词搜索结果也进行距离排序（如果启用）
            pois = response.pois
            if sort_by_distance:
                pois = amap_service._sort_pois_by_distance(pois)
            return pois
        else:
            return [] 