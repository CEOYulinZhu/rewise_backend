"""
API依赖注入模块

包含FastAPI的所有依赖项，如数据库会话、认证、验证等
"""

from .auth import *
from .database import *
from .validation import * 