"""
Celery异步任务应用

配置和管理后台异步任务
"""

from celery import Celery
from app.core.config import settings
from app.core.logger import app_logger

# 创建Celery应用实例
celery_app = Celery(
    "xianzhiwuyu",
    broker=settings.celery_broker_url,
    backend=settings.celery_result_backend,
    include=["app.tasks"]  # 包含任务模块
)

# Celery配置
celery_app.conf.update(
    # 任务序列化
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    
    # 时区设置
    timezone="Asia/Shanghai",
    enable_utc=True,
    
    # 任务路由
    task_routes={
        "app.tasks.process_item_task": {"queue": "item_processing"},
        "app.tasks.crawl_market_data": {"queue": "data_crawling"},
    },
    
    # 任务执行配置
    task_soft_time_limit=300,  # 5分钟软限制
    task_time_limit=600,       # 10分钟硬限制
    worker_prefetch_multiplier=1,
    
    # 结果过期时间
    result_expires=3600,  # 1小时
    
    # 重试配置
    task_acks_late=True,
    worker_disable_rate_limits=False,
)

# 任务发现
celery_app.autodiscover_tasks()

if __name__ == "__main__":
    celery_app.start() 