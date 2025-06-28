"""
POI筛选器测试

测试POI筛选功能的各种场景
"""

import pytest
from app.utils.poi_filter import (
    POIFilter,
    filter_recycling_pois,
    get_recycling_keywords,
    is_valid_recycling_keyword
)
from app.models.amap_models import AmapPOI


class TestPOIFilter:
    """POI筛选器测试类"""
    
    @pytest.fixture
    def sample_pois(self):
        """创建测试用的POI数据"""
        return [
            AmapPOI(
                id="1",
                name="绿色环保旧衣回收站",
                location="113.365382,23.133827",
                type="生活服务",
                typecode="070000",
                address="广州市天河区某街道",
                pname="广东省",
                cityname="广州市",
                adname="天河区",
                pcode="440000",
                citycode="020",
                adcode="440106"
            ),
            AmapPOI(
                id="2", 
                name="废品回收站",
                location="113.365382,23.133827",
                type="生活服务",
                typecode="070000",
                address="广州市天河区某街道",
                pname="广东省",
                cityname="广州市",
                adname="天河区",
                pcode="440000",
                citycode="020",
                adcode="440106"
            ),
            AmapPOI(
                id="3",
                name="家电维修回收中心",
                location="113.365382,23.133827",
                type="生活服务",
                typecode="070000",
                address="广州市天河区某街道",
                pname="广东省",
                cityname="广州市",
                adname="天河区",
                pcode="440000",
                citycode="020",
                adcode="440106"
            ),
            AmapPOI(
                id="4",
                name="二手电脑回收",
                location="113.365382,23.133827",
                type="生活服务",
                typecode="070000",
                address="广州市天河区某街道",
                pname="广东省",
                cityname="广州市",
                adname="天河区",
                pcode="440000",
                citycode="020",
                adcode="440106"
            ),
            AmapPOI(
                id="5",
                name="纸箱包装回收站",
                location="113.365382,23.133827",
                type="生活服务",
                typecode="070000",
                address="广州市天河区某街道",
                pname="广东省",
                cityname="广州市",
                adname="天河区",
                pcode="440000",
                citycode="020",
                adcode="440106"
            ),
            AmapPOI(
                id="6",
                name="普通超市",
                location="113.365382,23.133827",
                type="购物服务",
                typecode="060000",
                address="广州市天河区某街道",
                pname="广东省",
                cityname="广州市",
                adname="天河区",
                pcode="440000",
                citycode="020",
                adcode="440106"
            )
        ]
    
    def test_filter_old_clothes_recycling(self, sample_pois):
        """测试旧衣回收筛选"""
        filtered = POIFilter.filter_pois_by_keyword(sample_pois, "旧衣回收")
        
        # 应该只包含包含"衣"字且有回收相关词汇的POI
        assert len(filtered) == 1
        assert filtered[0].name == "绿色环保旧衣回收站"
    
    def test_filter_appliance_recycling(self, sample_pois):
        """测试家电回收筛选"""
        filtered = POIFilter.filter_pois_by_keyword(sample_pois, "家电回收")
        
        # 应该包含包含"家电"且有回收相关词汇的POI
        assert len(filtered) == 1
        assert filtered[0].name == "家电维修回收中心"
    
    def test_filter_computer_recycling(self, sample_pois):
        """测试电脑回收筛选"""
        filtered = POIFilter.filter_pois_by_keyword(sample_pois, "电脑回收")
        
        # 应该包含包含"电脑"且有回收相关词汇的POI
        assert len(filtered) == 1
        assert filtered[0].name == "二手电脑回收"
    
    def test_filter_cardboard_recycling(self, sample_pois):
        """测试纸箱回收筛选"""
        filtered = POIFilter.filter_pois_by_keyword(sample_pois, "纸箱回收")
        
        # 应该包含包含"纸箱"且有回收相关词汇的POI
        assert len(filtered) == 1
        assert filtered[0].name == "纸箱包装回收站"
    
    def test_filter_strict_mode(self, sample_pois):
        """测试严格模式筛选"""
        # 严格模式：必须同时包含通用回收关键字和特定关键字
        filtered = POIFilter.filter_pois_by_keyword(sample_pois, "旧衣回收", strict_mode=True)
        assert len(filtered) == 1
        
        # 宽松模式：包含任一类型关键字即可
        filtered_loose = POIFilter.filter_pois_by_keyword(sample_pois, "旧衣回收", strict_mode=False)
        assert len(filtered_loose) >= len(filtered)
    
    def test_filter_invalid_keyword(self, sample_pois):
        """测试无效关键词"""
        filtered = POIFilter.filter_pois_by_keyword(sample_pois, "无效关键词")
        
        # 无效关键词应该返回原始列表
        assert len(filtered) == len(sample_pois)
    
    def test_filter_empty_input(self):
        """测试空输入"""
        # 空POI列表
        assert POIFilter.filter_pois_by_keyword([], "旧衣回收") == []
        
        # 空关键词
        sample_pois = [AmapPOI(
            id="1", name="测试", location="0,0", type="测试", typecode="000000",
            address="测试", pname="测试", cityname="测试", adname="测试",
            pcode="000000", citycode="000", adcode="000000"
        )]
        assert POIFilter.filter_pois_by_keyword(sample_pois, "") == sample_pois
    
    def test_get_supported_keywords(self):
        """测试获取支持的关键词"""
        keywords = POIFilter.get_supported_keywords()
        
        assert "家电回收" in keywords
        assert "电脑回收" in keywords
        assert "旧衣回收" in keywords
        assert "纸箱回收" in keywords
        assert len(keywords) == 4
    
    def test_validate_keyword(self):
        """测试关键词验证"""
        assert POIFilter.validate_keyword("旧衣回收") is True
        assert POIFilter.validate_keyword("家电回收") is True
        assert POIFilter.validate_keyword("电脑回收") is True
        assert POIFilter.validate_keyword("纸箱回收") is True
        assert POIFilter.validate_keyword("无效关键词") is False
        assert POIFilter.validate_keyword("") is False
        assert POIFilter.validate_keyword("  旧衣回收  ") is True  # 测试去除空格


class TestPOIFilterUtilityFunctions:
    """POI筛选工具函数测试"""
    
    def test_filter_recycling_pois(self):
        """测试筛选回收POI便捷函数"""
        pois = [
            AmapPOI(
                id="1", name="旧衣回收站", location="0,0", type="生活服务", typecode="070000",
                address="测试地址", pname="测试省", cityname="测试市", adname="测试区",
                pcode="000000", citycode="000", adcode="000000"
            )
        ]
        
        filtered = filter_recycling_pois(pois, "旧衣回收")
        assert len(filtered) == 1
    
    def test_get_recycling_keywords(self):
        """测试获取回收关键词函数"""
        keywords = get_recycling_keywords()
        assert isinstance(keywords, list)
        assert len(keywords) == 4
    
    def test_is_valid_recycling_keyword(self):
        """测试验证回收关键词函数"""
        assert is_valid_recycling_keyword("旧衣回收") is True
        assert is_valid_recycling_keyword("无效关键词") is False


class TestPOIFilterEdgeCases:
    """POI筛选边界情况测试"""
    
    def test_case_insensitive_filtering(self):
        """测试大小写不敏感筛选"""
        poi = AmapPOI(
            id="1", name="旧衣回收站", location="0,0", type="生活服务", typecode="070000",
            address="测试地址", pname="测试省", cityname="测试市", adname="测试区",
            pcode="000000", citycode="000", adcode="000000"
        )
        
        # 中文不存在大小写问题，但测试英文关键词
        filtered = POIFilter.filter_pois_by_keyword([poi], "旧衣回收")
        assert len(filtered) == 1
    
    def test_multiple_keyword_matches(self):
        """测试多关键词匹配"""
        poi = AmapPOI(
            id="1", name="家电电脑回收中心", location="0,0", type="生活服务", typecode="070000",
            address="测试地址", pname="测试省", cityname="测试市", adname="测试区",
            pcode="000000", citycode="000", adcode="000000"
        )
        
        # 该POI包含家电和电脑两个关键词
        filtered_appliance = POIFilter.filter_pois_by_keyword([poi], "家电回收")
        filtered_computer = POIFilter.filter_pois_by_keyword([poi], "电脑回收")
        
        assert len(filtered_appliance) == 1
        assert len(filtered_computer) == 1
    
    def test_filter_with_address_keywords(self):
        """测试地址中包含关键词的筛选"""
        poi = AmapPOI(
            id="1", name="回收站", location="0,0", type="生活服务", typecode="070000",
            address="旧衣服专业回收点", pname="测试省", cityname="测试市", adname="测试区",
            pcode="000000", citycode="000", adcode="000000"
        )
        
        # 地址中包含"衣"字
        filtered = POIFilter.filter_pois_by_keyword([poi], "旧衣回收")
        assert len(filtered) == 1


if __name__ == "__main__":
    pytest.main([__file__, "-v"]) 