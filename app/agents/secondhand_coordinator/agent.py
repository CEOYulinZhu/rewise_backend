"""
二手交易平台协调器Agent

统一协调二手平台搜索和交易文案生成，为用户提供完整的二手交易解决方案。
异步调用搜索Agent和文案生成Agent，整合两者的结果。
"""

import asyncio
import time
from typing import Dict, Any, Optional

from app.core.logger import app_logger
from app.agents.secondhand_search.agent import SecondhandSearchAgent
from app.agents.content_generation.agent import ContentGenerationAgent
from app.models.secondhand_trading_models import (
    SecondhandTradingResponse,
    SecondhandTradingRequest,
    SecondhandTradingDataConverter
)


class SecondhandTradingAgent:
    """二手交易平台协调器Agent - 统一协调搜索和文案生成"""
    
    def __init__(self):
        # 子Agent实例（延迟初始化）
        self._search_agent = None
        self._content_agent = None
        self._is_initialized = False
    
    async def _ensure_initialized(self):
        """确保子Agent已初始化"""
        if not self._is_initialized:
            self._search_agent = SecondhandSearchAgent()
            self._content_agent = ContentGenerationAgent()
            self._is_initialized = True
            app_logger.info("二手交易平台协调器Agent子模块初始化完成")
    
    async def coordinate_trading(
        self,
        analysis_result: Dict[str, Any],
        max_results_per_platform: int = 10,
        include_xianyu: bool = True,
        include_aihuishou: bool = True,
        enable_parallel: bool = True
    ) -> SecondhandTradingResponse:
        """协调二手交易平台推荐
        
        Args:
            analysis_result: 物品分析结果，包含category、condition、description等信息
            max_results_per_platform: 每个平台最大返回结果数，默认10个
            include_xianyu: 是否包含闲鱼搜索，默认True
            include_aihuishou: 是否包含爱回收搜索，默认True
            enable_parallel: 是否启用并行处理，默认True
            
        Returns:
            整合了搜索结果和文案生成的完整响应对象
        """
        start_time = time.time()
        
        try:
            await self._ensure_initialized()
            app_logger.info("开始协调二手交易平台推荐")
            
            # 验证输入参数
            if not analysis_result or not isinstance(analysis_result, dict):
                return SecondhandTradingDataConverter.create_response(
                    success=False,
                    error="分析结果为空或格式错误"
                )
            
            # 记录处理信息
            category = analysis_result.get("category", "未知")
            condition = analysis_result.get("condition", "未知")
            description = analysis_result.get("description", "")[:50]
            app_logger.info(f"处理物品: 类别={category}, 状态={condition}, 描述={description}...")
            
            if enable_parallel:
                # 并行执行搜索和文案生成
                app_logger.info("启用并行处理模式")
                
                search_task = self._search_agent.search_from_analysis(
                    analysis_result=analysis_result,
                    max_results_per_platform=max_results_per_platform,
                    include_xianyu=include_xianyu,
                    include_aihuishou=include_aihuishou
                )
                
                content_task = self._content_agent.generate_content(
                    analysis_result=analysis_result
                )
                
                # 等待两个任务完成
                search_result, content_result = await asyncio.gather(
                    search_task,
                    content_task,
                    return_exceptions=True
                )
                
                # 检查是否有异常
                if isinstance(search_result, Exception):
                    app_logger.error(f"二手平台搜索异常: {search_result}")
                    search_result = None
                    search_error = str(search_result)
                else:
                    search_error = None if search_result and search_result.get("success", False) else search_result.get("error", "搜索返回空结果")
                
                if isinstance(content_result, Exception):
                    app_logger.error(f"文案生成异常: {content_result}")
                    content_result = None
                    content_error = str(content_result)
                else:
                    content_error = None if content_result and content_result.success else content_result.error if content_result else "文案生成返回空结果"
            
            else:
                # 串行执行
                app_logger.info("启用串行处理模式")
                
                # 1. 执行二手平台搜索
                app_logger.info("步骤1: 二手平台搜索")
                try:
                    search_result = await self._search_agent.search_from_analysis(
                        analysis_result=analysis_result,
                        max_results_per_platform=max_results_per_platform,
                        include_xianyu=include_xianyu,
                        include_aihuishou=include_aihuishou
                    )
                    search_error = None if search_result and search_result.get("success", False) else search_result.get("error", "搜索返回空结果")
                except Exception as e:
                    app_logger.error(f"二手平台搜索失败: {e}")
                    search_result = None
                    search_error = str(e)
                
                # 2. 执行文案生成
                app_logger.info("步骤2: 交易文案生成")
                try:
                    content_result = await self._content_agent.generate_content(
                        analysis_result=analysis_result
                    )
                    content_error = None if content_result and content_result.success else content_result.error if content_result else "文案生成返回空结果"
                except Exception as e:
                    app_logger.error(f"文案生成失败: {e}")
                    content_result = None
                    content_error = str(e)
            
            # 处理结果
            end_time = time.time()
            processing_time = end_time - start_time
            
            response = await self._process_results(
                analysis_result=analysis_result,
                search_result=search_result,
                content_result=content_result,
                search_error=search_error,
                content_error=content_error,
                enable_parallel=enable_parallel,
                processing_time=processing_time
            )
            
            app_logger.info(f"二手交易协调完成，总耗时: {processing_time:.2f}秒")
            return response
            
        except Exception as e:
            app_logger.error(f"协调二手交易推荐失败: {e}")
            processing_time = time.time() - start_time
            
            return SecondhandTradingDataConverter.create_response(
                success=False,
                error=str(e),
                analysis_result=analysis_result,
                processing_metadata=SecondhandTradingDataConverter.create_processing_metadata(
                    processing_mode="parallel" if enable_parallel else "serial",
                    processing_time_seconds=processing_time,
                    search_success=False,
                    content_success=False,
                    search_error="协调器异常",
                    content_error="协调器异常"
                )
            )
    
    async def _process_results(
        self,
        analysis_result: Dict[str, Any],
        search_result,
        content_result,
        search_error: Optional[str],
        content_error: Optional[str],
        enable_parallel: bool,
        processing_time: float
    ) -> SecondhandTradingResponse:
        """处理和整合子Agent的结果"""
        try:
            # 检查结果状态
            search_success = search_result is not None and search_result.get("success", False)
            content_success = content_result is not None and content_result.success
            
            # 如果两个都失败，返回失败响应
            if not search_success and not content_success:
                error_msg = f"搜索失败: {search_error or '未知错误'}; 文案生成失败: {content_error or '未知错误'}"
                return SecondhandTradingDataConverter.create_response(
                    success=False,
                    error=error_msg,
                    analysis_result=analysis_result,
                    processing_metadata=SecondhandTradingDataConverter.create_processing_metadata(
                        processing_mode="parallel" if enable_parallel else "serial",
                        processing_time_seconds=processing_time,
                        search_success=search_success,
                        content_success=content_success,
                        search_error=search_error,
                        content_error=content_error
                    )
                )
            
            # 记录结果状态
            if search_success:
                total_products = search_result.get("result", {}).get("total_products", 0)
                app_logger.info(f"二手平台搜索成功: 找到 {total_products} 个商品")
            else:
                app_logger.warning(f"二手平台搜索失败: {search_error}")
            
            if content_success:
                title = content_result.get_generated_title() if hasattr(content_result, 'get_generated_title') else content_result.content_result.title if content_result.content_result else "未知标题"
                app_logger.info(f"文案生成成功: 标题={title[:20]}...")
            else:
                app_logger.warning(f"文案生成失败: {content_error}")
            
            # 创建处理元数据
            processing_metadata = SecondhandTradingDataConverter.create_processing_metadata(
                processing_mode="parallel" if enable_parallel else "serial",
                processing_time_seconds=processing_time,
                search_success=search_success,
                content_success=content_success,
                search_error=search_error,
                content_error=content_error
            )
            
            # 构建最终响应
            response = SecondhandTradingDataConverter.create_response(
                success=True,  # 至少有一个成功就算成功
                analysis_result=analysis_result,
                search_result=search_result if search_success else None,
                content_result=content_result if content_success else None,
                processing_metadata=processing_metadata
            )
            
            app_logger.info("协调器结果处理完成")
            return response
            
        except Exception as e:
            app_logger.error(f"处理子Agent结果失败: {e}")
            return SecondhandTradingDataConverter.create_response(
                success=False,
                error=f"结果处理失败: {e}",
                analysis_result=analysis_result,
                processing_metadata=SecondhandTradingDataConverter.create_processing_metadata(
                    processing_mode="parallel" if enable_parallel else "serial",
                    processing_time_seconds=processing_time,
                    search_success=False,
                    content_success=False,
                    search_error="结果处理异常",
                    content_error="结果处理异常"
                )
            )
    
    async def coordinate_with_request(self, request: SecondhandTradingRequest) -> SecondhandTradingResponse:
        """使用请求对象进行协调"""
        return await self.coordinate_trading(
            analysis_result=request.analysis_result,
            max_results_per_platform=request.max_results_per_platform,
            include_xianyu=request.include_xianyu,
            include_aihuishou=request.include_aihuishou,
            enable_parallel=request.enable_parallel
        )
    
    def get_component_status(self) -> Dict[str, Any]:
        """获取子组件状态信息"""
        return {
            "initialized": self._is_initialized,
            "search_agent": self._search_agent is not None,
            "content_agent": self._content_agent is not None
        }
    
    async def close(self):
        """关闭Agent相关资源"""
        try:
            if self._search_agent:
                await self._search_agent.close()
            if self._content_agent:
                await self._content_agent.close()
            
            self._search_agent = None
            self._content_agent = None
            self._is_initialized = False
            
            app_logger.info("二手交易平台协调器Agent资源清理完成")
            
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
secondhand_trading_agent = SecondhandTradingAgent()


async def coordinate_secondhand_trading(
    analysis_result: Dict[str, Any],
    max_results_per_platform: int = 10,
    include_xianyu: bool = True,
    include_aihuishou: bool = True,
    enable_parallel: bool = True
) -> SecondhandTradingResponse:
    """协调二手交易推荐的便捷函数
    
    Args:
        analysis_result: 物品分析结果
        max_results_per_platform: 每个平台最大返回结果数，默认10个
        include_xianyu: 是否包含闲鱼搜索，默认True
        include_aihuishou: 是否包含爱回收搜索，默认True
        enable_parallel: 是否启用并行处理，默认True
        
    Returns:
        整合了搜索结果和文案生成的完整响应对象
    """
    return await secondhand_trading_agent.coordinate_trading(
        analysis_result=analysis_result,
        max_results_per_platform=max_results_per_platform,
        include_xianyu=include_xianyu,
        include_aihuishou=include_aihuishou,
        enable_parallel=enable_parallel
    ) 