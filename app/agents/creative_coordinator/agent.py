"""
创意改造协调器Agent

协调整合创意改造步骤生成和Bilibili视频搜索，
为用户提供完整的改造解决方案包，包含详细步骤指导和相关视频教程
"""

import asyncio
from typing import Dict, Any, Optional
from concurrent.futures import ThreadPoolExecutor

from app.core.logger import app_logger
from app.agents.creative_renovation.agent import CreativeRenovationAgent
from app.agents.bilibili_search.agent import BilibiliSearchAgent
from app.services.bilibili_ranking_service import BilibiliRankingService
from app.models.creative_coordinator_models import CoordinatorResponse, CoordinatorDataConverter


class CreativeCoordinatorAgent:
    """创意改造协调器Agent - 统一协调改造步骤生成和视频搜索"""
    
    def __init__(self):
        # 初始化子Agent实例，但不在构造函数中创建连接
        self._renovation_agent = None
        self._bilibili_agent = None
        self._ranking_service = BilibiliRankingService()
        self._is_initialized = False
    
    async def _ensure_initialized(self):
        """确保子Agent已初始化"""
        if not self._is_initialized:
            self._renovation_agent = CreativeRenovationAgent()
            self._bilibili_agent = BilibiliSearchAgent()
            self._is_initialized = True
            app_logger.info("创意改造协调器Agent子模块初始化完成")
    
    async def generate_complete_solution(
        self,
        analysis_result: Dict[str, Any],
        enable_parallel: bool = True
    ) -> CoordinatorResponse:
        """生成完整的创意改造解决方案
        
        Args:
            analysis_result: 物品分析结果，包含category、condition、description等信息
            enable_parallel: 是否启用并行处理，默认True
            
        Returns:
            结构化的协调器响应对象
        """
        try:
            await self._ensure_initialized()
            app_logger.info("开始生成完整的创意改造解决方案")
            
            # 验证分析结果格式
            if not analysis_result or not isinstance(analysis_result, dict):
                return CoordinatorResponse(
                    success=False,
                    error="分析结果为空或格式错误"
                )
            
            # 记录分析结果信息
            category = analysis_result.get("category", "未知")
            condition = analysis_result.get("condition", "未知")
            app_logger.info(f"处理物品: 类别={category}, 状态={condition}")
            
            if enable_parallel:
                # 并行执行改造步骤生成和视频搜索
                app_logger.info("启用并行处理模式")
                renovation_task = self._renovation_agent.generate_from_analysis(analysis_result)
                video_search_task = self._bilibili_agent.search_from_analysis(
                    analysis_result, 
                    max_videos=25  # 默认搜索25个视频
                )
                
                # 等待两个任务完成
                renovation_result, video_result = await asyncio.gather(
                    renovation_task,
                    video_search_task,
                    return_exceptions=True
                )
                
                # 检查是否有异常
                if isinstance(renovation_result, Exception):
                    app_logger.error(f"改造步骤生成异常: {renovation_result}")
                    renovation_result = {
                        "success": False,
                        "error": str(renovation_result),
                        "source": "renovation_parallel_error"
                    }
                
                if isinstance(video_result, Exception):
                    app_logger.error(f"视频搜索异常: {video_result}")
                    video_result = {
                        "success": False,
                        "error": str(video_result),
                        "source": "video_search_parallel_error"
                    }
            else:
                # 串行执行
                app_logger.info("启用串行处理模式")
                
                # 1. 生成改造步骤
                app_logger.info("步骤1: 生成创意改造步骤")
                renovation_result = await self._renovation_agent.generate_from_analysis(analysis_result)
                
                # 2. 搜索相关视频
                app_logger.info("步骤2: 搜索相关DIY视频")
                video_result = await self._bilibili_agent.search_from_analysis(
                    analysis_result,
                    max_videos=25  # 默认搜索25个视频
                )
            
            # 处理结果
            solution = await self._process_results(
                renovation_result=renovation_result,
                video_result=video_result
            )
            
            app_logger.info("完整创意改造解决方案生成完成")
            return solution
            
        except Exception as e:
            app_logger.error(f"生成完整改造解决方案失败: {e}")
            return CoordinatorResponse(
                success=False,
                error=str(e)
            )
    
    async def _process_results(
        self,
        renovation_result: Dict[str, Any],
        video_result: Dict[str, Any]
    ) -> CoordinatorResponse:
        """处理和整合子Agent的结果"""
        try:
            # 检查改造步骤结果
            renovation_success = renovation_result.get("success", False)
            video_search_success = video_result.get("success", False)
            
            # 如果两个都失败，返回失败响应
            if not renovation_success and not video_search_success:
                error_msg = f"改造方案生成失败: {renovation_result.get('error', '未知错误')}; 视频搜索失败: {video_result.get('error', '未知错误')}"
                return CoordinatorResponse(success=False, error=error_msg)
            
            # 处理改造方案
            renovation_plan = None
            if renovation_success:
                raw_renovation_data = renovation_result.get("renovation_plan", {})
                renovation_plan = CoordinatorDataConverter.convert_renovation_plan(raw_renovation_data)
                if renovation_plan:
                    app_logger.info(f"改造方案转换成功: {renovation_plan.summary.title}")
                else:
                    app_logger.warning("改造方案数据转换失败")
            else:
                app_logger.warning(f"改造步骤生成失败: {renovation_result.get('error', '未知错误')}")
            
            # 处理视频信息
            videos = []
            keywords = None
            search_intent = None
            if video_search_success:
                raw_videos = video_result.get("videos", [])
                keywords = video_result.get("keywords", [])
                search_intent = video_result.get("search_intent", "")
                app_logger.info(f"开始对 {len(raw_videos)} 个视频进行排序")
                
                # 使用排序服务筛选前5个视频
                ranking_result = self._ranking_service.rank_videos(raw_videos, top_count=5)
                
                if ranking_result.get("success"):
                    ranked_videos = ranking_result.get("ranked_videos", [])
                    videos = CoordinatorDataConverter.convert_videos(ranked_videos)
                    app_logger.info(f"视频排序完成，选取了 {len(videos)} 个优质视频")
                else:
                    app_logger.warning(f"视频排序失败: {ranking_result.get('error', '未知错误')}")
                    # 如果排序失败，直接取前5个
                    videos = CoordinatorDataConverter.convert_videos(raw_videos[:5])
            else:
                app_logger.warning(f"视频搜索失败: {video_result.get('error', '未知错误')}")
            
            # 构建最终响应
            response = CoordinatorResponse(
                success=True,
                renovation_plan=renovation_plan,
                videos=videos,
                keywords=keywords,
                search_intent=search_intent
            )
            
            app_logger.info(f"协调器结果处理完成: 改造方案={'有' if renovation_plan else '无'}, 视频数量={len(videos)}")
            return response
            
        except Exception as e:
            app_logger.error(f"处理子Agent结果失败: {e}")
            return CoordinatorResponse(
                success=False,
                error=f"结果处理失败: {e}"
            )
    

    
    def get_component_status(self) -> Dict[str, Any]:
        """获取子组件状态信息"""
        return {
            "initialized": self._is_initialized,
            "renovation_agent": self._renovation_agent is not None,
            "bilibili_agent": self._bilibili_agent is not None
        }
    
    async def close(self):
        """关闭Agent相关资源"""
        try:
            if self._renovation_agent:
                await self._renovation_agent.close()
            if self._bilibili_agent:
                await self._bilibili_agent.close()
            
            self._renovation_agent = None
            self._bilibili_agent = None
            self._is_initialized = False
            
            app_logger.info("创意改造协调器Agent资源清理完成")
            
        except Exception as e:
            app_logger.warning(f"关闭Agent资源时出现警告: {e}")
    
    async def __aenter__(self):
        """异步上下文管理器入口"""
        await self._ensure_initialized()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """异步上下文管理器出口"""
        await self.close() 