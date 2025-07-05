"""
图片反向代理工具类

提供图片URL代理功能，解决跨域访问问题
"""

import base64
from typing import Optional, Dict, Any

from app.core.logger import app_logger


class ImageProxyService:
    """图片反向代理服务"""
    
    def __init__(self, local_server_host: str = "127.0.0.1", local_server_port: int = 8000):
        # 本地服务器配置
        self.local_server_host = local_server_host
        self.local_server_port = local_server_port
        self.local_proxy_url = f"http://{local_server_host}:{local_server_port}/api/v1/proxy/image"
        
        # B站图片代理域名配置（用于检测）
        self.bilibili_proxy_domains = [
            "i0.hdslb.com",
            "i1.hdslb.com", 
            "i2.hdslb.com"
        ]
        
        # 平台配置
        self.proxy_config = {
            "bilibili": {
                "domains": ["hdslb.com", "bilibili.com"],
                "use_local_proxy": True
            },
            "xianyu": {
                "domains": ["alicdn.com", "taobao.com"],
                "use_local_proxy": True
            }
        }
    
    def _detect_platform(self, image_url: str) -> str:
        """
        检测图片URL所属平台
        
        Args:
            image_url: 图片URL
            
        Returns:
            平台名称（bilibili, xianyu, unknown）
        """
        if not image_url:
            return "unknown"
            
        # B站图片特征
        if any(domain in image_url for domain in ["hdslb.com", "bilibili.com"]):
            return "bilibili"
        
        # 闲鱼图片特征
        if any(domain in image_url for domain in ["alicdn.com", "taobao.com"]):
            return "xianyu"
            
        return "unknown"
    
    def _normalize_url(self, url: str) -> str:
        """
        标准化URL格式
        
        Args:
            url: 原始URL
            
        Returns:
            标准化后的URL
        """
        if not url:
            return ""
            
        # 补充协议
        if url.startswith('//'):
            url = 'https:' + url
        elif not url.startswith(('http://', 'https://')):
            url = 'https://' + url
            
        return url
    
    def _build_proxy_url(self, original_url: str, platform: str) -> str:
        """
        构建代理URL
        
        Args:
            original_url: 原始图片URL
            platform: 平台名称
            
        Returns:
            代理后的URL
        """
        if platform not in self.proxy_config:
            return original_url
            
        config = self.proxy_config[platform]
        
        # 使用本地服务器代理
        if config.get("use_local_proxy", False):
            # 将原始URL作为参数传递给本地代理服务
            encoded_url = base64.urlsafe_b64encode(original_url.encode()).decode()
            proxy_url = f"{self.local_proxy_url}?url={encoded_url}&platform={platform}"
            return proxy_url
            
        return original_url
    
    def proxy_image_url(self, image_url: str, force_proxy: bool = False) -> str:
        """
        代理图片URL
        
        Args:
            image_url: 原始图片URL
            force_proxy: 是否强制使用代理
            
        Returns:
            代理后的图片URL
        """
        if not image_url:
            return ""
            
        try:
            # 标准化URL
            normalized_url = self._normalize_url(image_url)
            
            # 检测平台
            platform = self._detect_platform(normalized_url)
            
            # 如果已经是本地代理URL，直接返回
            if self.local_proxy_url in normalized_url:
                return normalized_url
            
            # 构建代理URL
            if platform != "unknown" or force_proxy:
                proxy_url = self._build_proxy_url(normalized_url, platform)
                app_logger.debug(f"图片URL代理: {image_url} -> {proxy_url}")
                return proxy_url
            
            return normalized_url
            
        except Exception as e:
            app_logger.error(f"图片URL代理失败: {e}, url: {image_url}")
            return image_url
    
    def proxy_bilibili_cover(self, cover_url: str) -> str:
        """
        专门用于B站封面图片的代理
        
        Args:
            cover_url: B站封面URL
            
        Returns:
            代理后的封面URL
        """
        if not cover_url:
            return ""
            
        # 标准化URL
        normalized_url = self._normalize_url(cover_url)
        
        # 检查是否已经是本地代理URL
        if self.local_proxy_url in normalized_url:
            return normalized_url
        
        # 使用本地服务器代理
        encoded_url = base64.urlsafe_b64encode(normalized_url.encode()).decode()
        proxy_url = f"{self.local_proxy_url}?url={encoded_url}&platform=bilibili"
        
        app_logger.debug(f"B站封面代理: {cover_url} -> {proxy_url}")
        return proxy_url
    
    def batch_proxy_urls(self, urls: list[str], platform: Optional[str] = None) -> list[str]:
        """
        批量代理图片URL
        
        Args:
            urls: 图片URL列表
            platform: 指定平台（可选）
            
        Returns:
            代理后的URL列表
        """
        if not urls:
            return []
            
        proxied_urls = []
        for url in urls:
            if platform:
                # 指定平台
                proxied_url = self._build_proxy_url(self._normalize_url(url), platform)
            else:
                # 自动检测平台
                proxied_url = self.proxy_image_url(url)
            proxied_urls.append(proxied_url)
            
        return proxied_urls
    
    def get_proxy_info(self, image_url: str) -> Dict[str, Any]:
        """
        获取图片代理信息
        
        Args:
            image_url: 图片URL
            
        Returns:
            包含代理信息的字典
        """
        if not image_url:
            return {
                "original_url": "",
                "proxy_url": "",
                "platform": "unknown",
                "is_proxied": False
            }
            
        normalized_url = self._normalize_url(image_url)
        platform = self._detect_platform(normalized_url)
        proxy_url = self.proxy_image_url(image_url)
        
        return {
            "original_url": image_url,
            "proxy_url": proxy_url,
            "platform": platform,
            "is_proxied": proxy_url != normalized_url
        }


# 创建全局实例
# 可以通过环境变量或配置文件来设置本地服务器地址
image_proxy = ImageProxyService() 