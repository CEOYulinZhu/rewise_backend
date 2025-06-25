# 三大处置路径推荐Agent

## 功能概述

智能分析闲置物品的最佳处置方案，基于蓝心大模型分析，为用户提供**创意改造**、**回收捐赠**、**二手交易**三大路径的推荐度和理由标签。

## 核心功能

### 1. 多输入方式支持
- **图片分析推荐**: 从上传的物品图片获取处置建议
- **文字描述推荐**: 从用户文字描述获取处置建议  
- **分析结果推荐**: 从已有的物品分析结果获取处置建议

### 2. 智能推荐算法
- **AI驱动**: 使用蓝心大模型进行智能分析
- **备用逻辑**: 当AI分析失败时，使用基于规则的备用推荐算法
- **个性化推荐**: 基于物品类别、状态、材质等因素提供精准建议

### 3. 完整的推荐信息
每种处置路径包含：
- **推荐度百分比** (0-100%)
- **推荐理由标签** (3-5个，每个不超过7字)
- **具体参数估算** (难度、耗时、成本等)

## 使用示例

### 基本使用

```python
from app.agents.disposal_recommendation import DisposalRecommendationAgent

# 创建Agent实例
async with DisposalRecommendationAgent() as agent:
    
    # 方式1: 从图片获取推荐
    result = await agent.recommend_from_image("path/to/item_image.jpg")
    
    # 方式2: 从文字描述获取推荐  
    result = await agent.recommend_from_text("一台用了两年的笔记本电脑")
    
    # 方式3: 从分析结果获取推荐
    analysis_result = {
        "category": "电子产品",
        "condition": "八成新",
        "brand": "联想"
    }
    result = await agent.recommend_from_analysis(analysis_result)
```

### 返回结果格式

```json
{
    "success": true,
    "source": "text",
    "original_text": "一台用了两年的笔记本电脑",
    "analysis_result": {
        "category": "电子产品",
        "sub_category": "笔记本电脑",
        "condition": "八成新",
        "brand": "联想"
    },
    "recommendations": {
        "creative_renovation": {
            "recommendation_score": 25,
            "reason_tags": ["科技改造", "智能升级", "零件利用"],
            "difficulty_level": "困难",
            "estimated_time": "1-2周",
            "estimated_cost": "200-500元"
        },
        "recycling_donation": {
            "recommendation_score": 60,
            "reason_tags": ["环保回收", "数据安全", "专业处理"],
            "environmental_impact": 5,
            "social_value": 4
        },
        "secondhand_trading": {
            "recommendation_score": 75,
            "reason_tags": ["保值性好", "需求量大", "快速变现"],
            "estimated_price_range": "1500-2500元",
            "market_demand": "高",
            "selling_difficulty": "易"
        },
        "overall_recommendation": {
            "primary_choice": "二手交易",
            "reason": "笔记本电脑保值性好，市场需求旺盛"
        }
    },
    "recommendation_source": "ai_model"
}
```

## 推荐算法说明

### 1. AI模型推荐
- 使用蓝心大模型进行智能分析
- 基于物品的详细信息提供个性化建议
- 考虑市场需求、改造难度、环保价值等多维度因素

### 2. 备用推荐算法
当AI模型不可用时，使用基于规则的算法：

#### 物品类别倾向
- **电子产品**: 偏向二手交易和回收捐赠
- **家具**: 偏向创意改造和二手交易  
- **服装**: 偏向回收捐赠和创意改造
- **书籍**: 偏向回收捐赠
- **玩具**: 偏向回收捐赠

#### 物品状态修正
- **全新/九成新**: 提高交易推荐度
- **七成新/有磨损**: 提高改造推荐度
- **损坏**: 提高回收推荐度

## 扩展性设计

### 1. 类别配置
可在 `DisposalRecommendationPrompts.CATEGORY_DISPOSAL_PREFERENCES` 中添加新的物品类别配置。

### 2. 状态修正
可在 `DisposalRecommendationPrompts.CONDITION_MODIFIERS` 中调整不同状态的推荐度修正系数。

### 3. 提示词优化
可在 `DisposalRecommendationPrompts` 中优化系统提示词和用户提示词模板。

## 测试

运行测试：
```bash
# 运行完整测试套件
pytest tests/agents/disposal_recommendation/

# 运行简单测试
python tests/agents/disposal_recommendation/test_agent.py
```

## 依赖模块

- `app.services.llm.lanxin_service`: 蓝心大模型服务
- `app.prompts.disposal_recommendation_prompts`: 处置推荐提示词管理
- `app.core.config`: 配置管理
- `app.core.logger`: 日志记录
- `app.utils.vivo_auth`: VIVO API认证

## 注意事项

1. **API限制**: 需要配置有效的蓝心大模型API密钥
2. **图片格式**: 支持常见图片格式 (JPG, PNG等)
3. **响应时间**: AI分析可能需要几秒时间，建议异步调用
4. **错误处理**: 内置完善的错误处理和备用机制
5. **资源管理**: 使用完毕后需要调用 `close()` 方法释放资源 