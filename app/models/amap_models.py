"""
高德地图API相关数据模型

包含POI信息、图片信息、搜索结果等数据结构
"""

from typing import List, Optional
from pydantic import BaseModel, Field


class AmapPhoto(BaseModel):
    """高德地图POI图片信息"""
    title: Optional[str] = Field(None, description="图片介绍")
    url: Optional[str] = Field(None, description="图片下载链接")


class AmapPOI(BaseModel):
    """高德地图POI基础信息"""
    id: str = Field(..., description="POI唯一标识")
    name: str = Field(..., description="POI名称")
    location: str = Field(..., description="POI经纬度，格式为'经度,纬度'")
    type: str = Field(..., description="POI所属类型")
    typecode: str = Field(..., description="POI分类编码")
    address: str = Field(..., description="POI详细地址")
    pname: str = Field(..., description="POI所属省份")
    cityname: str = Field(..., description="POI所属城市")
    adname: str = Field(..., description="POI所属区县")
    pcode: str = Field(..., description="POI所属省份编码")
    citycode: str = Field(..., description="POI所属城市编码")
    adcode: str = Field(..., description="POI所属区域编码")
    
    # 营业信息
    opentime_today: Optional[str] = Field(None, description="今日营业时间")
    opentime_week: Optional[str] = Field(None, description="营业时间描述")
    tel: Optional[str] = Field(None, description="联系电话")
    
    # 图片信息
    photos: Optional[List[AmapPhoto]] = Field(None, description="POI图片列表")
    
    # 距离信息
    distance_meters: Optional[float] = Field(None, description="与用户位置的距离（米）")
    distance_formatted: Optional[str] = Field(None, description="格式化的距离字符串")
    
    @property
    def latitude(self) -> float:
        """获取纬度"""
        try:
            return float(self.location.split(',')[1])
        except (IndexError, ValueError):
            return 0.0
    
    @property
    def longitude(self) -> float:
        """获取经度"""
        try:
            return float(self.location.split(',')[0])
        except (IndexError, ValueError):
            return 0.0
    
    def to_dict(self) -> dict:
        """转换为字典格式（用于JSON序列化）"""
        result = {
            "id": self.id,
            "name": self.name,
            "location": self.location,
            "type": self.type,
            "typecode": self.typecode,
            "address": self.address,
            "pname": self.pname,
            "cityname": self.cityname,
            "adname": self.adname,
            "pcode": self.pcode,
            "citycode": self.citycode,
            "adcode": self.adcode,
            "opentime_today": self.opentime_today,
            "opentime_week": self.opentime_week,
            "tel": self.tel,
            "distance_meters": self.distance_meters,
            "distance_formatted": self.distance_formatted
        }
        
        if self.photos:
            result["photos"] = [photo.dict() for photo in self.photos]
        
        return result


class AmapSearchResponse(BaseModel):
    """高德地图搜索响应"""
    status: str = Field(..., description="返回结果状态值，1表示成功，0表示失败")
    info: str = Field(..., description="返回状态说明")
    infocode: str = Field(..., description="返回状态码")
    count: str = Field(..., description="本次请求返回的POI实际个数")
    pois: List[AmapPOI] = Field(default_factory=list, description="POI信息列表")
    
    @property
    def is_success(self) -> bool:
        """判断请求是否成功"""
        return self.status == "1" and self.infocode == "10000"
    
    @property
    def poi_count(self) -> int:
        """获取POI数量"""
        try:
            return int(self.count)
        except ValueError:
            return 0


class AmapSearchRequest(BaseModel):
    """高德地图搜索请求参数"""
    location: str = Field(..., description="中心点坐标，格式为'经度,纬度'")
    keywords: Optional[str] = Field(None, description="搜索关键词")
    radius: int = Field(default=5000, description="搜索半径（米），范围0-50000")
    page_size: int = Field(default=10, description="每页记录数，范围1-25")
    page_num: int = Field(default=1, description="当前页数")
    show_fields: str = Field(
        default="business,photos", 
        description="返回结果控制，指定需要的字段"
    )
    
    def to_params_dict(self, api_key: str) -> dict:
        """转换为API请求参数字典"""
        params = {
            "key": api_key,
            "location": self.location,
            "radius": self.radius,
            "page_size": self.page_size,
            "page_num": self.page_num,
            "show_fields": self.show_fields,
            "output": "json"
        }
        
        if self.keywords:
            params["keywords"] = self.keywords
            
        return params 