"""
图片代理工具类测试
"""

import pytest
from app.utils.image_proxy import ImageProxyService, image_proxy


class TestImageProxyService:
    """图片代理服务测试"""
    
    def setup_method(self):
        """测试前置设置"""
        self.proxy_service = ImageProxyService()
    
    def test_detect_platform_bilibili(self):
        """测试B站平台检测"""
        urls = [
            "https://i0.hdslb.com/bfs/archive/test.jpg",
            "https://i1.hdslb.com/bfs/archive/test.jpg", 
            "https://bilibili.com/test.jpg",
            "//i0.hdslb.com/bfs/archive/test.jpg"
        ]
        
        for url in urls:
            platform = self.proxy_service._detect_platform(url)
            assert platform == "bilibili", f"URL {url} should be detected as bilibili"
    
    def test_detect_platform_xianyu(self):
        """测试闲鱼平台检测"""
        urls = [
            "https://gw.alicdn.com/test.jpg",
            "https://img.alicdn.com/test.jpg",
            "https://taobao.com/test.jpg"
        ]
        
        for url in urls:
            platform = self.proxy_service._detect_platform(url)
            assert platform == "xianyu", f"URL {url} should be detected as xianyu"
    
    def test_detect_platform_unknown(self):
        """测试未知平台检测"""
        urls = [
            "https://example.com/test.jpg",
            "https://google.com/test.jpg",
            ""
        ]
        
        for url in urls:
            platform = self.proxy_service._detect_platform(url)
            assert platform == "unknown", f"URL {url} should be detected as unknown"
    
    def test_normalize_url(self):
        """测试URL标准化"""
        test_cases = [
            ("//i0.hdslb.com/test.jpg", "https://i0.hdslb.com/test.jpg"),
            ("i0.hdslb.com/test.jpg", "https://i0.hdslb.com/test.jpg"),
            ("https://i0.hdslb.com/test.jpg", "https://i0.hdslb.com/test.jpg"),
            ("", "")
        ]
        
        for input_url, expected in test_cases:
            result = self.proxy_service._normalize_url(input_url)
            assert result == expected, f"URL {input_url} should normalize to {expected}, got {result}"
    
    def test_proxy_bilibili_cover(self):
        """测试B站封面代理"""
        # 测试正常URL
        input_url = "https://i2.hdslb.com/bfs/archive/test.jpg"
        result = self.proxy_service.proxy_bilibili_cover(input_url)
        
        # 验证结果包含本地代理URL
        assert self.proxy_service.local_proxy_url in result
        assert "platform=bilibili" in result
        
        # 测试相对路径URL
        input_url = "//i2.hdslb.com/bfs/archive/test.jpg"
        result = self.proxy_service.proxy_bilibili_cover(input_url)
        assert self.proxy_service.local_proxy_url in result
        
        # 测试已经是代理URL的情况
        proxy_url = f"{self.proxy_service.local_proxy_url}?url=test&platform=bilibili"
        result = self.proxy_service.proxy_bilibili_cover(proxy_url)
        assert result == proxy_url  # 应该保持不变
        
        # 测试空URL
        result = self.proxy_service.proxy_bilibili_cover("")
        assert result == ""
    
    def test_proxy_image_url(self):
        """测试通用图片URL代理"""
        # B站URL
        bilibili_url = "https://i2.hdslb.com/bfs/archive/test.jpg"
        result = self.proxy_service.proxy_image_url(bilibili_url)
        assert self.proxy_service.local_proxy_url in result
        assert "platform=bilibili" in result
        
        # 闲鱼URL
        xianyu_url = "https://gw.alicdn.com/test.jpg"
        result = self.proxy_service.proxy_image_url(xianyu_url)
        assert self.proxy_service.local_proxy_url in result
        assert "platform=xianyu" in result
        
        # 未知平台URL（保持原样）
        unknown_url = "https://example.com/test.jpg"
        result = self.proxy_service.proxy_image_url(unknown_url)
        assert result == unknown_url
    
    def test_batch_proxy_urls(self):
        """测试批量代理URL"""
        urls = [
            "https://i2.hdslb.com/bfs/archive/test1.jpg",
            "https://i1.hdslb.com/bfs/archive/test2.jpg",
            "https://gw.alicdn.com/test3.jpg"
        ]
        
        result = self.proxy_service.batch_proxy_urls(urls)
        
        # 验证所有URL都被代理
        assert len(result) == 3
        assert all(self.proxy_service.local_proxy_url in url for url in result[:2])  # B站URL
        assert self.proxy_service.local_proxy_url in result[2]  # 闲鱼URL
    
    def test_get_proxy_info(self):
        """测试获取代理信息"""
        url = "https://i2.hdslb.com/bfs/archive/test.jpg"
        info = self.proxy_service.get_proxy_info(url)
        
        assert info["original_url"] == url
        assert self.proxy_service.local_proxy_url in info["proxy_url"]
        assert info["platform"] == "bilibili"
        assert info["is_proxied"] is True
    
    def test_global_instance(self):
        """测试全局实例"""
        # 测试全局实例可用
        assert image_proxy is not None
        assert isinstance(image_proxy, ImageProxyService)
        
        # 测试全局实例功能
        url = "https://i2.hdslb.com/bfs/archive/test.jpg"
        result = image_proxy.proxy_bilibili_cover(url)
        assert image_proxy.local_proxy_url in result


if __name__ == "__main__":
    pytest.main([__file__]) 