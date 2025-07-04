"""
回收捐赠总协调器Agent

统一协调回收地点推荐和平台推荐，为用户提供完整的回收捐赠解决方案。
异步调用地点推荐Agent和平台推荐Agent，整合两者的结果。
"""

import asyncio
import time
from typing import Dict, Any, Optional

from app.core.logger import app_logger
from app.agents.recycling_location.agent import RecyclingLocationAgent
from app.agents.platform_recommendation.agent import PlatformRecommendationAgent
from app.models.recycling_coordinator_models import (
    RecyclingCoordinatorResponse,
    RecyclingCoordinatorDataConverter
)


class RecyclingCoordinatorAgent:
    """回收捐赠总协调器Agent - 统一协调地点推荐和平台推荐"""
    
    def __init__(self):
        # 子Agent实例（延迟初始化）
        self._location_agent = None
        self._platform_agent = None
        self._is_initialized = False
    
    async def _ensure_initialized(self):
        """确保子Agent已初始化"""
        if not self._is_initialized:
            self._location_agent = RecyclingLocationAgent()
            self._platform_agent = PlatformRecommendationAgent()
            self._is_initialized = True
            app_logger.info("回收捐赠总协调器Agent子模块初始化完成")
    
    async def coordinate_recycling_donation(
        self,
        analysis_result: Dict[str, Any],
        user_location: str,
        radius: int = 50000,
        max_locations: int = 20,
        enable_parallel: bool = True
    ) -> RecyclingCoordinatorResponse:
        """协调回收捐赠推荐
        
        Args:
            analysis_result: 物品分析结果，包含category、condition、description等信息
            user_location: 用户位置，格式为"经度,纬度"
            radius: 搜索半径（米），默认50公里
            max_locations: 最大返回地点数量，默认20个
            enable_parallel: 是否启用并行处理，默认True
            
        Returns:
            整合了地点推荐和平台推荐的完整响应对象
        """
        start_time = time.time()
        
        try:
            await self._ensure_initialized()
            app_logger.info("开始协调回收捐赠推荐")
            
            # 验证输入参数
            if not analysis_result or not isinstance(analysis_result, dict):
                return RecyclingCoordinatorDataConverter.create_response(
                    success=False,
                    error="分析结果为空或格式错误"
                )
            
            if not user_location:
                return RecyclingCoordinatorDataConverter.create_response(
                    success=False,
                    error="用户位置不能为空",
                    analysis_result=analysis_result
                )
            
            # 记录处理信息
            category = analysis_result.get("category", "未知")
            condition = analysis_result.get("condition", "未知")
            app_logger.info(f"处理物品: 类别={category}, 状态={condition}, 用户位置={user_location}")
            
            if enable_parallel:
                # 并行执行地点推荐和平台推荐
                app_logger.info("启用并行处理模式")
                
                location_task = self._location_agent.analyze_and_recommend_locations(
                    analysis_result=analysis_result,
                    user_location=user_location,
                    radius=radius,
                    max_locations=max_locations
                )
                
                platform_task = self._platform_agent.recommend_platforms(
                    analysis_result=analysis_result
                )
                
                # 等待两个任务完成
                location_result, platform_result = await asyncio.gather(
                    location_task,
                    platform_task,
                    return_exceptions=True
                )
                
                # 检查是否有异常
                if isinstance(location_result, Exception):
                    app_logger.error(f"地点推荐异常: {location_result}")
                    location_result = None
                    location_error = str(location_result)
                else:
                    location_error = None if location_result and location_result.success else location_result.error if location_result else "地点推荐返回空结果"
                
                if isinstance(platform_result, Exception):
                    app_logger.error(f"平台推荐异常: {platform_result}")
                    platform_result = None
                    platform_error = str(platform_result)
                else:
                    platform_error = None if platform_result and platform_result.success else platform_result.error if platform_result else "平台推荐返回空结果"
            
            else:
                # 串行执行
                app_logger.info("启用串行处理模式")
                
                # 1. 执行地点推荐
                app_logger.info("步骤1: 回收地点推荐")
                try:
                    location_result = await self._location_agent.analyze_and_recommend_locations(
                        analysis_result=analysis_result,
                        user_location=user_location,
                        radius=radius,
                        max_locations=max_locations
                    )
                    location_error = None if location_result and location_result.success else location_result.error if location_result else "地点推荐返回空结果"
                except Exception as e:
                    app_logger.error(f"地点推荐失败: {e}")
                    location_result = None
                    location_error = str(e)
                
                # 2. 执行平台推荐
                app_logger.info("步骤2: 平台推荐")
                try:
                    platform_result = await self._platform_agent.recommend_platforms(
                        analysis_result=analysis_result
                    )
                    platform_error = None if platform_result and platform_result.success else platform_result.error if platform_result else "平台推荐返回空结果"
                except Exception as e:
                    app_logger.error(f"平台推荐失败: {e}")
                    platform_result = None
                    platform_error = str(e)
            
            # 处理结果
            end_time = time.time()
            processing_time = end_time - start_time
            
            response = await self._process_results(
                analysis_result=analysis_result,
                location_result=location_result,
                platform_result=platform_result,
                location_error=location_error,
                platform_error=platform_error,
                enable_parallel=enable_parallel,
                processing_time=processing_time
            )
            
            app_logger.info(f"回收捐赠协调完成，总耗时: {processing_time:.2f}秒")
            return response
            
        except Exception as e:
            app_logger.error(f"协调回收捐赠推荐失败: {e}")
            processing_time = time.time() - start_time
            
            return RecyclingCoordinatorDataConverter.create_response(
                success=False,
                error=str(e),
                analysis_result=analysis_result,
                processing_metadata=RecyclingCoordinatorDataConverter.create_processing_metadata(
                    enable_parallel=enable_parallel,
                    location_success=False,
                    platform_success=False,
                    location_error="协调器异常",
                    platform_error="协调器异常",
                    processing_time_seconds=processing_time
                )
            )
    
    async def _process_results(
        self,
        analysis_result: Dict[str, Any],
        location_result,
        platform_result,
        location_error: Optional[str],
        platform_error: Optional[str],
        enable_parallel: bool,
        processing_time: float
    ) -> RecyclingCoordinatorResponse:
        """处理和整合子Agent的结果"""
        try:
            # 检查结果状态
            location_success = location_result is not None and location_result.success
            platform_success = platform_result is not None and platform_result.success
            
            # 如果两个都失败，返回失败响应
            if not location_success and not platform_success:
                error_msg = f"地点推荐失败: {location_error or '未知错误'}; 平台推荐失败: {platform_error or '未知错误'}"
                return RecyclingCoordinatorDataConverter.create_response(
                    success=False,
                    error=error_msg,
                    analysis_result=analysis_result,
                    processing_metadata=RecyclingCoordinatorDataConverter.create_processing_metadata(
                        enable_parallel=enable_parallel,
                        location_success=location_success,
                        platform_success=platform_success,
                        location_error=location_error,
                        platform_error=platform_error,
                        processing_time_seconds=processing_time
                    )
                )
            
            # 记录结果状态
            if location_success:
                location_count = len(location_result.locations) if location_result.locations else 0
                recycling_type = location_result.recycling_type
                app_logger.info(f"地点推荐成功: 回收类型={recycling_type}, 地点数量={location_count}")
            else:
                app_logger.warning(f"地点推荐失败: {location_error}")
            
            if platform_success:
                platform_count = (len(platform_result.ai_recommendations.recommendations) 
                                if platform_result.ai_recommendations else 0)
                app_logger.info(f"平台推荐成功: 推荐平台数量={platform_count}")
            else:
                app_logger.warning(f"平台推荐失败: {platform_error}")
            
            # 创建处理元数据
            processing_metadata = RecyclingCoordinatorDataConverter.create_processing_metadata(
                enable_parallel=enable_parallel,
                location_success=location_success,
                platform_success=platform_success,
                location_error=location_error,
                platform_error=platform_error,
                processing_time_seconds=processing_time
            )
            
            # 构建最终响应
            response = RecyclingCoordinatorDataConverter.create_response(
                success=True,  # 至少有一个成功就算成功
                analysis_result=analysis_result,
                location_recommendation=location_result if location_success else None,
                platform_recommendation=platform_result if platform_success else None,
                processing_metadata=processing_metadata
            )
            
            app_logger.info("协调器结果处理完成")
            return response
            
        except Exception as e:
            app_logger.error(f"处理子Agent结果失败: {e}")
            return RecyclingCoordinatorDataConverter.create_response(
                success=False,
                error=f"结果处理失败: {e}",
                analysis_result=analysis_result,
                processing_metadata=RecyclingCoordinatorDataConverter.create_processing_metadata(
                    enable_parallel=enable_parallel,
                    location_success=False,
                    platform_success=False,
                    location_error="结果处理异常",
                    platform_error="结果处理异常",
                    processing_time_seconds=processing_time
                )
            )
    
    def get_component_status(self) -> Dict[str, Any]:
        """获取子组件状态信息"""
        return {
            "initialized": self._is_initialized,
            "location_agent": self._location_agent is not None,
            "platform_agent": self._platform_agent is not None
        }
    
    async def close(self):
        """关闭Agent相关资源"""
        try:
            if self._location_agent:
                await self._location_agent.close()
            if self._platform_agent:
                await self._platform_agent.close()
            
            self._location_agent = None
            self._platform_agent = None
            self._is_initialized = False
            
            app_logger.info("回收捐赠总协调器Agent资源清理完成")
            
        except Exception as e:
            app_logger.warning(f"关闭Agent资源时出现警告: {e}")
    
    async def __aenter__(self):
        """异步上下文管理器入口"""
        await self._ensure_initialized()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """异步上下文管理器出口"""
        await self.close()


# 全局Agent实例
recycling_coordinator_agent = RecyclingCoordinatorAgent()


async def coordinate_recycling_donation(
    analysis_result: Dict[str, Any],
    user_location: str,
    radius: int = 50000,
    max_locations: int = 20,
    enable_parallel: bool = True
) -> RecyclingCoordinatorResponse:
    """协调回收捐赠推荐的便捷函数
    
    Args:
        analysis_result: 物品分析结果
        user_location: 用户位置，格式为"经度,纬度"
        radius: 搜索半径（米），默认50公里
        max_locations: 最大返回地点数量，默认20个
        enable_parallel: 是否启用并行处理，默认True
        
    Returns:
        整合了地点推荐和平台推荐的完整响应对象
    """
    return await recycling_coordinator_agent.coordinate_recycling_donation(
        analysis_result=analysis_result,
        user_location=user_location,
        radius=radius,
        max_locations=max_locations,
        enable_parallel=enable_parallel
    ) 