"""
Bilibili视频排序服务测试
"""

import pytest
from typing import List, Dict, Any

from app.services.bilibili_ranking_service import (
    BilibiliRankingService,
    RankingConfig,
    VideoData,
    rank_bilibili_videos
)


class TestVideoData:
    """VideoData模型测试"""
    
    def test_from_dict(self):
        """测试从字典创建VideoData"""
        video_dict = {
            "title": "测试视频",
            "uploader": "测试UP主",
            "url": "https://www.bilibili.com/video/BV123456",
            "cover_url": "https://example.com/cover.jpg",
            "play_count": 10000,
            "danmaku_count": 500,
            "duration": "05:30",
            "description": "这是一个测试视频"
        }
        
        video = VideoData.from_dict(video_dict)
        
        assert video.title == "测试视频"
        assert video.uploader == "测试UP主"
        assert video.play_count == 10000
        assert video.danmaku_count == 500
    
    def test_from_dict_missing_fields(self):
        """测试缺少字段的字典"""
        video_dict = {
            "title": "测试视频",
            "play_count": 10000
        }
        
        video = VideoData.from_dict(video_dict)
        
        assert video.title == "测试视频"
        assert video.uploader == ""
        assert video.play_count == 10000
        assert video.danmaku_count == 0
    
    def test_to_dict(self):
        """测试转换为字典"""
        video = VideoData(
            title="测试视频",
            uploader="测试UP主",
            url="https://www.bilibili.com/video/BV123456",
            cover_url="https://example.com/cover.jpg",
            play_count=10000,
            danmaku_count=500,
            duration="05:30",
            description="这是一个测试视频"
        )
        
        video_dict = video.to_dict()
        
        assert video_dict["title"] == "测试视频"
        assert video_dict["play_count"] == 10000
        assert video_dict["danmaku_count"] == 500


class TestBilibiliRankingService:
    """Bilibili排序服务测试"""
    
    @pytest.fixture
    def sample_videos(self) -> List[Dict[str, Any]]:
        """示例视频数据"""
        return [
            {
                "title": "高播放低弹幕视频",
                "uploader": "UP主1",
                "url": "https://www.bilibili.com/video/BV1",
                "cover_url": "https://example.com/cover1.jpg",
                "play_count": 100000,
                "danmaku_count": 50,
                "duration": "10:00",
                "description": "描述1"
            },
            {
                "title": "中播放高弹幕视频",
                "uploader": "UP主2", 
                "url": "https://www.bilibili.com/video/BV2",
                "cover_url": "https://example.com/cover2.jpg",
                "play_count": 50000,
                "danmaku_count": 2000,
                "duration": "08:30",
                "description": "描述2"
            },
            {
                "title": "低播放低弹幕视频",
                "uploader": "UP主3",
                "url": "https://www.bilibili.com/video/BV3",
                "cover_url": "https://example.com/cover3.jpg",
                "play_count": 500,
                "danmaku_count": 5,
                "duration": "05:00",
                "description": "描述3"
            },
            {
                "title": "高质量视频",
                "uploader": "UP主4",
                "url": "https://www.bilibili.com/video/BV4",
                "cover_url": "https://example.com/cover4.jpg",
                "play_count": 200000,
                "danmaku_count": 5000,
                "duration": "15:20",
                "description": "描述4"
            },
            {
                "title": "中等质量视频",
                "uploader": "UP主5",
                "url": "https://www.bilibili.com/video/BV5",
                "cover_url": "https://example.com/cover5.jpg",
                "play_count": 30000,
                "danmaku_count": 800,
                "duration": "12:45",
                "description": "描述5"
            }
        ]
    
    def test_init_default_config(self):
        """测试默认配置初始化"""
        service = BilibiliRankingService()
        
        assert service.config.play_weight == 0.7
        assert service.config.danmaku_weight == 0.3
        assert service.config.top_count == 5
        assert service.config.min_play_count == 1000
        assert service.config.min_danmaku_count == 10
    
    def test_init_custom_config(self):
        """测试自定义配置初始化"""
        config = RankingConfig(
            play_weight=0.6,
            danmaku_weight=0.4,
            top_count=3
        )
        service = BilibiliRankingService(config)
        
        assert service.config.play_weight == 0.6
        assert service.config.danmaku_weight == 0.4
        assert service.config.top_count == 3
    
    def test_calculate_video_score(self):
        """测试视频得分计算"""
        service = BilibiliRankingService()
        video = VideoData(
            title="测试视频",
            uploader="测试UP主",
            url="https://www.bilibili.com/video/BV123456",
            cover_url="",
            play_count=10000,
            danmaku_count=500,
            duration="",
            description=""
        )
        
        score = service._calculate_video_score(video)
        
        # 验证得分为正数
        assert score > 0
        
        # 验证得分计算逻辑
        import math
        expected_score = (
            math.log10(10000) * 0.7 + 
            math.log10(501) * 0.3
        )
        assert abs(score - expected_score) < 0.001
    
    def test_filter_videos(self, sample_videos):
        """测试视频过滤"""
        service = BilibiliRankingService()
        videos = [VideoData.from_dict(v) for v in sample_videos]
        
        filtered = service._filter_videos(videos)
        
        # 应该过滤掉播放量或弹幕量不足的视频
        assert len(filtered) < len(videos)
        
        # 所有过滤后的视频都应该满足阈值要求
        for video in filtered:
            assert video.play_count >= service.config.min_play_count
            assert video.danmaku_count >= service.config.min_danmaku_count
    
    def test_rank_videos_success(self, sample_videos):
        """测试视频排序成功"""
        service = BilibiliRankingService()
        
        result = service.rank_videos(sample_videos)
        
        assert result["success"] is True
        assert "ranked_videos" in result
        assert "original_count" in result
        assert "filtered_count" in result
        assert "returned_count" in result
        
        # 验证返回的视频数量
        ranked_videos = result["ranked_videos"]
        assert len(ranked_videos) <= service.config.top_count
        
        # 验证排序顺序（得分应该递减）
        if len(ranked_videos) > 1:
            for i in range(len(ranked_videos) - 1):
                assert ranked_videos[i]["score"] >= ranked_videos[i + 1]["score"]
        
        # 验证每个视频都有rank和score字段
        for i, video in enumerate(ranked_videos):
            assert video["rank"] == i + 1
            assert "score" in video
            assert isinstance(video["score"], (int, float))
    
    def test_rank_videos_empty_input(self):
        """测试空输入"""
        service = BilibiliRankingService()
        
        result = service.rank_videos([])
        
        assert result["success"] is False
        assert "error" in result
        assert result["ranked_videos"] == []
    
    def test_rank_videos_custom_top_count(self, sample_videos):
        """测试自定义返回数量"""
        service = BilibiliRankingService()
        
        result = service.rank_videos(sample_videos, top_count=3)
        
        assert result["success"] is True
        assert len(result["ranked_videos"]) <= 3
    
    def test_update_config(self):
        """测试配置更新"""
        service = BilibiliRankingService()
        
        # 更新配置
        service.update_config(
            play_weight=0.8,
            danmaku_weight=0.2,
            top_count=3
        )
        
        assert service.config.play_weight == 0.8
        assert service.config.danmaku_weight == 0.2
        assert service.config.top_count == 3


class TestRankBilibiliVideos:
    """便捷函数测试"""
    
    def test_rank_bilibili_videos_function(self):
        """测试便捷排序函数"""
        videos_data = [
            {
                "title": "测试视频1",
                "uploader": "UP主1",
                "url": "https://www.bilibili.com/video/BV1",
                "cover_url": "",
                "play_count": 50000,
                "danmaku_count": 1000,
                "duration": "10:00",
                "description": "描述1"
            },
            {
                "title": "测试视频2",
                "uploader": "UP主2",
                "url": "https://www.bilibili.com/video/BV2",
                "cover_url": "",
                "play_count": 30000,
                "danmaku_count": 500,
                "duration": "08:00",
                "description": "描述2"
            }
        ]
        
        result = rank_bilibili_videos(
            videos_data,
            play_weight=0.6,
            danmaku_weight=0.4,
            top_count=2
        )
        
        assert result["success"] is True
        assert len(result["ranked_videos"]) <= 2
        assert result["ranking_config"]["play_weight"] == 0.6
        assert result["ranking_config"]["danmaku_weight"] == 0.4


if __name__ == "__main__":
    # 运行测试的示例
    pytest.main([__file__, "-v"]) 