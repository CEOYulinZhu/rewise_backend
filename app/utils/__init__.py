"""
工具模块

包含各种辅助工具和通用功能
"""

from .distance_utils import (
    haversine_distance,
    calculate_distance_from_location,
    parse_location_string,
    format_distance
)

from .poi_filter import (
    POIFilter,
    filter_recycling_pois,
    get_recycling_keywords,
    is_valid_recycling_keyword
)

from .vivo_auth import gen_sign_headers

# 新增：分析结果合并器
from .analysis_merger import AnalysisMerger

__all__ = [
    # 距离工具
    "haversine_distance",
    "calculate_distance_from_location", 
    "parse_location_string",
    "format_distance",
    
    # POI过滤器
    "POIFilter",
    "filter_recycling_pois",
    "get_recycling_keywords",
    "is_valid_recycling_keyword",
    
    # VIVO认证
    "gen_sign_headers",
    
    # 分析合并器
    "AnalysisMerger"
] 