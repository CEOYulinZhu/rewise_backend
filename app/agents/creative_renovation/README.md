# 创意改造步骤Agent

智能分析闲置物品并生成详细的创意改造步骤指导，基于蓝心大模型分析，为用户提供可行的改造方案和逐步操作指南。

## 功能特性

### 🎯 核心功能
- **智能步骤生成**: 基于物品分析结果生成详细的改造步骤
- **AI驱动方案**: 使用蓝心大模型进行创意改造方案设计
- **备用机制**: 当AI模型不可用时，提供基于规则的备用改造方案
- **详细指导**: 包含工具、材料、时间、难度等完整信息

### 📊 输入方式
- **分析结果输入**: 接收上层传入的物品分析结果（包含category、condition、description等信息）

### 🔧 输出内容
- **项目信息**: 改造标题、描述、难度等级
- **详细步骤**: 每步操作说明、所需工具材料
- **时间成本**: 总体和分步的时间、成本估算
- **安全提醒**: 操作安全注意事项
- **替代方案**: 其他可行的改造思路

## 使用示例

```python
from app.agents.creative_renovation import CreativeRenovationAgent

async def example_usage():
    # 准备物品分析结果
    analysis_result = {
        "category": "家具",
        "sub_category": "桌子",
        "condition": "八成新",
        "description": "一张旧木桌，表面有划痕但结构完好",
        "material": "木质",
        "color": "棕色",
        "keywords": ["桌子", "木质", "家具"]
    }
    
    async with CreativeRenovationAgent() as agent:
        # 从分析结果生成改造步骤
        result = await agent.generate_from_analysis(analysis_result)
        
        if result["success"]:
            renovation_plan = result["renovation_plan"]
            print(f"项目: {renovation_plan['project_title']}")
            print(f"难度: {renovation_plan['difficulty_level']}")
            print(f"步骤数: {len(renovation_plan['steps'])}")
            
            # 获取改造摘要
            summary = agent.get_step_summary(renovation_plan)
            print(f"摘要信息: {summary}")
```

## 分析结果输入格式

```json
{
  "category": "物品类别（如：家具、电子产品等）",
  "sub_category": "子类别（如：桌子、椅子等）",
  "condition": "物品状态（如：全新、八成新、有磨损等）",
  "description": "物品详细描述",
  "material": "材质信息（可选）",
  "color": "颜色信息（可选）",
  "keywords": ["关键词列表"],
  "special_features": "特殊特征（可选）"
}
```

## 改造方案结构

```json
{
  "project_title": "改造项目标题",
  "project_description": "改造项目整体描述",
  "difficulty_level": "简单/中等/困难",
  "estimated_total_time": "总体预计耗时",
  "estimated_total_cost": "总体预计成本",
  "required_skills": ["所需技能列表"],
  "safety_warnings": ["安全注意事项"],
  "steps": [
    {
      "step_number": 1,
      "title": "步骤标题",
      "description": "详细操作描述",
      "tools_needed": ["所需工具"],
      "materials_needed": ["所需材料"],
      "estimated_time_minutes": 30,
      "difficulty": "难度等级",
      "tips": ["操作小贴士"]
    }
  ],
  "final_result": {
    "description": "最终成品描述",
    "usage_scenarios": ["使用场景"],
    "maintenance_tips": ["保养建议"]
  },
  "alternative_ideas": [
    {
      "title": "替代方案标题",
      "description": "替代方案描述"
    }
  ]
}
```

## 支持的物品类别

| 类别 | 改造特点 | 常见改造方向 |
|------|----------|-------------|
| 家具 | 结构稳固，改造空间大 | 重新刷漆、功能改造、风格变换 |
| 电子产品 | 功能性强，科技感 | 外观定制、功能扩展、装饰改造 |
| 服装配饰 | 材料多样，个性化 | 款式改造、装饰添加、材料再利用 |
| 生活用品 | 实用性强，灵活性高 | 功能转换、装饰美化、组合利用 |
| 艺术品 | 美观性，装饰性 | 修复美化、风格融合、功能添加 |
| 运动器材 | 结构坚固，材料优质 | 用途转换、装饰改造、功能整合 |

## 物品状态影响

- **全新**: 保持原有功能基础上增加美观性
- **九成新**: 适度改造，注重实用性提升  
- **八成新**: 平衡美观与实用，适合中等改造
- **七成新**: 重点修复和功能改造
- **有磨损**: 创意遮盖磨损，转换用途
- **损坏**: 部件利用或艺术创作

## 备用机制

当AI模型调用失败时，系统会自动启用备用改造方案生成机制，基于物品类别和状态提供基础的改造建议，确保功能的稳定性和可用性。

## 架构优化

### 职责分离
- **分析职责**: 由上层统一进行图片/文字分析
- **改造职责**: 专注于从分析结果生成改造步骤
- **高效复用**: 避免重复分析，提高响应速度

### 输入验证
- 自动验证分析结果格式
- 提供清晰的错误提示
- 支持不完整分析结果的兜底处理

### 摘要功能
- `get_step_summary()`: 获取改造方案摘要
- `get_detailed_overview()`: 获取详细概览
- `generate_summary_text()`: 生成文本摘要

## 测试

```bash
# 运行完整测试套件
pytest tests/agents/creative_renovation/

# 运行简单测试
python tests/agents/creative_renovation/test_agent.py
```

## 依赖模块

- `app.services.renovation_summary_service`: 改造方案摘要服务
- `app.prompts.creative_renovation_prompts`: 创意改造提示词管理
- `app.core.config`: 配置管理
- `app.core.logger`: 日志记录
- `app.utils.vivo_auth`: VIVO API认证

## 注意事项

1. **API限制**: 需要配置有效的蓝心大模型API密钥
2. **输入格式**: 确保分析结果包含必要的字段（category、condition等）
3. **响应时间**: AI分析可能需要几秒时间，建议异步调用
4. **错误处理**: 内置完善的错误处理和备用机制
5. **资源管理**: 使用完毕后需要调用 `close()` 方法释放资源 