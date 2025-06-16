"""
输入验证依赖注入

提供请求参数验证等验证相关的依赖项
"""

from fastapi import HTTPException, status
from app.core.logger import app_logger


async def validate_task_input(
    image_url: str = None,
    text_description: str = None
) -> dict:
    """验证任务输入参数"""
    if not image_url and not text_description:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="必须提供图片URL或文字描述中的至少一项"
        )
    
    return {
        "image_url": image_url,
        "text_description": text_description
    } 