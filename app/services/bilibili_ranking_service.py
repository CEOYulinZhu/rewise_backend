"""
Bilibili视频排序服务

基于弹幕量和播放量对视频进行智能排序，选取最优质的视频推荐
"""

import math
from typing import Dict, List, Any, Optional
from dataclasses import dataclass

from app.core.logger import app_logger


@dataclass
class VideoData:
    """视频数据模型"""
    title: str
    uploader: str
    url: str
    cover_url: str
    play_count: int
    danmaku_count: int
    duration: str
    description: str
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'VideoData':
        """从字典创建VideoData实例"""
        return cls(
            title=data.get("title", ""),
            uploader=data.get("uploader", ""),
            url=data.get("url", ""),
            cover_url=data.get("cover_url", ""),
            play_count=data.get("play_count", 0),
            danmaku_count=data.get("danmaku_count", 0),
            duration=data.get("duration", ""),
            description=data.get("description", "")
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "title": self.title,
            "uploader": self.uploader,
            "url": self.url,
            "cover_url": self.cover_url,
            "play_count": self.play_count,
            "danmaku_count": self.danmaku_count,
            "duration": self.duration,
            "description": self.description
        }


@dataclass
class RankingConfig:
    """排序配置"""
    play_weight: float = 0.7  # 播放量权重
    danmaku_weight: float = 0.3  # 弹幕量权重
    top_count: int = 5  # 返回视频数量
    min_play_count: int = 1000  # 最小播放量阈值
    min_danmaku_count: int = 10  # 最小弹幕量阈值


class BilibiliRankingService:
    """Bilibili视频排序服务"""
    
    def __init__(self, config: Optional[RankingConfig] = None):
        """初始化排序服务
        
        Args:
            config: 排序配置，如果为None则使用默认配置
        """
        self.config = config or RankingConfig()
        app_logger.info(f"BilibiliRankingService初始化完成，配置: play_weight={self.config.play_weight}, danmaku_weight={self.config.danmaku_weight}")
    
    def _calculate_video_score(self, video: VideoData) -> float:
        """计算视频综合得分
        
        Args:
            video: 视频数据
            
        Returns:
            视频综合得分
        """
        # 获取播放量和弹幕量
        play_count = max(video.play_count, 1)  # 避免除零
        danmaku_count = max(video.danmaku_count, 0)
        
        # 对数标准化处理，避免数值过大
        normalized_play = math.log10(play_count)
        normalized_danmaku = math.log10(danmaku_count + 1)  # +1避免log(0)
        
        # 计算加权得分
        score = (
            normalized_play * self.config.play_weight +
            normalized_danmaku * self.config.danmaku_weight
        )
        
        app_logger.debug(
            f"视频得分计算: {video.title[:30]}... | "
            f"播放量={play_count}, 弹幕量={danmaku_count} | "
            f"标准化播放={normalized_play:.2f}, 标准化弹幕={normalized_danmaku:.2f} | "
            f"最终得分={score:.3f}"
        )
        
        return score
    
    def _filter_videos(self, videos: List[VideoData]) -> List[VideoData]:
        """过滤低质量视频
        
        Args:
            videos: 原始视频列表
            
        Returns:
            过滤后的视频列表
        """
        filtered_videos = []
        
        for video in videos:
            # 检查播放量阈值
            if video.play_count < self.config.min_play_count:
                app_logger.debug(f"过滤视频（播放量不足）: {video.title[:30]}... 播放量={video.play_count}")
                continue
            
            # 检查弹幕量阈值
            if video.danmaku_count < self.config.min_danmaku_count:
                app_logger.debug(f"过滤视频（弹幕量不足）: {video.title[:30]}... 弹幕量={video.danmaku_count}")
                continue
            
            # 检查标题是否有效
            if not video.title or not video.title.strip():
                app_logger.debug(f"过滤视频（标题无效）: {video.url}")
                continue
            
            filtered_videos.append(video)
        
        app_logger.info(f"视频过滤完成: 原始数量={len(videos)}, 过滤后数量={len(filtered_videos)}")
        return filtered_videos
    
    def rank_videos(
        self,
        videos_data: List[Dict[str, Any]],
        top_count: Optional[int] = None
    ) -> Dict[str, Any]:
        """对视频进行排序并返回前N个
        
        Args:
            videos_data: 视频数据列表，格式与agent.py中的格式化结果一致
            top_count: 返回的视频数量，如果为None则使用配置中的默认值
            
        Returns:
            包含排序结果的字典
        """
        try:
            if not videos_data:
                app_logger.warning("输入的视频数据为空")
                return {
                    "success": False,
                    "error": "输入的视频数据为空",
                    "ranked_videos": []
                }
            
            # 使用配置中的top_count或传入的参数
            final_top_count = top_count if top_count is not None else self.config.top_count
            
            app_logger.info(f"开始对 {len(videos_data)} 个视频进行排序，返回前 {final_top_count} 个")
            
            # 1. 转换为VideoData对象
            videos = []
            for video_dict in videos_data:
                try:
                    video = VideoData.from_dict(video_dict)
                    videos.append(video)
                except Exception as e:
                    app_logger.warning(f"解析视频数据失败: {e}, 数据: {video_dict}")
                    continue
            
            if not videos:
                return {
                    "success": False,
                    "error": "没有有效的视频数据",
                    "ranked_videos": []
                }
            
            # 2. 过滤低质量视频
            filtered_videos = self._filter_videos(videos)
            
            if not filtered_videos:
                app_logger.warning("过滤后没有符合条件的视频")
                return {
                    "success": True,
                    "warning": "过滤后没有符合条件的视频",
                    "ranked_videos": [],
                    "original_count": len(videos),
                    "filtered_count": 0
                }
            
            # 3. 计算得分并排序
            scored_videos = []
            for video in filtered_videos:
                score = self._calculate_video_score(video)
                scored_videos.append((video, score))
            
            # 按得分降序排序
            scored_videos.sort(key=lambda x: x[1], reverse=True)
            
            # 4. 取前N个视频
            top_videos = scored_videos[:final_top_count]
            
            # 5. 格式化结果
            ranked_videos = []
            for i, (video, score) in enumerate(top_videos, 1):
                video_dict = video.to_dict()
                video_dict["rank"] = i
                video_dict["score"] = round(score, 3)
                ranked_videos.append(video_dict)
            
            app_logger.info(f"视频排序完成，返回 {len(ranked_videos)} 个优质视频")
            
            return {
                "success": True,
                "ranked_videos": ranked_videos,
                "original_count": len(videos),
                "filtered_count": len(filtered_videos),
                "returned_count": len(ranked_videos),
                "ranking_config": {
                    "play_weight": self.config.play_weight,
                    "danmaku_weight": self.config.danmaku_weight,
                    "min_play_count": self.config.min_play_count,
                    "min_danmaku_count": self.config.min_danmaku_count
                }
            }
            
        except Exception as e:
            app_logger.error(f"视频排序失败: {e}")
            return {
                "success": False,
                "error": str(e),
                "ranked_videos": []
            }
    
    def update_config(self, **kwargs) -> None:
        """更新排序配置
        
        Args:
            **kwargs: 配置参数，支持play_weight, danmaku_weight, top_count等
        """
        old_config = {
            "play_weight": self.config.play_weight,
            "danmaku_weight": self.config.danmaku_weight,
            "top_count": self.config.top_count,
            "min_play_count": self.config.min_play_count,
            "min_danmaku_count": self.config.min_danmaku_count
        }
        
        # 更新配置
        for key, value in kwargs.items():
            if hasattr(self.config, key):
                setattr(self.config, key, value)
                app_logger.info(f"配置更新: {key} = {old_config.get(key)} -> {value}")
            else:
                app_logger.warning(f"未知配置参数: {key}")
        
        # 验证权重和
        total_weight = self.config.play_weight + self.config.danmaku_weight
        if abs(total_weight - 1.0) > 0.001:
            app_logger.warning(f"权重总和不为1.0: {total_weight}, 建议调整权重配置")


# 便捷函数
def rank_bilibili_videos(
    videos_data: List[Dict[str, Any]],
    play_weight: float = 0.7,
    danmaku_weight: float = 0.3,
    top_count: int = 5
) -> Dict[str, Any]:
    """便捷的视频排序函数
    
    Args:
        videos_data: 视频数据列表
        play_weight: 播放量权重
        danmaku_weight: 弹幕量权重
        top_count: 返回视频数量
        
    Returns:
        排序结果
    """
    config = RankingConfig(
        play_weight=play_weight,
        danmaku_weight=danmaku_weight,
        top_count=top_count
    )
    service = BilibiliRankingService(config)
    return service.rank_videos(videos_data) 