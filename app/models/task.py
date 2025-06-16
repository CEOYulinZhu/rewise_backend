"""
任务相关数据模型

包含处理任务的SQLAlchemy模型和Pydantic模式
"""

import uuid
from typing import Optional, Dict, Any
from datetime import datetime
from sqlalchemy import Column, String, Text, DateTime, func
from sqlalchemy.dialects.postgresql import UUID, JSONB
from geoalchemy2 import Geometry
from pydantic import BaseModel, Field
from app.database.connection import Base


class ProcessingTask(Base):
    """处理任务表"""
    __tablename__ = "processing_tasks"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    status = Column(String(20), nullable=False, default='PENDING', index=True)
    
    # 输入参数
    input_image_url = Column(Text, nullable=True)
    input_text_description = Column(Text, nullable=True) 
    input_user_location = Column(Geometry('POINT', srid=4326), nullable=True)
    
    # 输出结果
    result = Column(JSONB, nullable=True)
    
    # 元数据
    error_message = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())


class RecyclingChannel(Base):
    """回收渠道表"""
    __tablename__ = "recycling_channels"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False)
    category = Column(String(100), nullable=False, index=True)
    location = Column(Geometry('POINT', srid=4326), nullable=True)
    address = Column(Text, nullable=True)
    city = Column(String(100), nullable=True)
    province = Column(String(100), nullable=True)
    contact_info = Column(Text, nullable=True)
    website = Column(Text, nullable=True)
    operating_hours = Column(Text, nullable=True)
    details = Column(Text, nullable=True)
    is_active = Column(String(10), nullable=False, default='true')
    source = Column(String(100), nullable=True)


class OnlineRecyclingPlatform(Base):
    """线上回收平台表"""
    __tablename__ = "online_recycling_platforms"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False, unique=True)
    icon_url = Column(Text, nullable=True)
    description = Column(Text, nullable=True)
    tags = Column(JSONB, nullable=True)  # 存储标签数组
    user_count_desc = Column(String(50), nullable=True)
    rating = Column(String(10), nullable=True)  # 改为字符串类型避免精度问题
    website = Column(Text, nullable=True)
    platform_type = Column(String(50), nullable=True)


# Pydantic 模式定义

class TaskCreate(BaseModel):
    """创建任务请求模式"""
    image_url: Optional[str] = None
    text_description: Optional[str] = None
    user_location: Optional[Dict[str, float]] = None  # {"lat": float, "lon": float}
    
    class Config:
        json_schema_extra = {
            "example": {
                "image_url": "https://example.com/image.jpg",
                "text_description": "一件旧羊毛衫，袖口有些磨损",
                "user_location": {"lat": 39.9042, "lon": 116.4074}
            }
        }


class TaskResponse(BaseModel):
    """任务响应模式"""
    task_id: str
    
    class Config:
        json_schema_extra = {
            "example": {
                "task_id": "123e4567-e89b-12d3-a456-426614174000"
            }
        }


class TaskStatus(BaseModel):
    """任务状态模式"""
    status: str
    progress: Optional[Dict[str, Any]] = None
    data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "status": "PROGRESS",
                "progress": {
                    "step": 2,
                    "message": "正在评估处置路径..."
                }
            }
        }


class ProcessingResult(BaseModel):
    """处理结果模式"""
    overview: Dict[str, Any]
    details: Dict[str, Any]
    
    class Config:
        json_schema_extra = {
            "example": {
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
                    "creative_makeover": {
                        "overview": {
                            "step_count": 5,
                            "estimated_time": "约2小时",
                            "difficulty": "中等"
                        }
                    }
                }
            }
        } 