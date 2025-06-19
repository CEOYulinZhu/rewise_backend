# Bilibili搜索Agent

智能B站视频搜索代理，使用蓝心大模型的Function Calling功能，**直接接收图片文件或文字描述**，内部完成分析、关键词提取和视频搜索的**端到端**解决方案。

## 核心功能

### 1. 端到端搜索流程
- **图片搜索**: 直接传入图片文件路径，自动完成图片分析→关键词提取→视频搜索
- **文字搜索**: 直接传入文字描述，自动完成文字分析→关键词提取→视频搜索
- **智能关键词提取**: 使用蓝心大模型Function Calling智能提取搜索关键词
- **备用机制**: Function Calling失败时自动使用分类映射的备用逻辑

### 2. Function Calling智能分析
- 使用蓝心大模型分析物品特征（类别、材料、状态等）
- 智能生成B站搜索关键词，自动添加DIY、改造等相关词汇
- 提供搜索意图说明，便于理解搜索目的
- 支持图片和文字两种输入方式

### 3. B站视频搜索与结果整理
- 基于提取的关键词搜索B站相关教程视频
- 返回结构化视频信息（标题、UP主、播放量、时长、链接等）
- 支持结果数量控制
- 包含完整的处理流程追踪信息

## 架构设计

### 简化的端到端架构
```
输入: 图片文件路径 或 文字描述
   ↓
步骤1: LanxinService 分析内容
   ↓  
步骤2: Function Calling 提取关键词
   ↓
步骤3: BilibiliVideoSearchService 搜索视频
   ↓
输出: 结构化搜索结果
```

### 模块化结构
```
app/agents/bilibili_search/
├── __init__.py              # 模块初始化
├── agent.py                 # 核心Agent实现（仅2个主要方法）
└── README.md               # 文档

app/prompts/
├── bilibili_search_prompts.py  # 专用提示词模块

tests/agents/bilibili_search/
├── __init__.py              # 测试模块初始化
└── test_agent.py           # Agent测试（简化为核心功能测试）
```

### Function Calling流程
1. **内容分析**: 调用`LanxinService`分析图片或文字
2. **构建提示**: 使用`BilibiliSearchPrompts`构建System和User Prompt
3. **Function Calling**: 调用蓝心大模型提取关键词和搜索意图
4. **解析结果**: 提取`<APIs>`标签中的函数调用结果
5. **视频搜索**: 使用提取的关键词搜索B站视频
6. **备用机制**: Function Calling失败时使用智能分类映射

## 使用方法

### 核心API

#### 1. 从图片搜索（推荐）
```python
from app.agents.bilibili_search.agent import BilibiliSearchAgent

async with BilibiliSearchAgent() as agent:
    result = await agent.search_from_image(
        image_path="path/to/your/image.jpg",
        max_videos=10
    )
    
    if result["success"]:
        print(f"图片分析: {result['analysis_result']}")
        print(f"提取关键词: {result['keywords']}")
        print(f"搜索意图: {result['search_intent']}")
        print(f"找到 {len(result['videos'])} 个相关视频")
        
        for video in result["videos"]:
            print(f"- {video['title']} ({video['uploader']})")
```

#### 2. 从文字描述搜索
```python
async with BilibiliSearchAgent() as agent:
    result = await agent.search_from_text(
        text_description="我有一个旧的纸箱，想要改造成书架",
        max_videos=10
    )
    
    if result["success"]:
        print(f"文字分析: {result['analysis_result']}")
        print(f"提取关键词: {result['keywords']}")
        print(f"搜索意图: {result['search_intent']}")
        
        for video in result["videos"]:
            print(f"- {video['title']} - {video['uploader']}")
            print(f"  播放量: {video['play_count']}")
            print(f"  链接: {video['url']}")
```

### 典型使用场景

#### 场景1: 物品图片搜索
```python
# 用户上传了一张废旧物品的图片
image_path = "uploads/old_bottle.jpg"

async with BilibiliSearchAgent() as agent:
    result = await agent.search_from_image(image_path, max_videos=5)
    
    # 直接获得相关DIY教程视频
    if result["success"]:
        videos = result["videos"]
        # 展示给用户...
```

#### 场景2: 文字描述搜索
```python
# 用户描述想要改造的物品
description = "家里有很多空的玻璃瓶，想做成装饰品"

async with BilibiliSearchAgent() as agent:
    result = await agent.search_from_text(description, max_videos=8)
    
    # 直接获得相关教程推荐
    if result["success"]:
        keywords = result["keywords"]  # ['玻璃瓶', '装饰', 'DIY', '手工']
        videos = result["videos"]
```

## 返回格式

### 成功响应
```python
{
    "success": True,
    "source": "image",  # 或 "text"
    "image_path": "path/to/image.jpg",  # 仅图片搜索
    "original_text": "用户输入的文字",   # 仅文字搜索
    "analysis_result": {
        "category": "生活用品",
        "sub_category": "塑料瓶",
        "material": "塑料",
        "condition": "完好",
        "description": "分析描述"
    },
    "keywords": ["塑料瓶", "DIY", "改造", "手工"],
    "search_intent": "寻找塑料瓶改造教程",
    "videos": [
        {
            "title": "废弃塑料瓶的10种神奇改造",
            "uploader": "手工达人小李",
            "url": "https://www.bilibili.com/video/BV...",
            "play_count": "15.6万",
            "duration": "08:32",
            "description": "教你如何将废弃的塑料瓶..."
        }
    ],
    "total": 156,  # B站搜索总结果数
    "function_call_result": {
        "success": True,
        "keywords": ["塑料瓶", "DIY", "改造"],
        "search_intent": "寻找塑料瓶改造教程",
        "source": "function_calling",  # 或 "fallback"
        "raw_response": "大模型原始响应"
    }
}
```

### 失败响应
```python
{
    "success": False,
    "error": "具体错误信息",
    "source": "image",  # 或 "text"
    "image_path": "path/to/image.jpg"  # 如果是图片搜索失败
}
```

## 配置要求

### 环境变量
```bash
# 蓝心大模型API配置
LANXIN_APP_ID=your_app_id
LANXIN_APP_KEY=your_app_key
LANXIN_API_BASE_URL=https://api.xxx.com/v1/llm/query
LANXIN_TEXT_MODEL=BlueLM-7B-Chat-32K
```

### 依赖包
```txt
# 核心依赖
httpx==0.25.2
pytest==7.4.3
pytest-asyncio==0.21.1

# B站搜索
bilibili-api-python

# 图片处理（LanxinService需要）
Pillow
```

## 测试方法

### 使用pytest（推荐）
```bash
# 运行所有测试
pytest tests/agents/bilibili_search/test_agent.py -v -s

# 运行特定测试
pytest tests/agents/bilibili_search/test_agent.py::TestBilibiliSearchAgent::test_search_from_image -v -s
pytest tests/agents/bilibili_search/test_agent.py::TestBilibiliSearchAgent::test_search_from_text -v -s
```

### 直接运行Python文件
```bash
python tests/agents/bilibili_search/test_agent.py
```

### 测试覆盖内容
1. **图片搜索测试**: 使用测试图片完整流程测试
2. **文字搜索测试**: 使用详细文字描述测试
3. **多场景测试**: 测试不同类型物品（服装、电子产品、生活用品）
4. **错误处理测试**: 不存在图片、空文字描述等异常情况

## 技术特点

### 简化的设计理念
- **端到端处理**: 用户只需提供图片或文字，无需关心中间步骤
- **自动化流程**: 内部自动完成分析→提取→搜索的完整链路
- **智能降级**: Function Calling失败时自动使用备用逻辑
- **结果追踪**: 完整保留处理过程信息，便于调试和优化

### Function Calling优势
- **上下文理解**: 大模型能更好地理解物品特征和改造潜力
- **动态关键词**: 根据具体情况生成最适合的搜索词汇
- **意图识别**: 自动分析用户的改造意图和需求方向
- **质量保证**: 相比传统关键词匹配，搜索结果更精准

### 模块化架构
- **提示词管理**: 统一的提示词模块，便于维护和优化
- **备用机制**: 智能的分类映射，确保系统可靠性
- **异步设计**: 支持高并发处理，适合Web应用集成
- **易于集成**: 简单的API设计，便于接入现有系统

## 性能与优化

### 处理时间预估
- **图片搜索**: 3-8秒（图片分析2-4秒 + 关键词提取1-2秒 + 视频搜索1-2秒）
- **文字搜索**: 2-5秒（文字分析1-2秒 + 关键词提取1-2秒 + 视频搜索1秒）

### 优化建议
1. **缓存机制**: 对相似图片的分析结果进行缓存
2. **批量处理**: 支持多个物品的批量分析
3. **结果筛选**: 增加视频质量评分和过滤机制
4. **用户反馈**: 收集用户对搜索结果的满意度，优化算法

## 故障排除

### 常见问题

1. **图片分析失败**
   - 检查图片文件是否存在且格式正确
   - 确认LanxinService配置正确
   - 验证图片内容是否清晰可识别

2. **Function Calling无响应**
   - 查看`function_call_result.raw_response`了解原始响应
   - 检查蓝心API密钥和网络连接
   - 确认提示词格式符合要求

3. **B站搜索无结果**
   - 检查提取的关键词是否合理
   - 验证bilibili-api-python库是否正常工作
   - 尝试手动在B站搜索相同关键词

### 调试方法

1. **启用详细日志**
   ```python
   import logging
   logging.basicConfig(level=logging.INFO)
   ```

2. **查看处理过程**
   ```python
   result = await agent.search_from_image("test.jpg")
   print(f"分析结果: {result.get('analysis_result')}")
   print(f"Function Calling: {result.get('function_call_result')}")
   print(f"最终关键词: {result.get('keywords')}")
   ```

## 扩展方向

### 即将支持的功能
1. **批量处理**: 支持多张图片或多个文字描述的批量处理
2. **结果过滤**: 根据视频时长、播放量等条件过滤结果
3. **相关推荐**: 基于搜索历史的个性化推荐
4. **多平台搜索**: 扩展到小红书、抖音等其他平台

### 集成建议
- **Web API**: 包装为RESTful API，支持HTTP调用
- **任务队列**: 集成Celery支持异步处理
- **数据库**: 保存搜索历史和用户偏好
- **缓存优化**: 使用Redis缓存热门搜索结果 