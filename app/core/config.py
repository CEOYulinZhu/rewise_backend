"""
应用配置模块

使用pydantic-settings管理所有环境变量和配置项
"""

from typing import Optional, List
from pydantic import BaseSettings, Field
from pydantic_settings import BaseSettings
import os
from pathlib import Path

# 项目根目录
BASE_DIR = Path(__file__).resolve().parent.parent.parent


class Settings(BaseSettings):
    """应用设置"""
    
    # 应用基本信息
    app_name: str = Field(default="闲置物语后端", env="APP_NAME")
    app_version: str = Field(default="1.0.0", env="APP_VERSION")
    debug: bool = Field(default=False, env="DEBUG")
    api_prefix: str = Field(default="/api/v1", env="API_PREFIX")
    
    # 安全配置
    secret_key: str = Field(env="SECRET_KEY")
    allowed_hosts: List[str] = Field(default=["localhost", "127.0.0.1"], env="ALLOWED_HOSTS")
    
    # 数据库配置
    database_url: str = Field(env="DATABASE_URL")
    postgres_user: str = Field(env="POSTGRES_USER")
    postgres_password: str = Field(env="POSTGRES_PASSWORD") 
    postgres_db: str = Field(env="POSTGRES_DB")
    postgres_host: str = Field(default="localhost", env="POSTGRES_HOST")
    postgres_port: int = Field(default=5432, env="POSTGRES_PORT")
    
    # Redis配置
    redis_url: str = Field(default="redis://localhost:6379/0", env="REDIS_URL")
    celery_broker_url: str = Field(default="redis://localhost:6379/0", env="CELERY_BROKER_URL")
    celery_result_backend: str = Field(default="redis://localhost:6379/0", env="CELERY_RESULT_BACKEND")
    
    # ChromaDB配置
    chroma_db_path: str = Field(default=str(BASE_DIR / "data" / "chroma_db"), env="CHROMA_DB_PATH")
    chroma_collection_name: str = Field(default="item_knowledge", env="CHROMA_COLLECTION_NAME")
    
    # 蓝心大模型API配置
    lanxin_api_key: str = Field(env="LANXIN_API_KEY")
    lanxin_api_base_url: str = Field(default="https://api.lanxin.ai/v1", env="LANXIN_API_BASE_URL")
    lanxin_vision_model: str = Field(default="lanxin-vision-pro", env="LANXIN_VISION_MODEL")
    lanxin_text_model: str = Field(default="lanxin-chat-pro", env="LANXIN_TEXT_MODEL")
    
    # 文件存储配置
    upload_dir: str = Field(default=str(BASE_DIR / "data" / "uploads"), env="UPLOAD_DIR")
    max_file_size: int = Field(default=10485760, env="MAX_FILE_SIZE")  # 10MB
    
    # 爬虫配置
    crawler_user_agent: str = Field(
        default="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        env="CRAWLER_USER_AGENT"
    )
    crawler_timeout: int = Field(default=30, env="CRAWLER_TIMEOUT")
    crawler_max_retries: int = Field(default=3, env="CRAWLER_MAX_RETRIES")
    
    # 日志配置
    log_level: str = Field(default="INFO", env="LOG_LEVEL")
    log_file: str = Field(default=str(BASE_DIR / "logs" / "app.log"), env="LOG_FILE")
    
    # 第三方平台API配置
    xianyu_api_base: str = Field(default="https://h5api.m.taobao.com", env="XIANYU_API_BASE")
    zhuanzhuan_api_base: str = Field(default="https://app.zhuanzhuan.com", env="ZHUANZHUAN_API_BASE")
    dewu_api_base: str = Field(default="https://app.dewu.com", env="DEWU_API_BASE")
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


# 全局设置实例
settings = Settings()


def get_settings() -> Settings:
    """获取设置实例"""
    return settings 