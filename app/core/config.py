"""
应用配置模块

使用pydantic-settings管理所有环境变量和配置项
"""

from typing import Optional, List
from pydantic import Field
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
    secret_key: str = Field(default="test-secret-key-for-development", env="SECRET_KEY")
    allowed_hosts: str = Field(default="localhost,127.0.0.1", env="ALLOWED_HOSTS")
    
    @property
    def allowed_hosts_list(self) -> List[str]:
        """将允许的主机字符串转换为列表"""
        if self.allowed_hosts == "*":
            return ["*"]
        return [host.strip() for host in self.allowed_hosts.split(",") if host.strip()]
    
    # 数据库配置
    database_url: str = Field(default="postgresql+asyncpg://user:pass@localhost:5432/testdb", env="DATABASE_URL")
    postgres_user: str = Field(default="testuser", env="POSTGRES_USER")
    postgres_password: str = Field(default="testpass", env="POSTGRES_PASSWORD") 
    postgres_db: str = Field(default="testdb", env="POSTGRES_DB")
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
    lanxin_app_id: str = Field(env="LANXIN_APP_ID")
    lanxin_app_key: str = Field(env="LANXIN_APP_KEY")
    lanxin_api_base_url: str = Field(default="https://api-ai.vivo.com.cn/vivogpt/completions", env="LANXIN_API_BASE_URL")
    lanxin_text_model: str = Field(default="vivo-BlueLM-TB-Pro", env="LANXIN_TEXT_MODEL")
    
    # 高德地图API配置
    amap_api_key: str = Field(env="AMAP_API_KEY")
    amap_api_base_url: str = Field(default="https://restapi.amap.com/v5/place/around", env="AMAP_API_BASE_URL")
    amap_timeout: int = Field(default=30, env="AMAP_TIMEOUT")
    amap_max_retries: int = Field(default=3, env="AMAP_MAX_RETRIES")
    
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
    

    class Config:
        env_file = BASE_DIR / ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


# 全局设置实例
settings = Settings()


def get_settings() -> Settings:
    """获取设置实例"""
    return settings 