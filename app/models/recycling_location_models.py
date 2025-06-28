"""
回收地点推荐数据模型

定义回收地点推荐Agent返回的结构化数据模型
"""

from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any

from app.models.amap_models import AmapPOI


@dataclass
class RecyclingLocationResponse:
    """回收地点推荐完整响应数据模型"""
    success: bool                           # 操作是否成功
    recycling_type: Optional[str] = None    # 分析得出的回收类型
    locations: List[AmapPOI] = field(default_factory=list)  # 推荐的回收地点列表
    analysis_result: Optional[Dict[str, Any]] = None        # 输入的分析结果
    search_params: Optional[Dict[str, Any]] = None          # 搜索参数
    error: Optional[str] = None             # 错误信息（失败时）
    raw_ai_response: Optional[str] = None   # 原始AI响应（调试用）
    
    def __post_init__(self):
        """数据验证"""
        if self.success and not self.recycling_type:
            raise ValueError("成功响应必须包含回收类型")
        
        if self.recycling_type:
            valid_types = ["家电回收", "电脑回收", "旧衣回收", "纸箱回收"]
            if self.recycling_type not in valid_types:
                raise ValueError(f"回收类型必须是以下之一: {valid_types}，当前值: {self.recycling_type}")
        
        if not isinstance(self.locations, list):
            raise ValueError("locations必须是列表类型")
    
    def get_nearby_locations(self, max_distance_meters: int = 10000) -> List[AmapPOI]:
        """获取指定距离内的回收地点
        
        Args:
            max_distance_meters: 最大距离（米），默认10公里
            
        Returns:
            距离内的回收地点列表
        """
        if not self.locations:
            return []
        
        nearby_locations = []
        for location in self.locations:
            if location.distance_meters is not None:
                if location.distance_meters <= max_distance_meters:
                    nearby_locations.append(location)
            else:
                # 如果没有距离信息，默认包含
                nearby_locations.append(location)
        
        return nearby_locations
    
    def get_locations_by_distance_range(
        self, 
        min_distance_meters: int = 0, 
        max_distance_meters: int = 50000
    ) -> List[AmapPOI]:
        """获取指定距离范围内的回收地点
        
        Args:
            min_distance_meters: 最小距离（米），默认0
            max_distance_meters: 最大距离（米），默认50公里
            
        Returns:
            距离范围内的回收地点列表
        """
        if not self.locations:
            return []
        
        filtered_locations = []
        for location in self.locations:
            if location.distance_meters is not None:
                if min_distance_meters <= location.distance_meters <= max_distance_meters:
                    filtered_locations.append(location)
            else:
                # 如果没有距离信息，默认包含
                filtered_locations.append(location)
        
        return filtered_locations
    
    def get_top_locations(self, limit: int = 10) -> List[AmapPOI]:
        """获取最近的N个回收地点
        
        Args:
            limit: 返回的最大数量，默认10个
            
        Returns:
            最近的回收地点列表（按距离排序）
        """
        if not self.locations:
            return []
        
        # 过滤有距离信息的地点并排序
        locations_with_distance = [
            loc for loc in self.locations 
            if loc.distance_meters is not None
        ]
        locations_without_distance = [
            loc for loc in self.locations 
            if loc.distance_meters is None
        ]
        
        # 按距离排序
        locations_with_distance.sort(key=lambda x: x.distance_meters)
        
        # 合并结果，有距离信息的在前
        result = locations_with_distance[:limit]
        if len(result) < limit:
            remaining = limit - len(result)
            result.extend(locations_without_distance[:remaining])
        
        return result
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式（用于JSON序列化）"""
        result = {
            "success": self.success,
            "recycling_type": self.recycling_type,
            "locations_count": len(self.locations),
            "error": self.error
        }
        
        # 转换地点列表
        if self.locations:
            result["locations"] = [location.to_dict() for location in self.locations]
        
        if self.analysis_result:
            result["analysis_result"] = self.analysis_result
        
        if self.search_params:
            result["search_params"] = self.search_params
        
        if self.raw_ai_response:
            result["raw_ai_response"] = self.raw_ai_response
        
        return result


class RecyclingLocationDataConverter:
    """回收地点推荐数据转换器 - 将原始数据转换为结构化模型"""
    
    @staticmethod
    def create_response(
        success: bool,
        recycling_type: Optional[str] = None,
        locations: Optional[List[AmapPOI]] = None,
        analysis_result: Optional[Dict[str, Any]] = None,
        search_params: Optional[Dict[str, Any]] = None,
        error: Optional[str] = None,
        raw_ai_response: Optional[str] = None
    ) -> RecyclingLocationResponse:
        """创建回收地点推荐响应对象
        
        Args:
            success: 操作是否成功
            recycling_type: 分析得出的回收类型
            locations: 推荐的回收地点列表
            analysis_result: 输入的分析结果
            search_params: 搜索参数
            error: 错误信息
            raw_ai_response: 原始AI响应
            
        Returns:
            RecyclingLocationResponse对象
        """
        return RecyclingLocationResponse(
            success=success,
            recycling_type=recycling_type,
            locations=locations or [],
            analysis_result=analysis_result,
            search_params=search_params,
            error=error,
            raw_ai_response=raw_ai_response
        ) 