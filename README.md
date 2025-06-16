# 闲置物语后端系统

基于FastAPI + Celery + PostgreSQL + Redis + LangChain的智能物品处置建议系统。

## 🎯 项目简介

闲置物语是一个基于人工智能的物品处置建议系统，能够通过图片识别或文字描述分析用户的闲置物品，并提供个性化的处置建议，包括创意改造、回收捐赠、二手交易等多种方案。

## 🏗️ 技术架构

### 核心技术栈
- **Web框架**: FastAPI (高性能异步API框架)
- **依赖注入**: FastAPI Depends (模块化的依赖管理)
- **任务队列**: Celery + Redis (处理耗时的AI分析任务)
- **数据库**: PostgreSQL + SQLAlchemy (关系型数据存储)
- **向量数据库**: ChromaDB (知识库检索)
- **AI服务**: 蓝心大模型 (图像识别和文本分析)
- **爬虫**: httpx (市场数据采集)

### 系统架构
```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   前端应用       │───▶│   FastAPI       │───▶│   AI Agent      │
│                │    │   Web服务       │    │   处理层         │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                               │                        │
                               ▼                        ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   PostgreSQL    │    │   Redis         │    │   蓝心大模型     │
│   主数据库       │    │   缓存+队列      │    │   AI服务        │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                               │                        │
                               ▼                        ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   ChromaDB      │    │   Celery        │    │   市场爬虫       │
│   知识向量库     │    │   异步任务       │    │   数据采集       │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## 📁 项目结构

```
闲置物语-后端/
├── app/                        # 主应用目录
│   ├── __init__.py
│   ├── agents/                 # AI Agent模块
│   │   ├── __init__.py
│   │   └── processing_agent.py # 主处理Agent
│   ├── api/                    # API接口层
│   │   ├── __init__.py
│   │   ├── dependencies/       # 依赖注入模块
│   │   │   ├── __init__.py
│   │   │   ├── auth.py         # 认证相关依赖
│   │   │   ├── database.py     # 数据库相关依赖
│   │   │   └── validation.py   # 验证相关依赖
│   │   └── v1/                 # V1版本API
│   │       ├── __init__.py
│   │       └── tasks.py        # 任务相关接口
│   ├── core/                   # 核心配置
│   │   ├── __init__.py
│   │   ├── config.py           # 应用配置
│   │   └── logger.py           # 日志配置
│   ├── database/               # 数据库层
│   │   ├── __init__.py
│   │   └── connection.py       # 数据库连接
│   ├── models/                 # 数据模型
│   │   ├── __init__.py
│   │   └── task.py             # 任务模型
│   ├── services/               # 服务层
│   │   ├── __init__.py
│   │   ├── task_service.py     # 任务服务
│   │   ├── crawler/            # 爬虫服务
│   │   │   ├── __init__.py
│   │   │   └── market_crawler.py
│   │   ├── llm/                # LLM服务
│   │   │   ├── __init__.py
│   │   │   └── lanxin_service.py
│   │   └── rag/                # RAG服务
│   │       ├── __init__.py
│   │       └── knowledge_service.py
│   └── utils/                  # 工具函数
├── alembic/                    # 数据库迁移
│   ├── versions/
│   └── env.py
├── data/                       # 数据目录
│   ├── chroma_db/              # ChromaDB数据
│   └── uploads/                # 上传文件
├── docs/                       # 文档
├── logs/                       # 日志文件
├── scripts/                    # 脚本文件
│   └── start_dev.py            # 开发启动脚本
├── tests/                      # 测试文件
│   ├── api/
│   ├── services/
│   └── agents/
├── main.py                     # FastAPI应用入口
├── celery_app.py              # Celery应用配置
├── requirements.txt           # Python依赖
├── alembic.ini               # Alembic配置
├── env.example               # 环境变量示例
└── README.md                 # 项目说明
```

## 🚀 快速开始

### 环境要求
- Python 3.9+
- PostgreSQL 13+
- Redis 6+

### 安装步骤

1. **克隆项目**
```bash
git clone <repository-url>
cd 闲置物语-后端
```

2. **安装依赖**
```bash
pip install -r requirements.txt
```

3. **配置环境变量**
```bash
# 复制环境变量示例文件
cp env.example .env

# 编辑.env文件，设置必要的配置项
```

4. **初始化数据库**
```bash
# 创建数据库迁移
alembic revision --autogenerate -m "Initial migration"

# 执行迁移
alembic upgrade head
```

5. **启动服务**
```bash
# 开发环境一键启动
python scripts/start_dev.py

# 或者手动启动
python main.py
```

6. **启动Celery Worker** (另开终端)
```bash
celery -A celery_app worker --loglevel=info
```

## 📚 API文档

启动服务后，访问以下URL查看API文档：
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

### 主要接口

#### 创建处理任务
```http
POST /api/v1/tasks
Content-Type: application/json

{
    "image_url": "https://example.com/image.jpg",
    "text_description": "一件旧羊毛衫，袖口有些磨损",
    "user_location": {"lat": 39.9042, "lon": 116.4074}
}
```

#### 查询任务状态
```http
GET /api/v1/tasks/{task_id}
```

### 依赖注入使用示例

在API路由中使用依赖注入：

```python
from fastapi import Depends
from app.api.dependencies.database import get_database
from app.api.dependencies.validation import validate_task_input

@router.post("/tasks")
async def create_task(
    task_data: TaskCreate,
    db: AsyncSession = Depends(get_database),           # 数据库依赖
    validated_input: dict = Depends(validate_task_input) # 验证依赖
):
    # 路由处理逻辑
    pass
```

## 🧪 测试

```bash
# 运行所有测试
pytest

# 运行特定测试
pytest tests/api/test_tasks.py

# 运行覆盖率测试
pytest --cov=app tests/
```

## 🐳 Docker部署

```bash
# 构建镜像
docker build -t xianzhiwuyu-backend .

# 使用docker-compose启动
docker-compose up -d
```

## 📝 开发指南

### 添加新的API接口
1. 在`app/api/v1/`下创建新的路由文件
2. 在`main.py`中注册路由
3. 添加相应的测试用例

### 添加新的数据模型
1. 在`app/models/`下定义SQLAlchemy模型
2. 创建数据库迁移：`alembic revision --autogenerate -m "描述"`
3. 执行迁移：`alembic upgrade head`

### 添加新的服务
1. 在`app/services/`下创建服务类
2. 在Agent中集成新服务
3. 添加相应的配置项

### 添加新的依赖项
1. 在`app/api/dependencies/`下创建或编辑相应的依赖文件：
   - `auth.py`: 认证和权限相关依赖
   - `database.py`: 数据库相关依赖
   - `validation.py`: 输入验证相关依赖
2. 在`app/api/dependencies/__init__.py`中导出新的依赖项
3. 在API路由中使用`Depends()`注入依赖项

## 🎛️ 依赖注入架构

项目采用模块化的依赖注入设计，将不同类型的依赖项分离管理：

### 📋 依赖项分类
- **`database.py`**: 数据库会话管理
  - `get_database()`: 提供异步数据库会话
  - 自动处理连接的创建和关闭
  
- **`auth.py`**: 认证和配置管理  
  - `get_app_settings()`: 获取应用配置
  - 预留用户认证和权限验证功能

- **`validation.py`**: 输入验证
  - `validate_task_input()`: 验证任务创建参数
  - 统一的参数校验逻辑

### 🔄 依赖注入优势
- **🎯 模块化**: 不同类型的依赖项分离管理
- **♻️ 可重用**: 多个路由可共享相同的依赖项
- **🧪 易测试**: 依赖项可轻松被模拟替换
- **🔒 类型安全**: 完整的类型注解支持
- **⚡ 高性能**: FastAPI自动缓存依赖项结果

## 🔧 配置说明

主要配置项说明请参考`env.example`文件中的注释。

核心配置：
- `DATABASE_URL`: PostgreSQL数据库连接字符串
- `REDIS_URL`: Redis连接字符串
- `LANXIN_API_KEY`: 蓝心大模型API密钥
- `SECRET_KEY`: 应用密钥

## 📊 监控和日志

- 日志文件位置：`logs/app.log`
- 日志级别可通过`LOG_LEVEL`环境变量配置
- 支持日志轮转和压缩

## 🤝 贡献指南

1. Fork 项目
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启 Pull Request

## 📄 许可证

此项目采用 MIT 许可证。详见 [LICENSE](LICENSE) 文件。

## 📞 联系我们

- 项目链接: [GitHub Repository]
- 问题反馈: [GitHub Issues]

---

**闲置物语** - 让每一件物品都有最好的归宿 ♻️ 