"""
总处理协调器Agent

集成分析服务和四大处理Agent，为用户提供完整的闲置物品处置解决方案。
支持纯图片、纯文字、图片+文字三种输入方式，异步调用各个子Agent。
"""

import asyncio
import time
from typing import Dict, Any, Optional, Callable, AsyncGenerator
from pathlib import Path

from app.core.logger import app_logger
from app.services.llm.lanxin_service import LanxinService
from app.utils.analysis_merger import AnalysisMerger

# 导入四大Agent
from app.agents.disposal_recommendation.agent import DisposalRecommendationAgent
from app.agents.creative_coordinator.agent import CreativeCoordinatorAgent
from app.agents.recycling_coordinator.agent import RecyclingCoordinatorAgent
from app.agents.secondhand_coordinator.agent import SecondhandTradingAgent

from app.models.processing_master_models import (
    ProcessingMasterRequest,
    ProcessingMasterResponse,
    ProcessingMasterDataConverter,
    ProcessingStep,
    ProcessingStepStatus
)


class ProcessingMasterAgent:
    """总处理协调器Agent - 统一协调所有处理流程"""
    
    def __init__(self):
        # 分析服务
        self._lanxin_service = None
        
        # 四大子Agent（延迟初始化）
        self._disposal_agent = None
        self._creative_agent = None
        self._recycling_agent = None
        self._secondhand_agent = None
        
        self._is_initialized = False
    
    async def _ensure_initialized(self):
        """确保所有服务已初始化"""
        if not self._is_initialized:
            self._lanxin_service = LanxinService()
            
            # 初始化四大Agent
            self._disposal_agent = DisposalRecommendationAgent()
            self._creative_agent = CreativeCoordinatorAgent()
            self._recycling_agent = RecyclingCoordinatorAgent()
            self._secondhand_agent = SecondhandTradingAgent()
            
            self._is_initialized = True
            app_logger.info("总处理协调器Agent初始化完成")
    
    async def process_complete_solution(
        self,
        request: ProcessingMasterRequest,
        progress_callback: Optional[Callable[[ProcessingStep], None]] = None
    ) -> AsyncGenerator[ProcessingStep, None]:
        """处理完整解决方案（支持进度回调）
        
        Args:
            request: 处理请求
            progress_callback: 进度回调函数
            
        Yields:
            ProcessingStep: 处理步骤和结果
        """
        start_time = time.time()
        
        try:
            await self._ensure_initialized()
            app_logger.info("开始处理完整解决方案")
            
            # 步骤1: 输入验证
            step = ProcessingStep(
                step_name="input_validation",
                step_title="输入验证",
                description="验证输入数据的有效性",
                status=ProcessingStepStatus.RUNNING,
                result=None,
                error=None,
                metadata=None,
                timestamp=time.time()
            )
            yield step.copy(deep=True)
            
            validation_result = self._validate_request(request)
            if not validation_result["valid"]:
                step.status = ProcessingStepStatus.FAILED
                step.error = validation_result["error"]
                yield step.copy(deep=True)
                return
            
            step.status = ProcessingStepStatus.COMPLETED
            step.result = {"validation": "passed"}
            yield step.copy(deep=True)
            
            # 步骤2: 内容分析
            step = ProcessingStep(
                step_name="content_analysis",
                step_title="内容分析",
                description="分析图片和/或文字内容",
                status=ProcessingStepStatus.RUNNING,
                result=None,
                error=None,
                metadata=None,
                timestamp=time.time()
            )
            yield step.copy(deep=True)
            
            analysis_result = await self._analyze_content(request)
            if not analysis_result.get("success"):
                step.status = ProcessingStepStatus.FAILED
                step.error = analysis_result.get("error", "分析失败")
                yield step.copy(deep=True)
                return
            
            step.status = ProcessingStepStatus.COMPLETED
            step.result = analysis_result
            step.metadata = {
                "analysis_source": analysis_result.get("_merge_metadata", {}).get("source", "unknown"),
                "has_conflicts": analysis_result.get("_merge_metadata", {}).get("has_conflicts", False)
            }
            yield step.copy(deep=True)
            
            # 步骤3: 处置路径推荐
            step = ProcessingStep(
                step_name="disposal_recommendation",
                step_title="正在调用处置路径推荐Agent",
                description=f"基于物品类别「{analysis_result.get('category', '未知')}」和状态「{analysis_result.get('condition', '未知')}」进行智能推荐",
                status=ProcessingStepStatus.RUNNING,
                result=None,
                error=None,
                metadata=None,
                timestamp=time.time()
            )
            yield step.copy(deep=True)
            
            # 确保Agent已初始化
            await self._ensure_initialized()
            
            disposal_result = await self._disposal_agent.recommend_from_analysis(analysis_result)
            step.status = ProcessingStepStatus.COMPLETED if disposal_result.success else ProcessingStepStatus.FAILED
            step.result = disposal_result.to_dict()
            if disposal_result.success and disposal_result.recommendations:
                highest_rec = disposal_result.recommendations.get_highest_recommendation()
                step.metadata = {
                    "highest_recommendation": highest_rec[0],
                    "highest_score": highest_rec[1].recommendation_score
                }
            yield step.copy(deep=True)
            
            # 步骤4-6: 并行调用三大协调器Agent
            if disposal_result.success:
                # 获取用户位置（如果有）
                user_location = request.user_location
                if user_location:
                    location_str = f"{user_location['lon']},{user_location['lat']}"
                else:
                    location_str = None
                
                # 创建三个并行任务
                creative_step = ProcessingStep(
                    step_name="creative_coordination",
                    step_title="正在调用创意改造Agent",
                    description="生成改造方案和搜索相关DIY视频教程",
                    status=ProcessingStepStatus.RUNNING,
                    result=None,
                    error=None,
                    metadata=None,
                    timestamp=time.time()
                )
                
                recycling_step = ProcessingStep(
                    step_name="recycling_coordination", 
                    step_title="正在调用回收捐赠Agent",
                    description=f"推荐附近回收点和回收平台{f'（用户位置: {user_location}）' if user_location else ''}",
                    status=ProcessingStepStatus.RUNNING,
                    result=None,
                    error=None,
                    metadata=None,
                    timestamp=time.time()
                )
                
                secondhand_step = ProcessingStep(
                    step_name="secondhand_coordination",
                    step_title="正在调用二手交易Agent", 
                    description="搜索二手平台价格和生成交易文案",
                    status=ProcessingStepStatus.RUNNING,
                    result=None,
                    error=None,
                    metadata=None,
                    timestamp=time.time()
                )
                
                # 返回开始状态
                yield creative_step.copy(deep=True)
                yield recycling_step.copy(deep=True)
                yield secondhand_step.copy(deep=True)
                
                # 并行执行三个Agent
                tasks = []
                
                # 创意改造任务
                tasks.append(self._creative_agent.generate_complete_solution(analysis_result))
                
                # 回收捐赠任务（如果有位置信息）
                if location_str:
                    tasks.append(self._recycling_agent.coordinate_recycling_donation(
                        analysis_result=analysis_result,
                        user_location=location_str
                    ))
                else:
                    tasks.append(self._create_no_location_result())
                
                # 二手交易任务
                tasks.append(self._secondhand_agent.coordinate_trading(analysis_result))
                
                # 等待所有任务完成
                creative_result, recycling_result, secondhand_result = await asyncio.gather(
                    *tasks, return_exceptions=True
                )
                
                # 处理创意改造结果
                if isinstance(creative_result, Exception):
                    creative_step.status = ProcessingStepStatus.FAILED
                    creative_step.error = str(creative_result)
                    creative_step.result = None
                else:
                    creative_step.status = ProcessingStepStatus.COMPLETED
                    creative_step.result = creative_result.to_dict()
                    if hasattr(creative_result, 'renovation_plan') and creative_result.renovation_plan:
                        creative_step.metadata = {
                            "project_title": getattr(creative_result.renovation_plan.summary, 'title', 'Unknown'),
                            "difficulty": getattr(creative_result.renovation_plan.summary, 'difficulty', 'Unknown'),
                            "video_count": len(getattr(creative_result, 'videos', []))
                        }
                yield creative_step.copy(deep=True)
                
                # 处理回收捐赠结果
                if isinstance(recycling_result, Exception):
                    recycling_step.status = ProcessingStepStatus.FAILED
                    recycling_step.error = str(recycling_result)
                    recycling_step.result = None
                else:
                    recycling_step.status = ProcessingStepStatus.COMPLETED
                    recycling_step.result = recycling_result.to_dict() if hasattr(recycling_result, 'to_dict') else recycling_result
                    if hasattr(recycling_result, 'has_location_recommendations') and callable(getattr(recycling_result, 'has_location_recommendations')) and recycling_result.has_location_recommendations():
                        recycling_step.metadata = {
                            "location_count": len(getattr(recycling_result.location_recommendation, 'locations', [])),
                            "recycling_type": getattr(recycling_result, 'get_recycling_type', lambda: 'Unknown')()
                        }
                yield recycling_step.copy(deep=True)
                
                # 处理二手交易结果
                if isinstance(secondhand_result, Exception):
                    secondhand_step.status = ProcessingStepStatus.FAILED
                    secondhand_step.error = str(secondhand_result)
                    secondhand_step.result = None
                else:
                    secondhand_step.status = ProcessingStepStatus.COMPLETED
                    secondhand_step.result = secondhand_result.to_dict()
                    secondhand_step.metadata = {
                        "total_products": getattr(secondhand_result, 'get_total_products', lambda: 0)(),
                        "has_content": getattr(secondhand_result, 'has_content_results', lambda: False)()
                    }
                yield secondhand_step.copy(deep=True)
                
                # 步骤7: 结果整合
                step = ProcessingStep(
                    step_name="result_integration",
                    step_title="结果整合",
                    description="整合所有Agent的处理结果",
                    status=ProcessingStepStatus.RUNNING,
                    result=None,
                    error=None,
                    metadata=None,
                    timestamp=time.time()
                )
                yield step.copy(deep=True)
                
                # 整合最终结果（使用新的数据模型）
                processing_time = time.time() - start_time
                
                try:
                    final_response = ProcessingMasterDataConverter.create_response(
                        success=True,
                        analysis_result=analysis_result.copy(),  # 使用副本避免修改原始数据
                        disposal_recommendation=disposal_result if disposal_result.success else None,
                        creative_coordination=creative_result if not isinstance(creative_result, Exception) else None,
                        recycling_coordination=recycling_result if not isinstance(recycling_result, Exception) else None,
                        secondhand_coordination=secondhand_result if not isinstance(secondhand_result, Exception) else None,
                        processing_time_seconds=processing_time
                    )
                    
                    final_dict = final_response.to_dict()
                    app_logger.info(f"最终结果数据大小: {len(str(final_dict))} 字符")
                    app_logger.debug(f"最终结果结构: {list(final_dict.keys())}")
                    
                    step.status = ProcessingStepStatus.COMPLETED
                    step.result = final_dict
                    step.metadata = {
                        "total_processing_time": processing_time,
                        "successful_agents": len(final_response.get_successful_solutions()),
                        "primary_recommendation": final_response.get_primary_recommendation(),
                        "result_size": len(str(final_dict))
                    }
                    
                except Exception as e:
                    app_logger.error(f"创建最终响应失败: {e}")
                    step.status = ProcessingStepStatus.FAILED
                    step.error = f"结果整合失败: {str(e)}"
                    step.result = None
                
                yield step.copy(deep=True)
                
                app_logger.info(f"完整解决方案处理完成，总耗时: {processing_time:.2f}秒")
            
        except Exception as e:
            app_logger.error(f"处理完整解决方案失败: {e}")
            error_step = ProcessingStep(
                step_name="system_error",
                step_title="系统错误",
                description="处理过程中发生系统错误",
                status=ProcessingStepStatus.FAILED,
                result=None,
                error=str(e),
                metadata=None,
                timestamp=time.time()
            )
            yield error_step.copy(deep=True)
    
    async def _analyze_content(self, request: ProcessingMasterRequest) -> Dict[str, Any]:
        """分析内容（图片/文字/图片+文字）"""
        try:
            has_image = bool(request.image_url)
            has_text = bool(request.text_description)
            
            if has_image and has_text:
                # 图片+文字：分别分析然后合并
                app_logger.info("检测到图片+文字输入，分别进行分析")
                
                # 并行分析
                image_task = self._lanxin_service.analyze_image(request.image_url)
                text_task = self._lanxin_service.analyze_text(request.text_description)
                
                image_result, text_result = await asyncio.gather(
                    image_task, text_task, return_exceptions=True
                )
                
                # 处理异常
                if isinstance(image_result, Exception):
                    app_logger.error(f"图片分析失败: {image_result}")
                    image_result = None
                
                if isinstance(text_result, Exception):
                    app_logger.error(f"文字分析失败: {text_result}")
                    text_result = None
                
                # 合并结果
                if image_result or text_result:
                    merged_result = AnalysisMerger.compare_and_merge(image_result, text_result)
                    merged_result["success"] = True
                    return merged_result
                else:
                    return {"success": False, "error": "图片和文字分析都失败"}
                    
            elif has_image:
                # 纯图片
                app_logger.info("检测到纯图片输入")
                result = await self._lanxin_service.analyze_image(request.image_url)
                result["success"] = True
                result["_merge_metadata"] = {"source": "image_only"}
                return result
                
            elif has_text:
                # 纯文字
                app_logger.info("检测到纯文字输入")
                result = await self._lanxin_service.analyze_text(request.text_description)
                result["success"] = True
                result["_merge_metadata"] = {"source": "text_only"}
                return result
                
            else:
                return {"success": False, "error": "未提供图片或文字描述"}
                
        except Exception as e:
            app_logger.error(f"内容分析失败: {e}")
            return {"success": False, "error": str(e)}
    
    def _validate_request(self, request: ProcessingMasterRequest) -> Dict[str, Any]:
        """验证请求参数"""
        if not request.image_url and not request.text_description:
            return {"valid": False, "error": "必须提供图片URL或文字描述"}
        
        if request.image_url:
            # 验证图片路径
            if request.image_url.startswith("http"):
                # 网络图片URL暂时跳过验证
                pass
            else:
                # 本地文件路径
                image_path = Path(request.image_url)
                if not image_path.exists():
                    return {"valid": False, "error": f"图片文件不存在: {request.image_url}"}
        
        if request.text_description and len(request.text_description.strip()) < 2:
            return {"valid": False, "error": "文字描述至少需要2个字符"}
        
        return {"valid": True}
    
    async def _create_no_location_result(self) -> Dict[str, Any]:
        """创建无位置信息时的回收协调结果"""
        return {
            "success": False,
            "error": "用户未提供位置信息，无法推荐回收地点",
            "source": "no_location"
        }
    
    def get_component_status(self) -> Dict[str, Any]:
        """获取所有组件状态"""
        return {
            "initialized": self._is_initialized,
            "lanxin_service": self._lanxin_service is not None,
            "disposal_agent": self._disposal_agent is not None,
            "creative_agent": self._creative_agent is not None,
            "recycling_agent": self._recycling_agent is not None,
            "secondhand_agent": self._secondhand_agent is not None
        }
    
    async def close(self):
        """关闭所有Agent相关资源"""
        try:
            if self._lanxin_service:
                await self._lanxin_service.__aexit__(None, None, None)
            
            if self._disposal_agent:
                await self._disposal_agent.close()
            
            if self._creative_agent:
                await self._creative_agent.close()
            
            if self._recycling_agent:
                await self._recycling_agent.close()
            
            if self._secondhand_agent:
                await self._secondhand_agent.close()
            
            self._lanxin_service = None
            self._disposal_agent = None
            self._creative_agent = None
            self._recycling_agent = None
            self._secondhand_agent = None
            self._is_initialized = False
            
            app_logger.info("总处理协调器Agent资源清理完成")
            
        except Exception as e:
            app_logger.warning(f"关闭Agent资源时出现警告: {e}")
    
    async def __aenter__(self):
        """异步上下文管理器入口"""
        await self._ensure_initialized()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """异步上下文管理器出口"""
        await self.close() 