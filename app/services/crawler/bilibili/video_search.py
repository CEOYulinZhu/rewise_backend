"""
哔哩哔哩视频搜索服务

提供基于关键词的视频搜索功能，返回格式化的视频信息
"""

import re
from dataclasses import dataclass
from typing import Dict, Any, Optional

from bilibili_api import search
from bilibili_api.search import SearchObjectType, OrderVideo
from loguru import logger


@dataclass
class VideoInfo:
    """视频信息数据类"""
    title: str                    # 视频标题
    play_count: int              # 播放量
    uploader_name: str           # UP主名称
    video_url: str               # 视频链接
    cover_url: str               # 封面链接
    danmaku_count: int           # 弹幕量
    duration: str                # 视频时长
    bvid: str                    # 视频BV号
    uploader_mid: int            # UP主ID
    pub_date: str                # 发布时间
    description: str             # 视频描述


class BilibiliVideoSearchService:
    """哔哩哔哩视频搜索服务"""
    
    def __init__(self):
        self.proxy_domain = "i0.hdslb.com"  # B站图片代理域名
    
    def _format_duration(self, duration_str: str) -> str:
        """
        格式化视频时长
        
        Args:
            duration_str: 原始时长字符串（如 "01:23" 或 "1:23:45"）
            
        Returns:
            格式化后的时长字符串
        """
        if not duration_str:
            return "00:00"
            
        # 移除可能的空格
        duration_str = duration_str.strip()
        
        # 如果已经是标准格式，直接返回
        if re.match(r'^\d{2}:\d{2}$', duration_str) or re.match(r'^\d{1,2}:\d{2}:\d{2}$', duration_str):
            return duration_str
            
        return duration_str
    
    def _format_play_count(self, play_count: Any) -> int:
        """
        格式化播放量
        
        Args:
            play_count: 播放量（可能是字符串或数字）
            
        Returns:
            格式化后的播放量数字
        """
        if isinstance(play_count, int):
            return play_count
            
        if isinstance(play_count, str):
            # 处理带单位的播放量（如 "1.2万", "100.5万"）
            play_str = play_count.replace(' ', '').lower()
            
            if '万' in play_str:
                num_str = play_str.replace('万', '')
                try:
                    return int(float(num_str) * 10000)
                except ValueError:
                    return 0
            elif '亿' in play_str:
                num_str = play_str.replace('亿', '')
                try:
                    return int(float(num_str) * 100000000)
                except ValueError:
                    return 0
            else:
                try:
                    return int(play_str)
                except ValueError:
                    return 0
        
        return 0
    
    def _process_cover_url(self, cover_url: str) -> str:
        """
        处理封面URL，使其可以在前端正常访问
        
        Args:
            cover_url: 原始封面URL
            
        Returns:
            处理后的封面URL
        """
        if not cover_url:
            return ""
            
        # 如果是相对路径，添加协议
        if cover_url.startswith('//'):
            cover_url = 'https:' + cover_url
        
        # 替换为代理域名以解决跨域问题
        if 'i0.hdslb.com' in cover_url or 'i1.hdslb.com' in cover_url or 'i2.hdslb.com' in cover_url:
            # 已经是代理域名，直接返回
            return cover_url
        
        # 替换原始域名为代理域名
        cover_url = re.sub(r'https?://[^/]+', f'https://{self.proxy_domain}', cover_url)
        
        return cover_url
    
    def _parse_video_item(self, item: Dict[str, Any]) -> Optional[VideoInfo]:
        """
        解析单个视频项数据
        
        Args:
            item: B站API返回的视频项数据
            
        Returns:
            解析后的视频信息对象，解析失败返回None
        """
        try:
            # 提取基本信息
            title = item.get('title', '').replace('<em class="keyword">', '').replace('</em>', '')
            bvid = item.get('bvid', '')
            
            # UP主信息
            uploader_name = item.get('author', '')
            uploader_mid = item.get('mid', 0)
            
            # 播放数据
            play_count = self._format_play_count(item.get('play', 0))
            danmaku_count = item.get('danmaku', 0)
            
            # 时长和发布时间
            duration = self._format_duration(item.get('duration', ''))
            pub_date = item.get('pubdate', '')
            
            # 描述
            description = item.get('description', '').replace('<em class="keyword">', '').replace('</em>', '')
            
            # 链接
            video_url = f"https://www.bilibili.com/video/{bvid}" if bvid else ""
            
            # 封面链接
            cover_url = self._process_cover_url(item.get('pic', ''))
            
            return VideoInfo(
                title=title,
                play_count=play_count,
                uploader_name=uploader_name,
                video_url=video_url,
                cover_url=cover_url,
                danmaku_count=danmaku_count,
                duration=duration,
                bvid=bvid,
                uploader_mid=uploader_mid,
                pub_date=pub_date,
                description=description
            )
            
        except Exception as e:
            logger.error(f"解析视频项失败: {e}, item: {item}")
            return None
    
    async def search_videos(
        self,
        keyword: str,
        page: int = 1,
        page_size: int = 20,
        order: OrderVideo = OrderVideo.TOTALRANK
    ) -> Dict[str, Any]:
        """
        搜索哔哩哔哩视频
        
        Args:
            keyword: 搜索关键词
            page: 页码，从1开始
            page_size: 每页数量，最大50
            order: 排序方式
            
        Returns:
            包含视频列表和统计信息的字典
        """
        if not keyword or not keyword.strip():
            return {
                "videos": [],
                "total": 0,
                "page": page,
                "page_size": page_size,
                "keyword": keyword,
                "error": "搜索关键词不能为空"
            }
        
        # 限制page_size
        page_size = min(page_size, 50)
        
        try:
            logger.info(f"开始搜索B站视频: keyword={keyword}, page={page}, page_size={page_size}")
            
            # 调用bilibili-api搜索（异步调用）
            result = await search.search_by_type(
                keyword=keyword.strip(),
                search_type=SearchObjectType.VIDEO,
                order_type=order,
                page=page,
                page_size=page_size
            )
            
            if not result:
                logger.warning(f"B站搜索返回数据为空: {result}")
                return {
                    "videos": [],
                    "total": 0,
                    "page": page,
                    "page_size": page_size,
                    "keyword": keyword,
                    "error": "搜索返回数据为空"
                }
            
            # 打印返回数据结构以便调试
            logger.info(f"B站API返回数据结构: {list(result.keys())}")
            
            # 直接从result中获取数据，不需要data包装
            video_items = result.get('result', [])
            
            # 解析视频信息
            videos = []
            for item in video_items:
                video_info = self._parse_video_item(item)
                if video_info:
                    videos.append(video_info)
            
            # 获取总数
            total = result.get('numResults', len(videos))
            
            logger.info(f"B站视频搜索完成: 找到{len(videos)}个视频, 总共{total}个结果")
            
            return {
                "videos": videos,
                "total": total,
                "page": page,
                "page_size": page_size,
                "keyword": keyword,
                "error": None
            }
            
        except Exception as e:
            logger.error(f"B站视频搜索失败: {e}")
            return {
                "videos": [],
                "total": 0,
                "page": page,
                "page_size": page_size,
                "keyword": keyword,
                "error": f"搜索失败: {str(e)}"
            } 