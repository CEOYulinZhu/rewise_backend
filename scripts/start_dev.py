#!/usr/bin/env python3
"""
开发环境启动脚本

用于启动完整的开发环境，包括数据库迁移、数据初始化等
"""

import asyncio
import subprocess
import sys
import os
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from app.core.config import settings
from app.core.logger import app_logger


async def check_environment():
    """检查环境配置"""
    app_logger.info("检查环境配置...")
    
    # 检查必要的环境变量
    required_vars = [
        "DATABASE_URL",
        "REDIS_URL", 
        "LANXIN_API_KEY",
        "SECRET_KEY"
    ]
    
    missing_vars = []
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        app_logger.error(f"缺少必要的环境变量: {', '.join(missing_vars)}")
        app_logger.info("请创建.env文件并设置这些变量")
        return False
    
    app_logger.info("环境配置检查通过")
    return True


def run_command(cmd, description):
    """运行命令"""
    app_logger.info(f"执行: {description}")
    try:
        result = subprocess.run(cmd, shell=True, check=True, capture_output=True, text=True)
        if result.stdout:
            app_logger.info(result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        app_logger.error(f"{description} 失败: {e}")
        if e.stderr:
            app_logger.error(e.stderr)
        return False


async def setup_database():
    """设置数据库"""
    app_logger.info("设置数据库...")
    
    # 运行数据库迁移
    if not run_command("alembic upgrade head", "数据库迁移"):
        return False
    
    app_logger.info("数据库设置完成")
    return True


async def start_services():
    """启动服务"""
    app_logger.info("启动开发服务...")
    
    # 启动主应用
    app_logger.info("启动FastAPI应用...")
    app_logger.info("访问 http://localhost:8000 查看应用")
    app_logger.info("访问 http://localhost:8000/docs 查看API文档")
    
    # 运行主应用
    os.system("python main.py")


async def main():
    """主函数"""
    app_logger.info("=== 闲置物语后端开发环境启动 ===")
    
    # 检查环境
    if not await check_environment():
        sys.exit(1)
    
    # 设置数据库
    if not await setup_database():
        sys.exit(1)
    
    # 启动服务
    await start_services()


if __name__ == "__main__":
    asyncio.run(main()) 