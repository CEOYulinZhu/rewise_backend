"""
输入验证依赖注入

提供请求参数验证等验证相关的依赖项
"""

import uuid
from typing import Dict

from fastapi import HTTPException, status

from app.core.logger import app_logger
from app.models.task import TaskCreate
from app.models.processing_master_models import ProcessingMasterRequest


def validate_task_create_data(task_data: TaskCreate) -> TaskCreate:
    """验证任务创建数据"""
    app_logger.debug(f"开始验证任务创建数据: image_url={bool(task_data.image_url)}, text_description={bool(task_data.text_description)}")
    
    # 验证输入
    if not task_data.image_url and not task_data.text_description:
        app_logger.warning("任务创建验证失败: 未提供图片URL或文字描述")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="必须提供图片URL或文字描述中的至少一项"
        )
    
    # 验证图片URL格式（如果提供）
    if task_data.image_url:
        if not _is_valid_url(task_data.image_url):
            app_logger.warning(f"任务创建验证失败: 图片URL格式无效 - {task_data.image_url}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="图片URL格式无效"
            )
    
    # 验证文字描述长度（如果提供）
    if task_data.text_description:
        text_length = len(task_data.text_description.strip())
        if text_length < 2:
            app_logger.warning(f"任务创建验证失败: 文字描述太短 - 长度: {text_length}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="文字描述至少需要2个字符"
            )
        if len(task_data.text_description) > 1000:
            app_logger.warning(f"任务创建验证失败: 文字描述太长 - 长度: {len(task_data.text_description)}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="文字描述不能超过1000个字符"
            )
    
    # 验证用户位置（如果提供）
    if task_data.user_location:
        if not _is_valid_location(task_data.user_location):
            app_logger.warning(f"任务创建验证失败: 用户位置格式无效 - {task_data.user_location}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="用户位置格式无效，应包含有效的经纬度"
            )
    
    app_logger.debug("任务创建数据验证通过")
    return task_data


def validate_task_id(task_id: str) -> uuid.UUID:
    """验证任务ID格式"""
    app_logger.debug(f"开始验证任务ID: {task_id}")
    
    try:
        task_uuid = uuid.UUID(task_id)
        app_logger.debug(f"任务ID验证通过: {task_uuid}")
        return task_uuid
    except ValueError:
        app_logger.warning(f"任务ID验证失败: 格式无效 - {task_id}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="无效的任务ID格式"
        )


def _is_valid_url(url: str) -> bool:
    """验证URL格式，支持HTTP/HTTPS URL和data URI"""
    try:
        from urllib.parse import urlparse
        result = urlparse(url)
        
        # 支持data URI格式 (data:image/jpeg;base64,...)
        if result.scheme == 'data':
            # 验证data URI格式
            if ',' in url:
                header, data = url.split(',', 1)
                # 基本格式验证：data:mediatype;encoding,data
                if header.startswith('data:') and ';base64' in header:
                    return True
            return False
        
        # 标准HTTP/HTTPS URL验证
        return all([result.scheme, result.netloc])
    except Exception:
        return False


def _is_valid_location(location: Dict[str, float]) -> bool:
    """验证地理位置格式"""
    try:
        if not isinstance(location, dict):
            return False
        
        lat = location.get('lat')
        lon = location.get('lon')
        
        if lat is None or lon is None:
            return False
        
        # 验证经纬度范围
        if not (-90 <= lat <= 90) or not (-180 <= lon <= 180):
            return False
        
        return True
    except Exception:
        return False


def validate_processing_master_request(request_data: dict) -> ProcessingMasterRequest:
    """验证WebSocket处理请求数据"""
    app_logger.debug(f"开始验证WebSocket处理请求: image_url={bool(request_data.get('image_url'))}, text_description={bool(request_data.get('text_description'))}")
    
    # 处理前端传递的undefined值
    image_url = request_data.get('image_url')
    text_description = request_data.get('text_description')
    user_location = request_data.get('user_location')
    
    # 清理undefined值
    if image_url in ['undefined', 'null', None]:
        image_url = None
    if text_description in ['undefined', 'null', None]:
        text_description = None
    if user_location in ['undefined', 'null', None]:
        user_location = None
    
    # 验证至少提供一项输入
    if not image_url and not text_description:
        app_logger.warning("WebSocket请求验证失败: 未提供图片URL或文字描述")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="必须提供图片URL或文字描述中的至少一项"
        )
    
    # 验证图片URL格式（如果提供）
    if image_url:
        if not _is_valid_url(image_url):
            app_logger.warning(f"WebSocket请求验证失败: 图片URL格式无效 - {image_url[:50]}...")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="图片URL格式无效"
            )
    
    # 验证文字描述长度（如果提供）
    if text_description:
        text_length = len(text_description.strip())
        if text_length < 2:
            app_logger.warning(f"WebSocket请求验证失败: 文字描述太短 - 长度: {text_length}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="文字描述至少需要2个字符"
            )
        if len(text_description) > 1000:
            app_logger.warning(f"WebSocket请求验证失败: 文字描述太长 - 长度: {len(text_description)}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="文字描述不能超过1000个字符"
            )
    
    # 验证用户位置（如果提供）
    if user_location:
        if not _is_valid_location(user_location):
            app_logger.warning(f"WebSocket请求验证失败: 用户位置格式无效 - {user_location}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="用户位置格式无效，应包含有效的经纬度"
            )
    
    # 创建ProcessingMasterRequest对象
    try:
        request = ProcessingMasterRequest(
            image_url=image_url,
            text_description=text_description,
            user_location=user_location,
            enable_parallel=request_data.get('enable_parallel', True),
            max_results_per_platform=request_data.get('max_results_per_platform', 10)
        )
        app_logger.debug("WebSocket处理请求验证通过")
        return request
    except Exception as e:
        app_logger.warning(f"WebSocket请求验证失败: Pydantic验证错误 - {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"请求参数格式错误: {str(e)}"
        )