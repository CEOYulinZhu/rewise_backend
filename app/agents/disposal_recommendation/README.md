# 三大处置路径推荐Agent

## 功能概述

智能分析闲置物品的最佳处置方案，基于蓝心大模型分析，为用户提供**创意改造**、**回收捐赠**、**二手交易**三大路径的推荐度和理由标签。

## 核心功能

### 1. 智能推荐引擎
- **分析结果输入**: 接收上层传入的物品分析结果
- **AI驱动推荐**: 使用蓝心大模型进行智能分析
- **备用逻辑**: 当AI分析失败时，使用基于规则的备用推荐算法
- **个性化推荐**: 基于物品类别、状态、材质等因素提供精准建议

### 2. 精简的推荐信息
每种处置路径包含：
- **推荐度数值** (0-100的整数，不含单位)
- **推荐理由标签** (3-5个，每个不超过7字)

## 使用示例

### 基本使用

```python
from app.agents.disposal_recommendation import DisposalRecommendationAgent

async def example_usage():
    # 准备物品分析结果
    analysis_result = {
        "category": "电子产品",
        "sub_category": "笔记本电脑",
        "condition": "八成新",
        "description": "一台用了两年的笔记本电脑，外观良好",
        "brand": "联想",
        "material": "塑料金属",
        "keywords": ["笔记本", "电脑", "联想"]
    }
    
    # 创建Agent实例并获取推荐
    async with DisposalRecommendationAgent() as agent:
        response = await agent.recommend_from_analysis(analysis_result)
        
        if response.success:
            recommendations = response.recommendations
            print(f"创意改造推荐度: {recommendations.creative_renovation.recommendation_score}")
            print(f"回收捐赠推荐度: {recommendations.recycling_donation.recommendation_score}")
            print(f"二手交易推荐度: {recommendations.secondhand_trading.recommendation_score}")
            
            # 获取排序后的推荐
            sorted_recs = recommendations.get_sorted_recommendations()
            print(f"最高推荐: {sorted_recs[0][0]} ({sorted_recs[0][1].recommendation_score})")
```

### 分析结果输入格式

```json
{
  "category": "物品类别（如：电子产品、家具等）",
  "sub_category": "子类别（如：笔记本电脑、桌子等）",
  "condition": "物品状态（如：全新、八成新、有磨损等）",
  "description": "物品详细描述",
  "brand": "品牌信息（可选）",
  "material": "材质信息（可选）",
  "keywords": ["关键词列表"],
  "special_features": "特殊特征（可选）"
}
```

### 返回结果格式

现在返回结构化的数据对象，支持类型安全和便捷操作：

```python
# 返回 DisposalRecommendationResponse 对象
response = await agent.recommend_from_analysis(analysis_result)

# 访问基本信息
print(response.success)                    # True/False
print(response.source)                     # "analysis_result"
print(response.recommendation_source)      # "ai_model" 或 "fallback"

# 访问推荐结果（结构化对象）
recommendations = response.recommendations

# 访问单个路径推荐
print(recommendations.creative_renovation.recommendation_score)    # 25
print(recommendations.creative_renovation.reason_tags)            # ["科技改造", "智能升级", "零件利用"]

print(recommendations.recycling_donation.recommendation_score)    # 60
print(recommendations.recycling_donation.reason_tags)             # ["环保回收", "数据安全", "专业处理"]

print(recommendations.secondhand_trading.recommendation_score)    # 75
print(recommendations.secondhand_trading.reason_tags)             # ["保值性好", "需求量大", "快速变现"]

# 访问总体推荐
overall = recommendations.overall_recommendation
print(overall.primary_choice)             # "二手交易"
print(overall.reason)                     # "笔记本电脑保值性好，市场需求旺盛"

# 便捷方法
sorted_recs = recommendations.get_sorted_recommendations()         # 按推荐度排序
highest_rec = recommendations.get_highest_recommendation()         # 最高推荐

# 转换为字典（兼容旧代码）
dict_result = response.to_dict()
```

## 推荐算法说明

### 1. AI模型推荐
- 使用蓝心大模型进行智能分析
- 基于物品的详细信息提供个性化建议
- 考虑市场需求、改造难度、环保价值等多维度因素
- 输出精确的数值推荐度（0-100整数）

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

## 架构优化

### 职责分离
- **分析职责**: 由上层统一进行图片/文字分析
- **推荐职责**: 专注于从分析结果生成处置路径推荐
- **高效复用**: 避免重复分析，提高响应速度

### 输入验证
- 自动验证分析结果格式
- 提供清晰的错误提示
- 支持不完整分析结果的兜底处理

### 推荐一致性
- 确保三个路径推荐度总和合理
- 提供总体推荐建议
- 标签内容简洁明确
- 推荐度输出为精确数值，便于程序处理

## 数据格式说明

### 推荐度数值
- **格式**: 0-100之间的整数
- **含义**: 数值越高表示越推荐该处置方式
- **计算**: 三个路径的推荐度总和接近100
- **输出**: 纯数字，不含百分号或其他单位

### 推荐标签
- **数量**: 每个路径3-5个标签
- **长度**: 每个标签不超过7个字
- **内容**: 简洁明确的推荐理由
- **格式**: 字符串数组

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

## 数据模型架构

### 核心数据类型

#### DisposalPathRecommendation
单个处置路径的推荐信息，包含：
- `recommendation_score: int` - 推荐度分数（0-100）
- `reason_tags: List[str]` - 推荐理由标签

#### DisposalRecommendations
完整的三大路径推荐，包含：
- `creative_renovation: DisposalPathRecommendation` - 创意改造推荐
- `recycling_donation: DisposalPathRecommendation` - 回收捐赠推荐  
- `secondhand_trading: DisposalPathRecommendation` - 二手交易推荐
- `overall_recommendation: Optional[OverallRecommendation]` - 总体推荐

便捷方法：
- `get_sorted_recommendations()` - 按推荐度排序
- `get_highest_recommendation()` - 获取最高推荐
- `to_dict()` - 转换为字典格式

#### DisposalRecommendationResponse
完整响应对象，包含：
- `success: bool` - 操作是否成功
- `source: str` - 数据来源
- `recommendations: Optional[DisposalRecommendations]` - 推荐结果
- `analysis_result: Optional[Dict]` - 输入的分析结果
- `recommendation_source: Optional[str]` - 推荐来源（AI/备用）
- `error: Optional[str]` - 错误信息

### 数据验证

所有数据模型都包含完善的验证逻辑：
- 推荐度分数范围验证（0-100）
- 标签数量和长度验证（≤5个，每个≤7字符）
- 总体推荐选项验证
- 推荐度总和合理性检查

## 依赖模块

- `app.prompts.disposal_recommendation_prompts`: 处置推荐提示词管理
- `app.models.disposal_recommendation_models`: 数据模型定义
- `app.core.config`: 配置管理
- `app.core.logger`: 日志记录
- `app.utils.vivo_auth`: VIVO API认证

## 注意事项

1. **API限制**: 需要配置有效的蓝心大模型API密钥
2. **输入格式**: 确保分析结果包含必要的字段（category、condition等）
3. **响应时间**: AI分析可能需要几秒时间，建议异步调用
4. **错误处理**: 内置完善的错误处理和备用机制
5. **资源管理**: 使用完毕后需要调用 `close()` 方法释放资源
6. **数据类型**: 现在返回结构化数据对象，提供类型安全和便捷操作
7. **向后兼容**: 可通过 `response.to_dict()` 获取字典格式，兼容旧代码

## 数据模型优势

1. **类型安全**: 编译时类型检查，减少运行时错误
2. **数据验证**: 自动验证推荐度范围、标签长度等约束
3. **便捷操作**: 提供排序、查找最高推荐等便捷方法
4. **IDE支持**: 完整的代码补全和类型提示
5. **可维护性**: 结构化数据便于后续扩展和修改
6. **调试友好**: 清晰的数据结构便于问题排查

## 与其他模块的协作

- **上层调用**: 期望上层已完成图片/文字分析，直接传入分析结果
- **下层服务**: 调用蓝心大模型服务和提示词管理服务
- **并行处理**: 可与创意改造Agent并行调用，提高整体响应速度
- **数据输出**: 结构化数据便于前端展示和后续处理
- **类型安全**: 强类型接口减少集成错误 