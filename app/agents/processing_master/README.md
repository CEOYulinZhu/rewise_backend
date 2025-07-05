# 总处理协调器Agent

## 功能概述

总处理协调器Agent (`ProcessingMasterAgent`) 是闲置物语系统的核心调度模块，集成了内容分析服务和四大专业Agent，为用户提供完整的闲置物品处置解决方案。

## 核心功能

### 1. 多输入方式支持
- **纯图片**：上传物品图片进行AI图像识别分析
- **纯文字**：提供物品文字描述进行语义分析
- **图片+文字**：结合图片和文字描述，智能比较差异并以文字分析为准

### 2. 智能内容分析
- 基于蓝心大模型的图像识别和文本理解
- 自动识别物品类别、状态、价值等关键信息
- 图文差异检测与智能合并

### 3. 四大Agent协调
异步并行调用四个专业处理Agent：

#### 处置路径推荐Agent
- 基于物品分析结果智能推荐最佳处置路径
- 提供创意改造、回收捐赠、二手交易三大选择
- 计算各路径的推荐指数和理由

#### 创意改造协调器Agent
- 生成个性化DIY改造方案
- 搜索相关Bilibili视频教程
- 提供详细的改造步骤和材料清单

#### 回收捐赠协调器Agent
- 推荐附近的回收点和回收站
- 匹配专业回收平台（如爱回收）
- 支持基于用户位置的地理信息推荐

#### 二手交易协调器Agent
- 搜索二手平台的相似商品和价格
- 生成优化的交易文案和卖点描述
- 多平台价格对比分析

### 4. 实时进度反馈
- 支持WebSocket长连接推送处理进度
- 每个处理步骤都有详细的状态更新
- 异常处理和错误追踪

## 技术架构

### 异步并行设计
```python
# 四大Agent并行执行
tasks = [
    creative_agent.generate_complete_solution(analysis_result),
    recycling_agent.coordinate_recycling_donation(analysis_result, user_location),
    secondhand_agent.coordinate_trading(analysis_result)
]
results = await asyncio.gather(*tasks, return_exceptions=True)
```

### 进度回调机制
```python
async for step in agent.process_complete_solution(request):
    # 实时接收处理步骤更新
    print(f"步骤：{step.step_title} - 状态：{step.status}")
    if step.status == ProcessingStepStatus.COMPLETED:
        # 处理完成的步骤结果
        handle_step_result(step.result)
```

### 资源管理
```python
async with ProcessingMasterAgent() as agent:
    # 自动资源管理
    async for step in agent.process_complete_solution(request):
        yield step
# 自动清理资源
```

## 使用方法

### 基本使用

```python
from app.agents.processing_master.agent import ProcessingMasterAgent
from app.models.processing_master_models import ProcessingMasterRequest

# 创建请求
request = ProcessingMasterRequest(
    image_url="/path/to/image.jpg",  # 可选
    text_description="一个旧的电子产品",  # 可选
    user_location={"lat": 39.9042, "lon": 116.4074}  # 可选
)

# 处理完整解决方案
async with ProcessingMasterAgent() as agent:
    async for step in agent.process_complete_solution(request):
        print(f"步骤：{step.step_title}")
        print(f"状态：{step.status}")
        print(f"描述：{step.description}")
        
        if step.status == ProcessingStepStatus.COMPLETED:
            # 获取步骤结果
            result = step.result
        elif step.status == ProcessingStepStatus.FAILED:
            # 处理错误
            print(f"错误：{step.error}")
```

### WebSocket集成

```python
# 在FastAPI中集成WebSocket
@app.websocket("/ws/process")
async def websocket_process(websocket: WebSocket):
    await websocket.accept()
    
    request_data = await websocket.receive_json()
    request = ProcessingMasterRequest(**request_data)
    
    async with ProcessingMasterAgent() as agent:
        async for step in agent.process_complete_solution(request):
            await websocket.send_json({
                "step": step.step_name,
                "title": step.step_title,
                "status": step.status.value,
                "result": step.result,
                "metadata": step.metadata
            })
```

## 输入格式

### ProcessingMasterRequest

```python
{
    "image_url": "http://example.com/image.jpg",  # 可选：图片URL或本地路径
    "text_description": "物品的文字描述",        # 可选：文字描述
    "user_location": {                           # 可选：用户位置
        "lat": 39.9042,                         # 纬度
        "lon": 116.4074                         # 经度
    }
}
```

**注意**：`image_url` 和 `text_description` 至少需要提供一个。

## 输出格式

### ProcessingStep（进度步骤）

```python
{
    "step_name": "content_analysis",            # 步骤名称
    "step_title": "内容分析",                   # 步骤标题
    "description": "分析图片和/或文字内容",       # 步骤描述
    "status": "completed",                      # 状态：pending/running/completed/failed
    "result": {...},                           # 步骤结果（成功时）
    "error": "错误信息",                        # 错误信息（失败时）
    "metadata": {...},                         # 元数据信息
    "timestamp": "2024-01-01T00:00:00Z"        # 时间戳
}
```

### ProcessingMasterResponse（最终结果）

```python
{
    "success": true,
    "analysis_result": {                        # 分析结果
        "category": "电子产品",
        "condition": "使用痕迹明显",
        "brand": "苹果",
        "model": "iPhone 12",
        "estimated_value": 2000
    },
    "disposal_recommendation": {                # 处置推荐
        "recommendations": {
            "creative_renovation": {...},
            "recycling_donation": {...},
            "secondhand_trading": {...}
        }
    },
    "creative_coordination": {                  # 创意改造结果
        "renovation_plan": {...},
        "videos": [...]
    },
    "recycling_coordination": {                 # 回收捐赠结果
        "location_recommendation": {...},
        "platform_recommendation": {...}
    },
    "secondhand_coordination": {                # 二手交易结果
        "search_results": {...},
        "content_generation": {...}
    },
    "processing_time_seconds": 5.2,           # 处理耗时
    "timestamp": "2024-01-01T00:00:00Z"       # 完成时间
}
```

## 处理流程

1. **输入验证**：验证请求参数的有效性
2. **内容分析**：调用蓝心大模型分析图片/文字
3. **处置推荐**：基于分析结果推荐最佳处置路径
4. **并行协调**：同时调用三大协调器Agent
   - 创意改造协调器
   - 回收捐赠协调器  
   - 二手交易协调器
5. **结果整合**：汇总所有Agent的处理结果

## 错误处理

### 容错机制
- 单个Agent失败不影响其他Agent执行
- 详细的错误日志和用户友好的错误信息
- 自动资源清理和异常恢复

### 常见错误
- **输入验证失败**：图片文件不存在、文字描述过短
- **分析服务异常**：蓝心大模型API调用失败
- **Agent执行失败**：单个子Agent内部错误
- **网络超时**：外部服务调用超时

## 性能特点

- **异步并行**：四大Agent同时执行，显著提升处理速度
- **流式响应**：实时返回处理进度，提升用户体验
- **资源优化**：延迟初始化和自动资源清理
- **缓存支持**：分析结果和推荐数据支持缓存

## 配置要求

### 环境变量
```bash
# 蓝心大模型配置
LANXIN_API_KEY=your_api_key
LANXIN_API_URL=your_api_url

# 数据库配置
DATABASE_URL=postgresql://...

# Redis配置  
REDIS_URL=redis://localhost:6379
```

### 依赖服务
- PostgreSQL（主数据库）
- Redis（缓存和消息队列）
- 蓝心大模型API
- 各种外部API（高德地图、爱回收、闲鱼等）

## 监控和日志

### 日志记录
- 详细的处理步骤日志
- 性能指标记录（处理时间、成功率等）
- 错误追踪和异常信息

### 状态监控
```python
# 获取组件状态
status = agent.get_component_status()
print(status)
# {
#   "initialized": true,
#   "lanxin_service": true,
#   "disposal_agent": true,
#   "creative_agent": true,
#   "recycling_agent": true,
#   "secondhand_agent": true
# }
```

## 扩展性

### 新增Agent
1. 创建新的Agent类
2. 在 `ProcessingMasterAgent` 中添加初始化
3. 在 `process_complete_solution` 中添加调用逻辑
4. 更新数据模型和转换器

### 自定义处理流程
- 支持动态配置处理步骤
- 可配置Agent调用顺序和并行策略
- 支持条件性Agent调用（基于分析结果）

## 最佳实践

1. **使用异步上下文管理器**：确保资源正确清理
2. **实现进度回调**：提供实时用户反馈
3. **错误处理**：妥善处理各种异常情况
4. **性能监控**：记录处理时间和资源使用情况
5. **缓存策略**：合理缓存分析结果和推荐数据 