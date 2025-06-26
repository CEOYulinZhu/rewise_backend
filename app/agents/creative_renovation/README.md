# 创意改造步骤Agent

智能分析闲置物品并生成详细的创意改造步骤指导，基于蓝心大模型分析，为用户提供可行的改造方案和逐步操作指南。

## 功能特性

### 🎯 核心功能
- **智能分析**: 调用蓝心大模型对图片/文字进行深度分析
- **步骤生成**: 生成详细的改造步骤，包括工具、材料、时间、难度
- **安全指导**: 提供安全警告和操作建议
- **成本估算**: 预估改造所需时间和材料成本

### 📊 输入方式
1. **图片分析**: 上传物品图片，AI识别并分析
2. **文字描述**: 提供物品的文字描述
3. **分析结果**: 使用已有的物品分析结果

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
    async with CreativeRenovationAgent() as agent:
        # 从文字描述生成改造步骤
        result = await agent.generate_from_text(
            "一张旧木桌，表面有划痕但结构完好"
        )
        
        if result["success"]:
            renovation_plan = result["renovation_plan"]
            print(f"项目: {renovation_plan['project_title']}")
            print(f"难度: {renovation_plan['difficulty_level']}")
            print(f"步骤数: {len(renovation_plan['steps'])}")
            
            # 获取改造摘要
            summary = agent.get_step_summary(renovation_plan)
            print(f"所需工具: {summary['required_tools']}")
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
      "estimated_time": "预计耗时",
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