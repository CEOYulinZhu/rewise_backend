"""
WebSocket任务处理API路由

提供WebSocket实时处理端点，支持物品处置任务的实时进度推送
"""

import json
from datetime import datetime
from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from app.core.logger import app_logger
from app.models.processing_master_models import ProcessingMasterRequest
from app.agents.processing_master.agent import ProcessingMasterAgent
from app.api.dependencies.validation import validate_processing_master_request

router = APIRouter(prefix="/tasks", tags=["tasks"])


@router.websocket("/ws/process")
async def websocket_process(websocket: WebSocket):
    """
    WebSocket实时处理端点
    
    客户端连接后发送处理请求，服务端实时返回处理进度和结果。
    
    请求格式：
    {
        "image_url": "图片URL或路径（可选）",
        "text_description": "文字描述（可选）", 
        "user_location": {"lat": 纬度, "lon": 经度}（可选）
    }
    
    响应格式：
    {
        "type": "step_update",
        "step": "步骤名称",
        "title": "步骤标题", 
        "status": "pending|running|completed|failed",
        "description": "步骤描述",
        "result": {...},          // 步骤结果（成功时）
        "error": "错误信息",       // 错误信息（失败时）
        "metadata": {...},        // 元数据
        "timestamp": "时间戳"
    }
    """
    await websocket.accept()
    app_logger.info("WebSocket连接已建立")
    
    try:
        # 接收客户端请求
        request_data = await websocket.receive_text()
        try:
            request_json = json.loads(request_data)
        except json.JSONDecodeError as e:
            await websocket.send_text(json.dumps({
                "type": "error",
                "error": f"JSON格式错误: {str(e)}"
            }))
            await websocket.close()
            return
        
        # 验证请求格式
        try:
            request = validate_processing_master_request(request_json)
        except Exception as e:
            await websocket.send_text(json.dumps({
                "type": "error", 
                "error": f"请求参数验证失败: {str(e)}"
            }))
            await websocket.close()
            return
        
        app_logger.info(f"开始WebSocket处理请求: {request.text_description[:50] if request.text_description else 'image_only'}...")
        app_logger.debug(f"请求详情 - image_url存在: {bool(request.image_url)}, text_description: {request.text_description}, user_location: {request.user_location}")
        
        # 使用总处理协调器Agent处理请求
        async with ProcessingMasterAgent() as agent:
            try:
                step_count = 0
                async for step in agent.process_complete_solution(request):
                    step_count += 1
                    app_logger.debug(f"收到第{step_count}个步骤: {step.step_name} - {step.status.value}")
                    
                    # 发送步骤更新
                    step_data = {
                        "type": "step_update",
                        "step": step.step_name,
                        "title": step.step_title,
                        "status": step.status.value,
                        "description": step.description,
                        "timestamp": datetime.fromtimestamp(step.timestamp).isoformat() if step.timestamp else datetime.now().isoformat()
                    }
                    
                    # 添加结果数据（如果有）
                    if step.result is not None:
                        step_data["result"] = step.result  # type: ignore
                        # 特别记录最终结果
                        if step.step_name == "result_integration":
                            app_logger.info(f"最终结果步骤: 状态={step.status.value}, 结果大小={len(str(step.result))}")
                    else:
                        # 记录空结果的情况
                        if step.step_name == "result_integration":
                            app_logger.warning(f"最终结果步骤结果为空: 状态={step.status.value}, 错误={step.error}")
                    
                    # 添加错误信息（如果有） 
                    if step.error:
                        step_data["error"] = step.error
                    
                    # 添加元数据（如果有）
                    if step.metadata:
                        step_data["metadata"] = step.metadata  # type: ignore
                    
                    await websocket.send_text(json.dumps(step_data, ensure_ascii=False))
                    app_logger.debug(f"发送步骤更新: {step.step_name} - {step.status.value}")
                
                app_logger.info(f"处理完成，总共处理了{step_count}个步骤")
                
                # 发送完成信号
                await websocket.send_text(json.dumps({
                    "type": "process_complete",
                    "message": "处理完成",
                    "timestamp": datetime.now().isoformat()
                }))
                app_logger.info("WebSocket处理完成")
                
            except Exception as e:
                app_logger.error(f"处理过程中发生错误: {e}")
                await websocket.send_text(json.dumps({
                    "type": "error",
                    "error": f"处理失败: {str(e)}",
                    "timestamp": datetime.now().isoformat()
                }))
    
    except WebSocketDisconnect:
        app_logger.info("WebSocket连接已断开")
    except Exception as e:
        app_logger.error(f"WebSocket处理异常: {e}")
        try:
            await websocket.send_text(json.dumps({
                "type": "error",
                "error": f"服务器错误: {str(e)}",
                "timestamp": datetime.now().isoformat()
            }))
        except:
            pass  # 连接可能已断开
    finally:
        try:
            await websocket.close()
        except:
            pass
