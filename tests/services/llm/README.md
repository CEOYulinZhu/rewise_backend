# 蓝心大模型服务测试文档

本目录包含了对 VIVO BlueLM 大模型服务的完整测试套件，专注于**基础LLM调用功能**：文本分析和视觉分析。

## 📁 文件结构

```
tests/services/llm/
├── README.md                    # 本文档
├── test_lanxin_service.py       # 蓝心文本服务测试
├── test_lanxin_vision.py        # 蓝心视觉服务测试
├── 测试图片.png                  # 视觉测试用图片
└── __init__.py                  # 包初始化文件
```

## 🚀 测试文件说明

### 1. test_lanxin_service.py - 文本服务测试

**功能覆盖：**
- ✅ 服务初始化验证
- ✅ 鉴权头部生成测试  
- ✅ 文本分析功能（`analyze_text`）
- ✅ 错误处理机制
- ✅ 性能基准测试

**设计说明：**
根据后端架构设计，`LanxinService` 只负责基础的LLM调用，不包含复杂的业务逻辑。处置建议生成和多轮对话功能由更高层的 Agent 模块负责。

**主要测试类：**
- `TestLanxinServiceReal` - 真实API调用测试类

**测试用例：**
```python
# 基础功能测试
test_service_initialization()         # 服务初始化
test_auth_headers_generation()        # 鉴权验证
test_analyze_text_simple()           # 简单文本分析
test_analyze_text_detailed()         # 详细文本分析
test_error_handling()               # 错误处理
test_performance()                  # 性能测试
test_all_functions()                # 综合功能测试
```

### 2. test_lanxin_vision.py - 视觉服务测试

**功能覆盖：**
- ✅ 图片分析功能（`analyze_image`）
- ✅ JSON解析验证
- ✅ 错误处理（文件不存在、格式错误等）
- ✅ 性能测试
- ✅ 综合分析测试

**设计说明：**
视觉服务专注于图片内容识别和分析，使用蓝心视觉大模型进行物品识别，输出标准化的JSON格式结果。

**主要测试类：**
- `TestLanxinVisionService` - 视觉API测试类

**测试用例：**
```python
# 视觉功能测试
test_service_initialization()        # 服务初始化
test_image_file_exists()            # 测试图片验证
test_analyze_image_basic()          # 基础图片分析
test_error_handling()              # 错误处理
test_json_parsing()                # JSON解析测试
test_performance()                 # 性能测试
test_all_vision_functions()        # 全功能测试
```

## 🔧 运行测试

### 环境准备

1. **安装依赖：**
```bash
pip install pytest pytest-asyncio httpx
```

2. **配置环境变量：**
确保在环境中设置了以下变量：
```bash
LANXIN_APP_ID=your_app_id
LANXIN_APP_KEY=your_app_key
LANXIN_API_BASE_URL=https://api.vivo.com.cn/...
LANXIN_TEXT_MODEL=vivo-BlueLM-TB-Pro
```

### 运行方式

#### 1. 运行所有测试
```bash
# 在项目根目录执行
pytest tests/services/llm/ -v
```

#### 2. 运行特定测试文件
```bash
# 文本服务测试
pytest tests/services/llm/test_lanxin_service.py -v

# 视觉服务测试  
pytest tests/services/llm/test_lanxin_vision.py -v
```

#### 3. 运行特定测试用例
```bash
# 运行文本分析测试
pytest tests/services/llm/test_lanxin_service.py::TestLanxinServiceReal::test_analyze_text_simple -v

# 运行图片分析测试
pytest tests/services/llm/test_lanxin_vision.py::TestLanxinVisionService::test_analyze_image_basic -v
```

#### 4. 快速验证测试
```bash
# 快速文本API测试
python tests/services/llm/test_lanxin_service.py

# 快速视觉API测试
python tests/services/llm/test_lanxin_vision.py
```

## 📊 测试报告示例

### 文本服务测试输出
```
=== 测试简单文本分析 ===
✅ 文本分析成功
   输入: 一台黑色苹果iPhone手机
   结果: {
     "category": "电器",
     "sub_category": "手机",
     "brand": "苹果",
     "condition": "未知",
     "keywords": ["iPhone", "手机", "苹果"]
   }

🚀 开始蓝心服务综合功能测试
✅ 所有功能测试通过！
```

### 视觉服务测试输出
```
=== 测试基础图片分析 ===
✅ 图片分析成功
   图片路径: /path/to/测试图片.png
   分析结果:
     category: 电器
     sub_category: 手机
     brand: 苹果
     condition: 九成新
     description: 一台黑色的苹果iPhone手机...

🔍 开始蓝心视觉服务综合功能测试
🎉 所有视觉功能测试通过！
```

## 🎯 测试重点

### 文本服务测试重点
1. **API连接性** - 验证与蓝心文本API的连接
2. **鉴权机制** - 测试VIVO签名算法的正确性
3. **文本处理** - 验证物品描述分析的准确性和JSON格式输出
4. **错误恢复** - 验证各种异常情况的处理

### 视觉服务测试重点
1. **图片上传** - 测试Base64编码和图片传输
2. **视觉理解** - 验证AI对图片内容的识别能力
3. **JSON解析** - 测试返回数据的格式化处理和解析逻辑
4. **格式处理** - 测试不同图片格式的兼容性
5. **错误处理** - 验证文件异常和API异常的处理机制

## ⚠️ 注意事项

### API限制
- **并发限制：** 避免过于频繁的API调用
- **文件大小：** 图片文件建议小于10MB
- **格式支持：** 主要支持JPG、PNG格式
- **请求超时：** 单次请求超时设置为30秒

### 测试数据
- **测试图片：** `测试图片.png` 用于视觉功能测试
- **敏感信息：** 避免在测试中使用真实敏感数据
- **清理策略：** 测试完成后自动清理临时文件

### 错误排查
1. **认证失败：** 检查APP_ID和APP_KEY配置
2. **网络超时：** 检查网络连接和API端点
3. **文件错误：** 确认测试图片文件存在且可读
4. **格式错误：** 验证API返回数据的JSON格式


## 📐 架构说明

根据后端设计文档，蓝心大模型服务在整体系统中的定位：

```
Frontend → FastAPI → Celery Worker → **Agent** → LanxinService
                                         ↓
                                 RAG + Crawler + Database
```

### 职责分工
- **LanxinService**: 负责基础LLM调用（文本分析、图片分析）
- **Agent**: 负责业务逻辑编排（处置建议生成、多数据源整合）
- **其他服务**: 负责特定功能（RAG检索、爬虫、数据库操作）

## 🔄 更新维护

本测试套件会随着蓝心大模型API的更新而持续维护：

- **API变更：** 及时更新测试用例适配新版本API
- **功能扩展：** 根据新功能添加相应测试
- **性能优化：** 持续优化测试执行效率
- **文档同步：** 保持文档与代码的同步更新
