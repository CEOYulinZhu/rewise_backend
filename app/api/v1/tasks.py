"""
任务相关API路由

处理物品处置任务的创建、状态查询等接口
"""

from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies.database import get_database
from app.api.dependencies.validation import validate_task_create_data, validate_task_id
from app.core.logger import app_logger
from app.models.task import (
    TaskCreate, TaskResponse, TaskStatus
)
from app.services.task_service import TaskService

router = APIRouter(prefix="/tasks", tags=["tasks"])


@router.post("/", response_model=TaskResponse, status_code=status.HTTP_202_ACCEPTED)
async def create_task(
        background_tasks: BackgroundTasks,
        db: AsyncSession = Depends(get_database),
        validated_task_data: TaskCreate = Depends(validate_task_create_data)
) -> TaskResponse:
    """
    创建新的物品处置任务
    
    - **image_url**: 物品图片URL（可选）
    - **text_description**: 物品文字描述（可选）
    - **user_location**: 用户地理位置（可选）
    
    至少需要提供图片或文字描述其中一项
    """

    try:
        # 创建任务记录
        task_service = TaskService(db)
        task_id = await task_service.create_task(validated_task_data)

        # 添加后台任务处理
        background_tasks.add_task(task_service.process_task_async, task_id)

        app_logger.info(f"任务创建成功: {task_id}")
        return TaskResponse(task_id=str(task_id))

    except Exception as e:
        app_logger.error(f"创建任务失败: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="任务创建失败，请稍后重试"
        )


@router.get("/{task_id}", response_model=TaskStatus)
async def get_task_status(
        task_id: str,
        db: AsyncSession = Depends(get_database)
) -> TaskStatus:
    """
    获取任务状态和进度
    
    - **task_id**: 任务ID
    
    返回任务当前状态：
    - PENDING: 等待处理
    - PROGRESS: 处理中（包含进度信息）
    - SUCCESS: 完成（包含结果数据）
    - FAILED: 失败（包含错误信息）
    """

    # 验证任务ID格式
    task_uuid = validate_task_id(task_id)

    try:
        # 查询任务状态
        task_service = TaskService(db)
        task_status = await task_service.get_task_status(task_uuid)

        if not task_status:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="任务不存在"
            )

        return task_status

    except HTTPException:
        raise
    except Exception as e:
        app_logger.error(f"查询任务状态失败: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="查询任务状态失败，请稍后重试"
        )
