"""
日志配置模块

使用loguru进行统一的日志管理
"""

import sys
from pathlib import Path
from loguru import logger
from app.core.config import settings


def setup_logging():
    """设置日志配置"""
    # 移除默认的日志处理器
    logger.remove()
    
    # 控制台日志
    logger.add(
        sys.stdout,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
        level=settings.log_level,
        colorize=True
    )
    
    # 文件日志
    log_file_path = Path(settings.log_file)
    log_file_path.parent.mkdir(parents=True, exist_ok=True)
    
    logger.add(
        log_file_path,
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
        level=settings.log_level,
        rotation="100 MB",
        retention="30 days",
        compression="zip",
        encoding="utf-8"
    )
    
    return logger


# 初始化日志
app_logger = setup_logging() 