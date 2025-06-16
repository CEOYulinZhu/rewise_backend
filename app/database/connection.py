"""
数据库连接管理

提供PostgreSQL的异步连接池管理
"""

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base
from app.core.config import settings
from app.core.logger import app_logger

# 创建异步数据库引擎
engine = create_async_engine(
    settings.database_url,
    echo=settings.debug,  # 开发环境下输出SQL语句
    pool_size=20,
    max_overflow=0,
    pool_recycle=3600,  # 1小时回收连接
    pool_pre_ping=True,  # 连接前测试
)

# 创建会话工厂
async_session_maker = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False
)

# ORM基类
Base = declarative_base()


async def get_db_session() -> AsyncSession:
    """获取数据库会话"""
    async with async_session_maker() as session:
        try:
            yield session
        except Exception as e:
            app_logger.error(f"数据库会话错误: {e}")
            await session.rollback()
            raise
        finally:
            await session.close()


async def create_tables():
    """创建所有数据库表"""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        app_logger.info("数据库表创建完成")


async def close_db():
    """关闭数据库连接"""
    await engine.dispose()
    app_logger.info("数据库连接已关闭") 