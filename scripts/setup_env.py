#!/usr/bin/env python3
"""
开发环境启动脚本

用于检查环境配置、初始化开发环境并启动服务
"""

import os
import sys
import subprocess
from pathlib import Path

# 项目根目录
BASE_DIR = Path(__file__).resolve().parent.parent


def run_command(cmd: str, description: str, cwd: Path = None) -> bool:
    """运行PowerShell命令"""
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(
            ["powershell", "-Command", cmd], 
            cwd=cwd or BASE_DIR,
            check=True, 
            capture_output=True, 
            text=True,
            encoding='utf-8'
        )
        if result.stdout:
            print(f"✅ {result.stdout.strip()}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} 失败: {e}")
        if e.stderr:
            print(f"错误详情: {e.stderr}")
        return False


def check_environment():
    """检查环境配置"""
    print("🔍 检查环境配置...")
    
    # 检查.env文件是否存在
    env_file = BASE_DIR / ".env"
    if not env_file.exists():
        print("❌ .env文件不存在")
        print("💡 请确保项目根目录下有 .env 配置文件")
        print("   可以参考 env.example 文件创建")
        return False
    
    print("✅ .env配置文件存在")
    return True


def setup_directories():
    """创建必要的目录结构"""
    print("📁 创建必要的目录...")
    
    directories = [
        BASE_DIR / "data" / "chroma_db",
        BASE_DIR / "data" / "uploads", 
        BASE_DIR / "logs",
        BASE_DIR / "init-db"
    ]
    
    for directory in directories:
        directory.mkdir(parents=True, exist_ok=True)
        print(f"✅ 已创建目录: {directory}")
    
    return True


def check_dependencies():
    """检查依赖服务"""
    print("🔍 检查依赖服务...")
    
    # 检查Docker是否运行
    if not run_command("docker info", "检查Docker状态"):
        print("⚠️  Docker未运行，请启动Docker Desktop")
        return False
    
    # 检查docker-compose文件
    if not (BASE_DIR / "docker-compose.yml").exists():
        print("❌ docker-compose.yml文件不存在")
        return False
    
    return True


def start_infrastructure():
    """启动基础设施服务"""
    print("🐳 启动基础设施服务...")
    
    # 启动Docker Compose服务
    if not run_command("docker-compose up -d", "启动PostgreSQL和Redis"):
        return False
    
    # 等待服务启动
    print("⏳ 等待数据库服务启动...")
    import time
    time.sleep(5)
    
    return True


def start_application():
    """启动应用"""
    print("🎯 启动FastAPI应用...")
    print("📋 访问地址:")
    print("   • 应用主页: http://localhost:8000")
    print("   • API文档: http://localhost:8000/docs")
    print("   • 健康检查: http://localhost:8000/health")
    print("\n💡 数据库表将在应用启动时自动创建")
    print("🔄 启动中...")
    
    # 直接运行主应用
    os.chdir(BASE_DIR)
    os.system("python main.py")


def main():
    """主函数"""
    print("=" * 50)
    print("🏠 闲置物语后端开发环境管理")
    print("=" * 50)
    
    if len(sys.argv) > 1:
        command = sys.argv[1]
        
        if command == "setup":
            # 仅设置环境
            if not check_environment():
                sys.exit(1)
            
            if not setup_directories():
                sys.exit(1)
            
            print("\n🎉 环境设置完成！")
            print("运行 'python scripts/setup_env.py start' 启动服务")
            
        elif command == "start":
            # 完整启动流程
            if not check_environment():
                sys.exit(1)
            
            if not setup_directories():
                sys.exit(1)
            
            if not check_dependencies():
                print("\n💡 请先执行以下步骤:")
                print("1. 安装并启动Docker Desktop")
                print("2. 确保docker-compose.yml文件存在")
                sys.exit(1)
            
            if not start_infrastructure():
                sys.exit(1)
            
            start_application()
            
        else:
            print(f"❌ 未知命令: {command}")
            print("使用方法:")
            print("  python scripts/setup_env.py setup  # 检查环境并创建目录")
            print("  python scripts/setup_env.py start  # 完整启动")
    
    else:
        # 默认行为：仅设置环境
        if not check_environment():
            sys.exit(1)
        
        if not setup_directories():
            sys.exit(1)
        
        print("\n🎉 环境检查完成！")
        print("\n📋 接下来的步骤:")
        print("1. 启动Docker Desktop")
        print("2. 运行: python scripts/setup_env.py start")


if __name__ == "__main__":
    main() 