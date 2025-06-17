# 提示词管理模块

## 概述

此模块提供集中式的提示词管理功能，专门用于管理LLM模型的各种提示词模板。

## 设计理念

遵循 **KISS 原则**（Keep It Simple, Stupid），提供简洁而实用的提示词管理功能：
- **集中管理**：所有提示词统一管理，便于维护
- **模板化**：支持参数化的提示词模板
- **类型安全**：提供完整的类型提示
- **易于扩展**：简单直观的扩展方式

## 目录结构

```
app/prompts/
├── __init__.py           # 模块导出
├── llm_prompts.py        # LLM模型提示词管理
└── README.md            # 使用说明

tests/prompts/
└── test_prompt_management.py  # 提示词功能测试
```

## 核心功能

### LLMPrompts 类

提供以下提示词管理功能：

- **文本分析提示词**：分析用户输入的文字描述
- **图像分析提示词**：分析上传的图片内容
- **系统提示词**：设定AI助手的角色和行为

## 使用方法

### 1. 基础使用

```python
from app.prompts import LLMPrompts

# 获取系统提示词
system_prompt = LLMPrompts.get_text_analysis_system_prompt()

# 获取文本分析提示词（带参数）
user_prompt = LLMPrompts.get_text_analysis_prompt("这是一台二手笔记本电脑")

# 获取图像分析提示词
image_prompt = LLMPrompts.get_image_analysis_prompt()

# 获取所有提示词（用于调试或管理）
all_prompts = LLMPrompts.get_all_prompts()
```

### 2. 在服务中使用

```python
# 在 lanxin_service.py 中的使用示例
from app.prompts import LLMPrompts

class LanxinService:
    async def analyze_text(self, text_description: str):
        request_body = {
            "model": self.text_model,
            "sessionId": session_id,
            "systemPrompt": LLMPrompts.get_text_analysis_system_prompt(),
            "prompt": LLMPrompts.get_text_analysis_prompt(text_description),
            # ... 其他参数
        }
```

## 扩展指南

### 添加新的提示词

1. **在 LLMPrompts 类中添加常量**：
```python
# 新的提示词模板
PRICE_ESTIMATION_PROMPT = """请根据物品信息估算价格：
物品信息：{item_info}
请返回JSON格式的价格评估结果..."""
```

2. **添加获取方法**：
```python
@classmethod
def get_price_estimation_prompt(cls, item_info: str) -> str:
    """获取价格评估提示词"""
    return cls.PRICE_ESTIMATION_PROMPT.format(item_info=item_info)
```

3. **更新 get_all_prompts() 方法**：
```python
@classmethod
def get_all_prompts(cls) -> Dict[str, str]:
    return {
        "text_analysis_system": cls.TEXT_ANALYSIS_SYSTEM_PROMPT,
        "text_analysis_user": cls.TEXT_ANALYSIS_USER_PROMPT_TEMPLATE,
        "image_analysis": cls.IMAGE_ANALYSIS_PROMPT,
        "price_estimation": cls.PRICE_ESTIMATION_PROMPT,  # 新增
    }
```

### 创建新的提示词类

如果需要管理不同领域的提示词，可以创建新的管理类：

```python
# app/prompts/market_prompts.py
class MarketPrompts:
    """市场分析提示词管理"""
    
    TREND_ANALYSIS_PROMPT = """分析市场趋势：{data}"""
    
    @classmethod
    def get_trend_analysis_prompt(cls, data: str) -> str:
        return cls.TREND_ANALYSIS_PROMPT.format(data=data)
```

## 最佳实践

### 1. 命名规范
- **常量命名**：使用大写下划线格式，如 `TEXT_ANALYSIS_PROMPT`
- **方法命名**：使用 `get_` 前缀，如 `get_text_analysis_prompt()`
- **参数命名**：使用描述性名称，如 `text_description` 而非 `text`

### 2. 提示词设计
- **结构化输出**：明确指定返回的JSON格式
- **错误处理**：提供无法识别时的fallback指引
- **参数化**：使用 `{parameter}` 格式进行参数替换

### 3. 文档化
- 为每个提示词添加详细的文档说明
- 描述预期的输入参数和输出格式
- 提供使用示例

### 4. 测试
```python
def test_text_analysis_prompt():
    prompt = LLMPrompts.get_text_analysis_prompt("测试描述")
    assert "测试描述" in prompt
    assert "category" in prompt
```

## 当前提示词列表

| 提示词类型 | 方法名 | 用途 |
|-----------|--------|------|
| 系统提示词 | `get_text_analysis_system_prompt()` | 设定AI角色为物品分析专家 |
| 文本分析 | `get_text_analysis_prompt(text)` | 分析文字描述的物品信息 |
| 图像分析 | `get_image_analysis_prompt()` | 分析图片中的物品信息 |


