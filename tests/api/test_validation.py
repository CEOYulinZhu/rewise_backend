"""
验证依赖注入测试

测试app.api.dependencies.validation模块的功能
"""

import pytest
import uuid
from fastapi import HTTPException
from app.api.dependencies.validation import (
    validate_task_create_data,
    validate_task_id,
    _is_valid_url,
    _is_valid_location
)
from app.models.task import TaskCreate


class TestValidateTaskCreateData:
    """测试任务创建数据验证"""
    
    def test_valid_task_data_with_image_url(self):
        """测试有效的任务数据（包含图片URL）"""
        task_data = TaskCreate(
            image_url="https://example.com/image.jpg",
            text_description="测试描述"
        )
        result = validate_task_create_data(task_data)
        assert result == task_data
    
    def test_valid_task_data_with_text_only(self):
        """测试有效的任务数据（仅包含文字描述）"""
        task_data = TaskCreate(
            text_description="这是一个有效的描述"
        )
        result = validate_task_create_data(task_data)
        assert result == task_data
    
    def test_invalid_task_data_no_input(self):
        """测试无效的任务数据（没有输入）"""
        task_data = TaskCreate()
        with pytest.raises(HTTPException) as exc_info:
            validate_task_create_data(task_data)
        assert exc_info.value.status_code == 400
        assert "必须提供图片URL或文字描述中的至少一项" in exc_info.value.detail
    
    def test_invalid_url_format(self):
        """测试无效的URL格式"""
        task_data = TaskCreate(
            image_url="invalid-url"
        )
        with pytest.raises(HTTPException) as exc_info:
            validate_task_create_data(task_data)
        assert exc_info.value.status_code == 400
        assert "图片URL格式无效" in exc_info.value.detail
    
    def test_invalid_text_too_short(self):
        """测试文字描述太短"""
        task_data = TaskCreate(
            text_description="a"
        )
        with pytest.raises(HTTPException) as exc_info:
            validate_task_create_data(task_data)
        assert exc_info.value.status_code == 400
        assert "文字描述至少需要2个字符" in exc_info.value.detail
    
    def test_invalid_text_too_long(self):
        """测试文字描述太长"""
        task_data = TaskCreate(
            text_description="a" * 1001
        )
        with pytest.raises(HTTPException) as exc_info:
            validate_task_create_data(task_data)
        assert exc_info.value.status_code == 400
        assert "文字描述不能超过1000个字符" in exc_info.value.detail
    
    def test_invalid_location(self):
        """测试无效的地理位置"""
        task_data = TaskCreate(
            text_description="测试描述",
            user_location={"lat": 200, "lon": 300}  # 超出有效范围
        )
        with pytest.raises(HTTPException) as exc_info:
            validate_task_create_data(task_data)
        assert exc_info.value.status_code == 400
        assert "用户位置格式无效" in exc_info.value.detail


class TestValidateTaskId:
    """测试任务ID验证"""
    
    def test_valid_uuid(self):
        """测试有效的UUID"""
        valid_uuid = str(uuid.uuid4())
        result = validate_task_id(valid_uuid)
        assert isinstance(result, uuid.UUID)
        assert str(result) == valid_uuid
    
    def test_invalid_uuid(self):
        """测试无效的UUID"""
        with pytest.raises(HTTPException) as exc_info:
            validate_task_id("invalid-uuid")
        assert exc_info.value.status_code == 400
        assert "无效的任务ID格式" in exc_info.value.detail


class TestHelperFunctions:
    """测试辅助函数"""
    
    def test_is_valid_url_valid(self):
        """测试有效URL"""
        assert _is_valid_url("https://example.com/image.jpg") is True
        assert _is_valid_url("http://example.com") is True
    
    def test_is_valid_url_invalid(self):
        """测试无效URL"""
        assert _is_valid_url("invalid-url") is False
        assert _is_valid_url("") is False
        assert _is_valid_url("ftp://example.com") is True  # 有scheme和netloc
    
    def test_is_valid_location_valid(self):
        """测试有效地理位置"""
        assert _is_valid_location({"lat": 39.9042, "lon": 116.4074}) is True
        assert _is_valid_location({"lat": 0, "lon": 0}) is True
        assert _is_valid_location({"lat": -90, "lon": -180}) is True
        assert _is_valid_location({"lat": 90, "lon": 180}) is True
    
    def test_is_valid_location_invalid(self):
        """测试无效地理位置"""
        assert _is_valid_location({"lat": 200, "lon": 300}) is False
        assert _is_valid_location({"lat": 39.9042}) is False  # 缺少lon
        assert _is_valid_location({"lon": 116.4074}) is False  # 缺少lat
        assert _is_valid_location({}) is False
        assert _is_valid_location("not a dict") is False 