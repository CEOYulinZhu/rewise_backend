"""
地理距离计算工具

提供经纬度坐标间距离计算的工具函数
"""

import math
from typing import Tuple


def haversine_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """
    使用 Haversine 公式计算两个经纬度坐标间的球面距离
    
    Args:
        lat1: 第一个点的纬度
        lon1: 第一个点的经度  
        lat2: 第二个点的纬度
        lon2: 第二个点的经度
    
    Returns:
        float: 距离（米）
    """
    # 地球半径（米）
    R = 6371000
    
    # 将度数转换为弧度
    lat1_rad = math.radians(lat1)
    lat2_rad = math.radians(lat2)
    delta_lat = math.radians(lat2 - lat1)
    delta_lon = math.radians(lon2 - lon1)
    
    # Haversine 公式
    a = (math.sin(delta_lat / 2) ** 2 + 
         math.cos(lat1_rad) * math.cos(lat2_rad) * 
         math.sin(delta_lon / 2) ** 2)
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    
    # 距离（米）
    distance = R * c
    return distance


def parse_location_string(location: str) -> Tuple[float, float]:
    """
    解析位置字符串，返回经纬度坐标
    
    Args:
        location: 位置字符串，格式为"经度,纬度"
    
    Returns:
        Tuple[float, float]: (经度, 纬度)
    
    Raises:
        ValueError: 位置字符串格式错误
    """
    try:
        parts = location.strip().split(',')
        if len(parts) != 2:
            raise ValueError(f"位置字符串格式错误，期望'经度,纬度'，实际得到: {location}")
        
        longitude = float(parts[0].strip())
        latitude = float(parts[1].strip())
        
        # 验证经纬度范围
        if not (-180 <= longitude <= 180):
            raise ValueError(f"经度超出有效范围[-180, 180]: {longitude}")
        if not (-90 <= latitude <= 90):
            raise ValueError(f"纬度超出有效范围[-90, 90]: {latitude}")
        
        return longitude, latitude
        
    except ValueError as e:
        if "could not convert" in str(e):
            raise ValueError(f"位置字符串包含无效数字: {location}")
        raise


def calculate_distance_from_location(
    user_location: str, 
    target_location: str
) -> float:
    """
    计算用户位置到目标位置的距离
    
    Args:
        user_location: 用户位置，格式为"经度,纬度"
        target_location: 目标位置，格式为"经度,纬度"
    
    Returns:
        float: 距离（米）
    
    Raises:
        ValueError: 位置字符串格式错误
    """
    user_lon, user_lat = parse_location_string(user_location)
    target_lon, target_lat = parse_location_string(target_location)
    
    return haversine_distance(user_lat, user_lon, target_lat, target_lon)


def format_distance(distance_meters: float) -> str:
    """
    格式化距离显示
    
    Args:
        distance_meters: 距离（米）
    
    Returns:
        str: 格式化的距离字符串
    """
    if distance_meters < 1000:
        return f"{distance_meters:.0f}米"
    else:
        distance_km = distance_meters / 1000
        if distance_km < 10:
            return f"{distance_km:.1f}公里"
        else:
            return f"{distance_km:.0f}公里" 