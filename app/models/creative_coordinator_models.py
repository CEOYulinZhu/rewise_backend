"""
创意改造协调器数据模型

定义协调器Agent返回的结构化数据模型
"""

from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class RenovationStep:
    """改造步骤数据模型"""
    title: str                          # 步骤标题
    description: str                    # 详细描述
    estimated_time_minutes: int         # 预计用时（分钟）
    difficulty: str                     # 难度等级
    tools: List[str] = field(default_factory=list)      # 所需工具（不分类）
    materials: List[str] = field(default_factory=list)  # 所需材料（不分类）


@dataclass
class RenovationSummary:
    """改造方案摘要数据模型"""
    title: str                          # 改造项目标题
    difficulty: str                     # 总体难度
    total_time_hours: float             # 总耗时（小时）
    budget_range: str                   # 预算成本范围（如"50-100元"）
    cost_description: str               # 成本描述
    required_skills: List[str] = field(default_factory=list)  # 所需技能
    tools: List[str] = field(default_factory=list)            # 工具清单（不分类）
    materials: List[str] = field(default_factory=list)        # 材料清单（不分类）
    total_steps: int = 0                # 改造步骤总数


@dataclass
class RenovationPlan:
    """完整改造方案数据模型"""
    summary: RenovationSummary          # 改造摘要
    steps: List[RenovationStep] = field(default_factory=list)  # 详细步骤


@dataclass
class VideoInfo:
    """视频信息数据模型"""
    title: str                          # 视频标题
    cover_url: str                      # 封面图片链接
    url: str                            # 视频链接
    score: float                        # 评分（排序得分）
    play_count: int                     # 播放量
    description: str                    # 视频简介
    uploader: str                       # UP主名称
    duration: str                       # 时长


@dataclass
class CoordinatorResponse:
    """协调器完整响应数据模型"""
    success: bool                       # 操作是否成功
    renovation_plan: Optional[RenovationPlan] = None  # 改造方案
    videos: List[VideoInfo] = field(default_factory=list)  # 推荐视频列表
    keywords: Optional[List[str]] = None  # 搜索关键字
    search_intent: Optional[str] = None   # 搜索意图
    error: Optional[str] = None         # 错误信息（失败时）
    
    def to_dict(self) -> dict:
        """转换为字典格式（用于JSON序列化）"""
        result = {
            "success": self.success,
            "error": self.error
        }
        
        if self.renovation_plan:
            result["renovation_plan"] = {
                "summary": {
                    "title": self.renovation_plan.summary.title,
                    "difficulty": self.renovation_plan.summary.difficulty,
                    "total_time_hours": self.renovation_plan.summary.total_time_hours,
                    "budget_range": self.renovation_plan.summary.budget_range,
                    "cost_description": self.renovation_plan.summary.cost_description,
                    "required_skills": self.renovation_plan.summary.required_skills,
                    "tools": self.renovation_plan.summary.tools,
                    "materials": self.renovation_plan.summary.materials,
                    "total_steps": self.renovation_plan.summary.total_steps
                },
                "steps": [
                    {
                        "title": step.title,
                        "description": step.description,
                        "estimated_time_minutes": step.estimated_time_minutes,
                        "difficulty": step.difficulty,
                        "tools": step.tools,
                        "materials": step.materials
                    }
                    for step in self.renovation_plan.steps
                ]
            }
        
        if self.videos:
            result["videos"] = [
                {
                    "title": video.title,
                    "cover_url": video.cover_url,
                    "url": video.url,
                    "score": video.score,
                    "play_count": video.play_count,
                    "description": video.description,
                    "uploader": video.uploader,
                    "duration": video.duration
                }
                for video in self.videos
            ]
        
        # 添加搜索关键字和搜索意图
        if self.keywords:
            result["keywords"] = self.keywords
        
        if self.search_intent:
            result["search_intent"] = self.search_intent
        
        return result


class CoordinatorDataConverter:
    """协调器数据转换器 - 将原始Agent数据转换为结构化模型"""
    
    @staticmethod
    def convert_renovation_plan(raw_renovation_data: dict) -> Optional[RenovationPlan]:
        """转换改造方案数据
        
        Args:
            raw_renovation_data: 来自改造Agent的原始数据
            
        Returns:
            结构化的改造方案对象
        """
        try:
            if not raw_renovation_data or not isinstance(raw_renovation_data, dict):
                return None
            
            # 解析摘要信息
            raw_summary = raw_renovation_data
            
            # 提取工具和材料清单（合并所有步骤的工具和材料）
            all_tools = set()
            all_materials = set()
            
            raw_steps = raw_renovation_data.get('steps', [])
            for step_data in raw_steps:
                all_tools.update(step_data.get('tools_needed', []))
                all_materials.update(step_data.get('materials_needed', []))
            
            # 计算总耗时（分钟转小时）
            total_minutes = sum(
                step.get('estimated_time_minutes', 0) 
                for step in raw_steps
            )
            total_hours = round(total_minutes / 60.0, 1)
            
            # 处理成本信息
            cost_info = raw_summary.get('estimated_cost_range', {})
            if isinstance(cost_info, dict):
                # 如果是字典格式（包含min_cost, max_cost, cost_description）
                min_cost = cost_info.get('min_cost', 0)
                max_cost = cost_info.get('max_cost', 0)
                cost_desc = cost_info.get('cost_description', '')
                
                budget_range_str = f"{min_cost}-{max_cost}元"
                cost_description = cost_desc if cost_desc else f"预计成本 {budget_range_str}"
            else:
                # 如果是字符串格式，直接使用
                budget_range_str = str(cost_info) if cost_info else "成本待定"
                cost_description = f"预计成本 {budget_range_str}"
            
            # 创建摘要对象
            summary = RenovationSummary(
                title=raw_summary.get('project_title', ''),
                difficulty=raw_summary.get('difficulty_level', ''),
                total_time_hours=total_hours,
                budget_range=budget_range_str,
                cost_description=cost_description,
                required_skills=raw_summary.get('required_skills', []),
                tools=list(all_tools),
                materials=list(all_materials),
                total_steps=len(raw_steps)
            )
            
            # 转换详细步骤
            steps = []
            for step_data in raw_steps:
                step = RenovationStep(
                    title=step_data.get('title', ''),
                    description=step_data.get('description', ''),
                    estimated_time_minutes=step_data.get('estimated_time_minutes', 0),
                    difficulty=step_data.get('difficulty', ''),
                    tools=step_data.get('tools_needed', []),
                    materials=step_data.get('materials_needed', [])
                )
                steps.append(step)
            
            return RenovationPlan(summary=summary, steps=steps)
            
        except Exception as e:
            from app.core.logger import app_logger
            app_logger.error(f"转换改造方案数据失败: {e}")
            return None
    
    @staticmethod
    def convert_videos(ranked_videos_data: List[dict]) -> List[VideoInfo]:
        """转换视频数据
        
        Args:
            ranked_videos_data: 来自排序服务的视频数据
            
        Returns:
            结构化的视频信息列表
        """
        try:
            videos = []
            for video_data in ranked_videos_data:
                video = VideoInfo(
                    title=video_data.get('title', ''),
                    cover_url=video_data.get('cover_url', ''),
                    url=video_data.get('url', ''),
                    score=video_data.get('score', 0.0),
                    play_count=video_data.get('play_count', 0),
                    description=video_data.get('description', ''),
                    uploader=video_data.get('uploader', ''),
                    duration=video_data.get('duration', '')
                )
                videos.append(video)
            
            return videos
            
        except Exception as e:
            from app.core.logger import app_logger
            app_logger.error(f"转换视频数据失败: {e}")
            return [] 