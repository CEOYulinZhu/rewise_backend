"""
Alembic环境配置

数据库迁移的环境设置
"""

import asyncio
from logging.config import fileConfig
from sqlalchemy import pool
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import async_engine_from_config
from alembic import context
import os
import sys

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# 导入模型
from app.database.connection import Base
from app.models.task import ProcessingTask, RecyclingChannel, OnlineRecyclingPlatform

# 导入设置
from app.core.config import settings

# Alembic配置对象
config = context.config

# 设置数据库URL
config.set_main_option("sqlalchemy.url", settings.database_url)

# 解释配置文件的日志记录
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# 添加模型的MetaData对象用于'autogenerate'支持
target_metadata = Base.metadata


def run_migrations_offline() -> None:
    """在'离线'模式下运行迁移。
    
    这将配置上下文仅与URL一起，而不需要创建Engine，
    尽管在这里仍需要Engine，但我们不创建与数据库的连接。
    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection: Connection) -> None:
    """运行迁移"""
    context.configure(connection=connection, target_metadata=target_metadata)

    with context.begin_transaction():
        context.run_migrations()


async def run_async_migrations() -> None:
    """在'online'模式下运行异步迁移。"""
    
    configuration = config.get_section(config.config_ini_section)
    configuration["sqlalchemy.url"] = settings.database_url
    
    connectable = async_engine_from_config(
        configuration,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)

    await connectable.dispose()


def run_migrations_online() -> None:
    """在'online'模式下运行迁移。"""
    asyncio.run(run_async_migrations())


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()