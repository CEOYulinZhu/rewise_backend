"""
地理距离计算工具测试

测试距离计算相关的工具函数
"""

import pytest
import math

from app.utils.distance_utils import (
    haversine_distance,
    parse_location_string,
    calculate_distance_from_location,
    format_distance
)


class TestDistanceUtils:
    """距离计算工具测试类"""

    def test_haversine_distance_zero(self):
        """测试同一点的距离为0"""
        distance = haversine_distance(39.9042, 116.4074, 39.9042, 116.4074)
        assert distance == 0.0

    def test_haversine_distance_known_points(self):
        """测试已知点之间的距离"""
        # 北京天安门到上海外滩的大致距离约1067公里
        beijing_lat, beijing_lon = 39.9042, 116.4074  # 北京天安门
        shanghai_lat, shanghai_lon = 31.2304, 121.4737  # 上海外滩
        
        distance = haversine_distance(beijing_lat, beijing_lon, shanghai_lat, shanghai_lon)
        
        # 允许5%的误差范围
        expected_distance = 1067000  # 1067公里转米
        assert abs(distance - expected_distance) / expected_distance < 0.05

    def test_haversine_distance_short_distance(self):
        """测试短距离计算"""
        # 测试广州两个相近点之间的距离
        lat1, lon1 = 23.133827, 113.365382
        lat2, lon2 = 23.134827, 113.366382  # 大约110米的距离
        
        distance = haversine_distance(lat1, lon1, lat2, lon2)
        
        # 预期距离约为150米左右（两个维度各移动约0.001度）
        assert 100 < distance < 200

    def test_parse_location_string_valid(self):
        """测试有效的位置字符串解析"""
        test_cases = [
            ("113.365382,23.133827", (113.365382, 23.133827)),
            ("116.4074,39.9042", (116.4074, 39.9042)),
            (" 121.4737 , 31.2304 ", (121.4737, 31.2304)),  # 带空格
            ("-74.0060,40.7128", (-74.0060, 40.7128)),  # 负数
        ]
        
        for location_str, expected in test_cases:
            lon, lat = parse_location_string(location_str)
            assert abs(lon - expected[0]) < 1e-6
            assert abs(lat - expected[1]) < 1e-6

    def test_parse_location_string_invalid(self):
        """测试无效的位置字符串解析"""
        invalid_cases = [
            "",  # 空字符串
            "113.365382",  # 只有一个数字
            "113.365382,23.133827,100",  # 三个数字
            "abc,123",  # 包含非数字
            "113.365382,abc",  # 部分非数字
            "200,23.133827",  # 经度超出范围
            "113.365382,100",  # 纬度超出范围
        ]
        
        for invalid_location in invalid_cases:
            with pytest.raises(ValueError):
                parse_location_string(invalid_location)

    def test_calculate_distance_from_location(self):
        """测试从位置字符串计算距离"""
        user_location = "113.365382,23.133827"
        target_location = "113.366382,23.134827"
        
        distance = calculate_distance_from_location(user_location, target_location)
        
        # 应该是一个合理的短距离
        assert 100 < distance < 200

    def test_calculate_distance_from_location_same_point(self):
        """测试同一点的距离"""
        location = "113.365382,23.133827"
        
        distance = calculate_distance_from_location(location, location)
        assert distance == 0.0

    def test_format_distance_meters(self):
        """测试米为单位的距离格式化"""
        test_cases = [
            (0, "0米"),
            (50, "50米"),
            (150, "150米"),
            (999, "999米"),
        ]
        
        for distance, expected in test_cases:
            assert format_distance(distance) == expected

    def test_format_distance_kilometers(self):
        """测试公里为单位的距离格式化"""
        test_cases = [
            (1000, "1.0公里"),
            (1500, "1.5公里"),
            (2800, "2.8公里"),
            (9900, "9.9公里"),
            (10000, "10公里"),
            (25000, "25公里"),
            (100000, "100公里"),
        ]
        
        for distance, expected in test_cases:
            assert format_distance(distance) == expected

    def test_integration_distance_calculation(self):
        """集成测试：完整的距离计算流程"""
        # 使用真实的广州坐标
        user_location = "113.365382,23.133827"  # 用户位置
        poi_locations = [
            "113.366382,23.134827",  # 约150米
            "113.370000,23.140000",  # 约1公里
            "113.400000,23.160000",  # 约5公里
        ]
        
        distances = []
        for poi_location in poi_locations:
            distance = calculate_distance_from_location(user_location, poi_location)
            formatted = format_distance(distance)
            distances.append((distance, formatted))
        
        # 验证距离递增
        assert distances[0][0] < distances[1][0] < distances[2][0]
        
        # 验证格式化结果
        assert "米" in distances[0][1]  # 第一个应该是米
        assert "公里" in distances[1][1]  # 后两个应该是公里
        assert "公里" in distances[2][1] 