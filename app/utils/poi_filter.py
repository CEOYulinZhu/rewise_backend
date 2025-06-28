"""
POI搜索结果筛选工具

提供基于关键词的POI筛选功能，确保搜索结果的准确性
"""

from typing import List, Dict, Set
from app.core.logger import app_logger
from app.models.amap_models import AmapPOI


class POIFilter:
    """POI筛选器类"""
    
    # 定义支持的回收类型和对应的关键字
    RECYCLING_KEYWORDS = {
        "家电回收": {"家电", "电器", "电机", "空调", "冰箱", "洗衣机", "电视", "微波炉", "热水器"},
        "电脑回收": {"电脑", "计算机", "笔记本", "台式机", "显示器", "主机", "服务器", "IT"},
        "旧衣回收": {"衣", "服装", "衣服", "衣物", "纺织", "布料", "棉衣", "外套", "裤子", "裙子"},
        "纸箱回收": {"纸", "纸箱", "纸盒", "纸板", "包装", "瓦楞", "纸制品", "硬纸板"}
    }
    
    # 通用回收关键字（适用于所有类型）
    GENERAL_RECYCLING_KEYWORDS = {
        "回收", "收购", "废品", "再生", "循环", "环保", "废旧", "二手", "处理", "利用"
    }
    
    @classmethod
    def filter_pois_by_keyword(
        cls, 
        pois: List[AmapPOI], 
        search_keyword: str,
        strict_mode: bool = True
    ) -> List[AmapPOI]:
        """
        根据搜索关键词筛选POI列表
        
        Args:
            pois: 原始POI列表
            search_keyword: 搜索关键词（如"旧衣回收"）
            strict_mode: 严格模式，为True时必须包含特定关键字
        
        Returns:
            List[AmapPOI]: 筛选后的POI列表
        """
        if not pois or not search_keyword:
            return pois
        
        search_keyword = search_keyword.strip()
        
        # 获取对应的关键字集合
        target_keywords = cls.RECYCLING_KEYWORDS.get(search_keyword, set())
        
        if not target_keywords:
            app_logger.warning(f"未找到关键词'{search_keyword}'对应的筛选规则，返回原始结果")
            return pois
        
        filtered_pois = []
        
        for poi in pois:
            if cls._is_poi_relevant(poi, target_keywords, strict_mode):
                filtered_pois.append(poi)
                app_logger.debug(f"POI '{poi.name}' 通过筛选")
            else:
                app_logger.debug(f"POI '{poi.name}' 被筛选掉")
        
        app_logger.info(f"关键词'{search_keyword}'筛选: {len(pois)} -> {len(filtered_pois)}")
        return filtered_pois
    
    @classmethod
    def _is_poi_relevant(
        cls, 
        poi: AmapPOI, 
        target_keywords: Set[str], 
        strict_mode: bool
    ) -> bool:
        """
        判断POI是否与目标关键词相关
        
        Args:
            poi: POI对象
            target_keywords: 目标关键字集合
            strict_mode: 严格模式
        
        Returns:
            bool: 是否相关
        """
        # 构建搜索文本（名称 + 地址 + 类型）
        search_text = f"{poi.name} {poi.address} {poi.type}".lower()
        
        # 检查是否包含通用回收关键字
        has_general_recycling = any(
            keyword in search_text 
            for keyword in cls.GENERAL_RECYCLING_KEYWORDS
        )
        
        # 检查是否包含特定关键字
        has_specific_keyword = any(
            keyword in search_text 
            for keyword in target_keywords
        )
        
        if strict_mode:
            # 严格模式：必须同时包含通用回收关键字和特定关键字
            return has_general_recycling and has_specific_keyword
        else:
            # 宽松模式：包含任一类型关键字即可
            return has_general_recycling or has_specific_keyword
    
    @classmethod
    def get_supported_keywords(cls) -> List[str]:
        """获取支持的搜索关键词列表"""
        return list(cls.RECYCLING_KEYWORDS.keys())
    
    @classmethod
    def validate_keyword(cls, keyword: str) -> bool:
        """验证关键词是否支持"""
        return keyword.strip() in cls.RECYCLING_KEYWORDS


def filter_recycling_pois(
    pois: List[AmapPOI], 
    search_keyword: str,
    strict_mode: bool = True
) -> List[AmapPOI]:
    """
    筛选回收类POI的便捷函数
    
    Args:
        pois: POI列表
        search_keyword: 搜索关键词
        strict_mode: 是否使用严格模式
    
    Returns:
        List[AmapPOI]: 筛选后的POI列表
    """
    return POIFilter.filter_pois_by_keyword(pois, search_keyword, strict_mode)


def get_recycling_keywords() -> List[str]:
    """获取支持的回收关键词列表"""
    return POIFilter.get_supported_keywords()


def is_valid_recycling_keyword(keyword: str) -> bool:
    """检查是否为有效的回收关键词"""
    return POIFilter.validate_keyword(keyword) 