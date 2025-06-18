# 开发环境管理脚本 - 使用指南

## 📋 脚本简介

`setup_env.py` 是闲置物语后端项目的**一键开发环境管理工具**，专为简化项目初始化和日常开发启动而设计。

### 🎯 主要功能
- 🔧 **环境配置**：自动生成 `.env` 配置文件
- 📁 **目录管理**：创建项目所需的目录结构
- 🐳 **服务管理**：启动 Docker 基础设施（数据库、缓存）
- 🚀 **应用启动**：一键启动完整开发环境
- ✅ **依赖检查**：自动验证环境配置

---

## 🚀 快速开始

### 对于开发人员

```powershell
# 首次使用（完整设置）
python scripts/setup_env.py start

# 仅设置环境文件（如果需要重新生成配置）
python scripts/setup_env.py setup

# 无参数运行（默认仅设置环境）
python scripts/setup_env.py
```

### 对于非技术人员

如果你需要启动后端服务进行测试或演示：

1. **打开 PowerShell**
   - 按 `Win + R`，输入 `powershell`，回车

2. **进入项目目录**
   ```powershell
   cd "你的项目路径\闲置物语-后端"
   ```

3. **一键启动**
   ```powershell
   python scripts/setup_env.py start
   ```

4. **等待启动完成**
   - 看到 "🔄 启动中..." 后应用会自动启动
   - 访问 http://localhost:8000 查看应用

---

## 📚 详细使用说明

### 🔧 命令详解

#### `python scripts/setup_env.py` （默认模式）
**功能**：仅设置环境配置
```powershell
python scripts/setup_env.py

# 执行内容：
# ✅ 创建 .env 配置文件（如果不存在）
# ✅ 创建必要目录（data、logs 等）
# ℹ️  显示后续操作提示
```

**适用场景**：
- 首次克隆项目后的初始化
- 需要重新生成配置文件
- 仅需要环境准备，不启动服务

#### `python scripts/setup_env.py setup`
**功能**：明确的环境设置模式（与默认模式相同）
```powershell
python scripts/setup_env.py setup

# 等同于默认模式
```

#### `python scripts/setup_env.py start` ⭐ **推荐**
**功能**：完整的开发环境启动
```powershell
python scripts/setup_env.py start

# 执行流程：
# 1. 🔧 设置环境配置
# 2. 🔍 检查 Docker 状态
# 3. 🐳 启动 PostgreSQL 和 Redis
# 4. ⏳ 等待服务就绪
# 5. 🚀 启动 FastAPI 应用
```

**适用场景**：
- 日常开发启动
- 演示环境准备
- 完整功能测试

---

## 🔍 执行流程详解

### 环境设置阶段
```
🚀 正在设置闲置物语后端开发环境...
✅ 已创建环境配置文件: /path/to/.env
✅ 已创建目录: /path/to/data/chroma_db
✅ 已创建目录: /path/to/data/uploads
✅ 已创建目录: /path/to/logs
✅ 已创建目录: /path/to/init-db
```

### 依赖检查阶段
```
🔍 检查依赖服务...
🔄 检查Docker状态...
✅ Docker Engine running
```

### 基础设施启动阶段
```
🐳 启动基础设施服务...
🔄 启动PostgreSQL和Redis...
✅ Container xianzhiwuyu_postgres  Started
✅ Container xianzhiwuyu_redis     Started
✅ Container xianzhiwuyu_pgadmin   Started
⏳ 等待数据库服务启动...
```

### 应用启动阶段
```
🎯 启动FastAPI应用...
📋 访问地址:
   • 应用主页: http://localhost:8000
   • API文档: http://localhost:8000/docs
   • 健康检查: http://localhost:8000/health

💡 数据库表将在应用启动时自动创建
🔄 启动中...
```

---

## 🗂️ 生成的文件和目录

### 配置文件
```
.env                    # 环境变量配置（自动生成）
├── 应用配置
├── 数据库配置
├── Redis配置
├── 蓝心API配置
└── 其他服务配置
```

### 目录结构
```
data/
├── chroma_db/         # 向量数据库存储
└── uploads/           # 文件上传目录

logs/
└── app.log           # 应用日志文件

init-db/              # 数据库初始化脚本目录
```

---

## ⚙️ 配置说明

### 自动生成的 .env 配置

脚本会创建包含以下配置的 `.env` 文件：

```env
# 应用配置
APP_NAME=闲置物语后端
APP_VERSION=1.0.0
DEBUG=True
API_PREFIX=/api/v1

# 数据库配置
DATABASE_URL=postgresql+asyncpg://xianzhiwuyu_user:xianzhiwuyu_pass@localhost:5432/xianzhiwuyu
POSTGRES_USER=xianzhiwuyu_user
POSTGRES_PASSWORD=xianzhiwuyu_pass
POSTGRES_DB=xianzhiwuyu

# Redis配置
REDIS_URL=redis://localhost:6379/0

# 蓝心大模型API配置
LANXIN_APP_ID=2025251747
LANXIN_APP_KEY=wmuPTuICigJsKdYU

# 安全配置
SECRET_KEY=xianzhiwuyu-dev-secret-key-2024
```

### 🔧 自定义配置

如需修改配置，直接编辑 `.env` 文件即可：

```powershell
# 编辑配置文件
notepad .env

# 重启应用生效
python main.py
```

---

## 🐳 Docker 服务说明

脚本会启动以下 Docker 服务：

| 服务 | 容器名 | 端口 | 用途 |
|------|---------|------|------|
| PostgreSQL | `xianzhiwuyu_postgres` | 5432 | 主数据库 |
| Redis | `xianzhiwuyu_redis` | 6379 | 缓存/消息队列 |
| pgAdmin | `xianzhiwuyu_pgadmin` | 8080 | 数据库管理 |

### 服务状态检查
```powershell
# 查看服务状态
docker-compose ps

# 预期输出
# NAME                   STATUS
# xianzhiwuyu_postgres   Up
# xianzhiwuyu_redis      Up  
# xianzhiwuyu_pgadmin    Up
```

---

## 🚨 故障排除

### ❌ Docker 未运行
**错误信息**：
```
❌ 检查Docker状态 失败: ...
⚠️  Docker未运行，请启动Docker Desktop
```

**解决方案**：
1. 启动 Docker Desktop
2. 等待 Docker 完全启动
3. 重新运行脚本

### ❌ 端口被占用
**错误信息**：
```
Error: Port 8000 is already in use
```

**解决方案**：
```powershell
# 查找占用进程
netstat -ano | findstr "8000"

# 结束占用进程（替换PID）
taskkill /PID 12345 /F

# 或修改应用端口
```

### ❌ docker-compose.yml 不存在
**错误信息**：
```
❌ docker-compose.yml文件不存在
```

**解决方案**：
确保在项目根目录下运行脚本，检查文件是否存在。

### ❌ 权限不足
**错误信息**：
```
Access denied
```

**解决方案**：
1. 以管理员身份运行 PowerShell
2. 或检查项目目录权限

---

## 🔄 日常工作流程

### 首次使用
```powershell
# 一键启动
python scripts/setup_env.py start
```

### 日常开发
```powershell
# 检查 Docker 服务状态
docker-compose ps

# 如果服务运行中，直接启动应用
python main.py

# 如果服务未运行，使用脚本启动
python scripts/setup_env.py start
```

### 完全停止
```powershell
# 1. 停止 FastAPI 应用（Ctrl+C）
# 2. 停止 Docker 服务
docker-compose down
```

---

## 💡 最佳实践

### ✅ 推荐做法
- 首次使用时用 `start` 模式
- 日常开发可直接运行 `python main.py`
- 定期运行 `docker-compose ps` 检查服务状态
- 修改配置后重启应用

### ❌ 避免事项
- 不要同时运行多个 `setup_env.py start`
- 不要在应用运行时停止 Docker 服务
- 不要手动删除自动生成的目录

---

## 🆘 获取帮助

### 查看帮助信息
```powershell
python scripts/setup_env.py help
# 或
python scripts/setup_env.py unknown_command
```

### 常见问题
- **应用无法访问**：检查 http://localhost:8000/health
- **数据库连接失败**：确认 Docker 服务正常运行
- **配置文件问题**：删除 `.env` 后重新运行脚本

---

## 📝 附录

### 脚本源码位置
```
scripts/setup_env.py      # 主脚本
scripts/README.md         # 本文档
```

### 相关文档
- `docs/运维指南.md` - 详细运维说明
- `docker-compose.yml` - Docker 服务配置
- `main.py` - 应用启动入口

### 版本信息
- 脚本版本：v1.0
- 支持系统：Windows 10/11
- 依赖：Python 3.8+, Docker Desktop 