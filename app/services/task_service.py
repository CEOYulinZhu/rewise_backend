"""
任务服务

处理物品处置任务的业务逻辑
"""

import uuid
from typing import Optional

from geoalchemy2 import WKTElement
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.logger import app_logger
from app.models.task import ProcessingTask, TaskCreate, TaskStatus


class TaskService:
    """任务服务类"""
    
    def __init__(self, db_session: AsyncSession):
        self.db = db_session
    
    async def create_task(self, task_data: TaskCreate) -> uuid.UUID:
        """创建新任务"""
        
        # 处理地理位置
        user_location = None
        if task_data.user_location:
            lat = task_data.user_location["lat"]
            lon = task_data.user_location["lon"]
            user_location = WKTElement(f'POINT({lon} {lat})', srid=4326)
        
        # 创建任务记录
        task = ProcessingTask(
            input_image_url=task_data.image_url,
            input_text_description=task_data.text_description,
            input_user_location=user_location,
            status='PENDING'
        )
        
        self.db.add(task)
        await self.db.commit()
        await self.db.refresh(task)
        
        app_logger.info(f"任务已创建: {task.id}")
        return task.id
    
    async def get_task_status(self, task_id: uuid.UUID) -> Optional[TaskStatus]:
        """获取任务状态"""
        
        # 查询数据库中的任务
        stmt = select(ProcessingTask).where(ProcessingTask.id == task_id)
        result = await self.db.execute(stmt)
        task = result.scalars().first()
        
        if not task:
            return None
        
        # 构造响应
        if task.status == 'SUCCESS':
            return TaskStatus(
                status=task.status,
                data=task.result
            )
        elif task.status == 'FAILED':
            return TaskStatus(
                status=task.status,
                error=task.error_message
            )
        elif task.status == 'PROGRESS':
            # 这里可以从Redis中获取实时进度信息
            return TaskStatus(
                status=task.status,
                progress={"step": 1, "message": "任务处理中..."}
            )
        else:  # PENDING
            return TaskStatus(status=task.status)
    
    async def process_task_async(self, task_id: uuid.UUID):
        """异步处理任务（后台任务）"""
        try:
            app_logger.info(f"开始处理任务: {task_id}")
            
            # 获取任务详情
            stmt = select(ProcessingTask).where(ProcessingTask.id == task_id)
            result = await self.db.execute(stmt)
            task = result.scalars().first()
            
            if not task:
                app_logger.error(f"任务不存在: {task_id}")
                return
            
            # 更新状态为处理中
            task.status = 'PROGRESS'
            await self.db.commit()
            
            # TODO: 等待ProcessingAgent实现后再集成
            # 临时处理逻辑 - 模拟任务处理
            await self._mock_process_item(task)
            
            app_logger.info(f"任务处理完成: {task_id}")
            
        except Exception as e:
            app_logger.error(f"任务处理失败 {task_id}: {e}")
            
            # 更新失败状态
            try:
                stmt = select(ProcessingTask).where(ProcessingTask.id == task_id)
                result = await self.db.execute(stmt)
                task = result.scalars().first()
                
                if task:
                    task.status = 'FAILED'
                    task.error_message = str(e)
                    await self.db.commit()
            except Exception as update_error:
                app_logger.error(f"更新任务失败状态时出错: {update_error}")
    
    async def _mock_process_item(self, task: ProcessingTask):
        """临时的模拟处理逻辑"""
        try:
            # 模拟处理延时
            import asyncio
            await asyncio.sleep(1)
            
            # 构造模拟结果
            mock_result = {
                "overview": {
                    "creative_makeover": {
                        "recommendation_score": 75,
                        "reason_tags": ["旧物新生", "个性化定制", "实用小物"]
                    },
                    "recycling_donation": {
                        "recommendation_score": 50,
                        "reason_tags": ["环保处理", "支持公益"]
                    },
                    "second_hand_trade": {
                        "recommendation_score": 85,
                        "reason_tags": ["快速变现", "高需求品类"]
                    }
                },
                "details": {
                    "note": "这是临时的模拟数据，等待ProcessingAgent完成后将提供真实处理结果"
                }
            }
            
            # 更新结果
            task.status = 'SUCCESS'
            task.result = mock_result
            await self.db.commit()
            
            app_logger.info(f"任务 {task.id} 模拟处理完成")
            
        except Exception as e:
            app_logger.error(f"模拟处理失败: {e}")
            task.status = 'FAILED'
            task.error_message = f"模拟处理失败: {str(e)}"
            await self.db.commit() 