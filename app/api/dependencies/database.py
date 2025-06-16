"""
数据库依赖注入

提供数据库会话等数据库相关的依赖项
"""

from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession
from app.database.connection import get_db_session


async def get_database() -> AsyncGenerator[AsyncSession, None]:
    """获取数据库会话依赖"""
    async for session in get_db_session():
        yield session 