"""
闲置物语后端主应用

FastAPI应用的启动入口
"""

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import uvicorn
import time

from app.core.config import settings
from app.core.logger import app_logger
from app.database.connection import create_tables, close_db
from app.api.v1.tasks import router as tasks_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    
    # 启动时执行
    app_logger.info("正在启动闲置物语后端服务...")
    
    try:
        # 创建数据库表
        await create_tables()
        app_logger.info("数据库初始化完成")
        
        yield
        
    finally:
        # 关闭时执行
        app_logger.info("正在关闭闲置物语后端服务...")
        await close_db()
        app_logger.info("数据库连接已关闭")


# 创建FastAPI应用实例
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="基于AI的智能物品处置建议系统",
    docs_url="/docs" if settings.debug else None,
    redoc_url="/redoc" if settings.debug else None,
    lifespan=lifespan
)

# 配置CORS中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_hosts if settings.allowed_hosts != ["*"] else ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# 请求日志中间件
@app.middleware("http")
async def log_requests(request: Request, call_next):
    """记录请求日志"""
    
    start_time = time.time()
    
    # 记录请求信息
    app_logger.info(f"收到请求: {request.method} {request.url}")
    
    # 处理请求
    response = await call_next(request)
    
    # 计算处理时间
    process_time = time.time() - start_time
    
    # 记录响应信息
    app_logger.info(
        f"请求完成: {request.method} {request.url} - "
        f"状态码: {response.status_code} - "
        f"耗时: {process_time:.3f}s"
    )
    
    return response


# 健康检查接口
@app.get("/health")
async def health_check():
    """健康检查"""
    return {
        "status": "healthy",
        "service": settings.app_name,
        "version": settings.app_version
    }


# 注册API路由
app.include_router(tasks_router, prefix=settings.api_prefix)


# 根路径
@app.get("/")
async def root():
    """根路径欢迎信息"""
    return {
        "message": f"欢迎使用{settings.app_name}",
        "version": settings.app_version,
        "docs": "/docs" if settings.debug else "API文档在生产环境中不可用"
    }


if __name__ == "__main__":
    # 开发环境启动
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.debug,
        log_level=settings.log_level.lower()
    ) 