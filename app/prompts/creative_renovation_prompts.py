"""
创意改造步骤提示词管理

管理创意改造Agent相关的提示词模板，用于生成详细的改造步骤指导
"""

from typing import Dict, Any, List


class CreativeRenovationPrompts:
    """创意改造步骤提示词管理类"""
    
    # 系统提示词
    SYSTEM_PROMPT = """你是一位专业的创意改造专家，擅长将闲置物品通过创意改造转换为新的实用物品。
你需要根据物品的分析结果，提供详细的改造步骤指导。

你的回答必须严格按照以下JSON格式返回，不要添加任何额外的文字说明：

{
    "project_title": "改造项目标题",
    "project_description": "改造项目整体描述和预期效果",
    "difficulty_level": "简单/中等/困难",
    "estimated_cost_range": {
        "min_cost": 数字（最低成本，单位：元）,
        "max_cost": 数字（最高成本，单位：元）,
        "cost_description": "成本说明"
    },
    "required_skills": ["需要的技能1", "需要的技能2"],
    "safety_warnings": ["安全注意事项1", "安全注意事项2"],
    "steps": [
        {
            "step_number": 1,
            "title": "步骤标题",
            "description": "详细的操作描述",
            "tools_needed": ["工具1", "工具2"],
            "materials_needed": ["材料1", "材料2"],
            "estimated_time_minutes": 数字（预计耗时分钟数）,
            "difficulty": "简单/中等/困难",
            "tips": ["小贴士1", "小贴士2"],
            "image_description": "建议配图描述（如果需要图片说明）"
        }
    ],
    "final_result": {
        "description": "最终成品描述",
        "usage_scenarios": ["使用场景1", "使用场景2"],
        "maintenance_tips": ["保养建议1", "保养建议2"]
    },
    "alternative_ideas": [
        {
            "title": "替代方案标题",
            "description": "替代改造方案简述"
        }
    ]
}

请确保：
1. 步骤要详细具体，新手也能理解
2. 工具和材料要现实可获得
3. 时间用分钟数表示，成本用数字范围表示，便于统计
4. 安全提醒要充分
5. 改造方案要有创意和实用性"""

    # 用户提示词模板
    USER_PROMPT_TEMPLATE = """请根据以下物品分析结果，设计一个创意改造方案，并提供详细的步骤指导：

物品信息：
- 类别：{category}
- 子类别：{sub_category}
- 品牌：{brand}
- 状态：{condition}
- 材质：{material}
- 颜色：{color}
- 描述：{description}
- 关键词：{keywords}
- 特殊特征：{special_features}

请考虑以下因素：
1. 物品的现状和可改造性
2. 改造的实用性和美观性
3. 改造的可行性和成本
4. 安全性和持久性
5. 创意性和个性化

请提供一个完整的改造方案，包括详细步骤、所需工具材料、时间成本估算等。"""

    # 简化版用户提示词（当分析结果不完整时使用）
    SIMPLE_USER_PROMPT_TEMPLATE = """请根据以下物品信息，设计一个创意改造方案：

物品描述：{description}
物品类别：{category}
物品状态：{condition}

请提供详细的改造步骤指导，包括所需工具、材料、时间和成本估算。"""

    # 不同类别物品的改造倾向配置
    CATEGORY_RENOVATION_PREFERENCES = {
        "家具": {
            "优势": ["结构稳固", "改造空间大", "实用性强"],
            "常见改造": ["重新刷漆", "功能改造", "风格变换", "组合拼接"],
            "难度系数": 0.7,
            "成本系数": 0.6
        },
        "电子产品": {
            "优势": ["功能性强", "科技感", "可集成性"],
            "常见改造": ["外观定制", "功能扩展", "装饰改造", "组件利用"],
            "难度系数": 0.8,
            "成本系数": 0.5
        },
        "服装配饰": {
            "优势": ["材料多样", "个性化", "时尚性"],
            "常见改造": ["款式改造", "装饰添加", "材料再利用", "功能转换"],
            "难度系数": 0.6,
            "成本系数": 0.4
        },
        "生活用品": {
            "优势": ["实用性", "材料适应性", "改造灵活性"],
            "常见改造": ["功能转换", "装饰美化", "组合利用", "创意应用"],
            "难度系数": 0.5,
            "成本系数": 0.3
        },
        "艺术品": {
            "优势": ["美观性", "装饰性", "文化价值"],
            "常见改造": ["修复美化", "风格融合", "功能添加", "创意展示"],
            "难度系数": 0.9,
            "成本系数": 0.7
        },
        "运动器材": {
            "优势": ["结构坚固", "材料优质", "功能性"],
            "常见改造": ["用途转换", "装饰改造", "功能整合", "创意利用"],
            "难度系数": 0.6,
            "成本系数": 0.5
        }
    }

    # 物品状态对改造方案的影响
    CONDITION_IMPACT = {
        "全新": {
            "改造建议": "保持原有功能基础上增加美观性",
            "难度调整": 0.8,
            "成本调整": 1.2,
            "注意事项": ["保持原有价值", "避免过度改造"]
        },
        "九成新": {
            "改造建议": "适度改造，注重实用性提升",
            "难度调整": 0.9,
            "成本调整": 1.0,
            "注意事项": ["评估改造价值", "保留核心功能"]
        },
        "八成新": {
            "改造建议": "平衡美观与实用，适合中等改造",
            "难度调整": 1.0,
            "成本调整": 0.9,
            "注意事项": ["检查结构完整性", "合理利用现有材料"]
        },
        "七成新": {
            "改造建议": "重点修复和功能改造",
            "难度调整": 1.1,
            "成本调整": 0.8,
            "注意事项": ["先修复再改造", "注意安全性"]
        },
        "有磨损": {
            "改造建议": "创意遮盖磨损，转换用途",
            "难度调整": 1.2,
            "成本调整": 0.7,
            "注意事项": ["巧妙处理磨损", "确保结构安全"]
        },
        "损坏": {
            "改造建议": "部件利用或艺术创作",
            "难度调整": 1.3,
            "成本调整": 0.6,
            "注意事项": ["安全第一", "材料再利用"]
        }
    }

    @classmethod
    def get_system_prompt(cls) -> str:
        """获取系统提示词"""
        return cls.SYSTEM_PROMPT

    @classmethod
    def get_user_prompt(cls, analysis_result: Dict[str, Any]) -> str:
        """获取用户提示词"""
        
        # 提取分析结果中的各个字段，提供默认值
        category = analysis_result.get("category", "未知")
        sub_category = analysis_result.get("sub_category", "未知")
        brand = analysis_result.get("brand", "未知")
        condition = analysis_result.get("condition", "未知")
        material = analysis_result.get("material", "未知")
        color = analysis_result.get("color", "未知")
        description = analysis_result.get("description", "")
        keywords = analysis_result.get("keywords", [])
        special_features = analysis_result.get("special_features", "无")
        
        # 如果信息不够完整，使用简化版提示词
        if not description or category == "未知":
            return cls.SIMPLE_USER_PROMPT_TEMPLATE.format(
                description=description or "物品描述不详",
                category=category,
                condition=condition
            )
        
        # 格式化关键词列表
        keywords_str = "、".join(keywords) if keywords else "无"
        
        return cls.USER_PROMPT_TEMPLATE.format(
            category=category,
            sub_category=sub_category,
            brand=brand,
            condition=condition,
            material=material,
            color=color,
            description=description,
            keywords=keywords_str,
            special_features=special_features
        )

    @classmethod
    def get_category_preferences(cls, category: str) -> Dict[str, Any]:
        """获取指定类别的改造偏好"""
        # 尝试精确匹配
        if category in cls.CATEGORY_RENOVATION_PREFERENCES:
            return cls.CATEGORY_RENOVATION_PREFERENCES[category]
        
        # 尝试模糊匹配
        for cat_key in cls.CATEGORY_RENOVATION_PREFERENCES.keys():
            if cat_key in category or category in cat_key:
                return cls.CATEGORY_RENOVATION_PREFERENCES[cat_key]
        
        # 返回默认配置
        return {
            "优势": ["可改造性", "实用潜力"],
            "常见改造": ["功能改造", "外观美化"],
            "难度系数": 0.7,
            "成本系数": 0.6
        }

    @classmethod
    def get_condition_impact(cls, condition: str) -> Dict[str, Any]:
        """获取物品状态对改造的影响"""
        return cls.CONDITION_IMPACT.get(condition, cls.CONDITION_IMPACT["八成新"])

    @classmethod
    def get_fallback_renovation_plan(cls, category: str, condition: str, description: str) -> Dict[str, Any]:
        """获取备用改造方案（当AI调用失败时使用）"""
        
        preferences = cls.get_category_preferences(category)
        condition_impact = cls.get_condition_impact(condition)
        
        # 根据类别生成基础方案
        if "家具" in category:
            project_title = f"{category}创意翻新改造"
            steps = [
                {
                    "step_number": 1,
                    "title": "清洁和检查",
                    "description": "彻底清洁物品表面，检查结构完整性",
                    "tools_needed": ["清洁剂", "抹布", "刷子"],
                    "materials_needed": ["清洁用品"],
                    "estimated_time_minutes": 30,
                    "difficulty": "简单",
                    "tips": ["注意检查连接处是否松动"],
                    "image_description": "清洁前后对比图"
                },
                {
                    "step_number": 2,
                    "title": "表面处理",
                    "description": "打磨旧漆面，为重新涂装做准备",
                    "tools_needed": ["砂纸", "电动砂光机"],
                    "materials_needed": ["不同粗细砂纸"],
                    "estimated_time_minutes": 90,
                    "difficulty": "中等",
                    "tips": ["由粗到细依次打磨", "佩戴防护用品"],
                    "image_description": "打磨过程示意图"
                },
                {
                    "step_number": 3,
                    "title": "涂装装饰",
                    "description": "选择合适的涂料进行重新涂装",
                    "tools_needed": ["刷子", "滚筒", "喷枪"],
                    "materials_needed": ["底漆", "面漆", "保护漆"],
                    "estimated_time_minutes": 150,
                    "difficulty": "中等",
                    "tips": ["薄涂多遍", "等待充分干燥"],
                    "image_description": "涂装步骤图解"
                }
            ]
        elif "电子产品" in category:
            project_title = f"{category}创意外观定制"
            steps = [
                {
                    "step_number": 1,
                    "title": "拆解和清洁",
                    "description": "小心拆解外壳，清洁内部组件",
                    "tools_needed": ["螺丝刀", "镊子", "清洁剂"],
                    "materials_needed": ["清洁用品", "防静电手套"],
                    "estimated_time_minutes": 45,
                    "difficulty": "中等",
                    "tips": ["记录拆解步骤", "防止静电损坏"],
                    "image_description": "拆解步骤图"
                },
                {
                    "step_number": 2,
                    "title": "外壳设计",
                    "description": "设计新的外观样式或添加装饰元素",
                    "tools_needed": ["设计软件", "打印机"],
                    "materials_needed": ["贴纸", "喷漆", "装饰材料"],
                    "estimated_time_minutes": 60,
                    "difficulty": "简单",
                    "tips": ["先设计草图", "选择适合的材料"],
                    "image_description": "设计效果图"
                }
            ]
        else:
            project_title = f"{category}创意改造"
            steps = [
                {
                    "step_number": 1,
                    "title": "评估和规划",
                    "description": "分析物品当前状态，规划改造方案",
                    "tools_needed": ["尺子", "笔记本"],
                    "materials_needed": [],
                    "estimated_time_minutes": 20,
                    "difficulty": "简单",
                    "tips": ["仔细观察可改造的地方"],
                    "image_description": "规划草图"
                },
                {
                    "step_number": 2,
                    "title": "基础改造",
                    "description": "进行基础的清洁、修复或改造工作",
                    "tools_needed": ["基础工具"],
                    "materials_needed": ["改造材料"],
                    "estimated_time_minutes": 90,
                    "difficulty": "中等",
                    "tips": ["循序渐进", "注意安全"],
                    "image_description": "改造过程图"
                }
            ]
        
        return {
            "project_title": project_title,
            "project_description": f"将{description}进行创意改造，提升实用性和美观性",
            "difficulty_level": "中等",
            "estimated_cost_range": {
                "min_cost": 50,
                "max_cost": 150,
                "cost_description": "基础改造材料成本"
            },
            "required_skills": preferences["常见改造"][:2],
            "safety_warnings": ["佩戴防护用品", "注意工具使用安全", "保持工作环境整洁"],
            "steps": steps,
            "final_result": {
                "description": f"焕然一新的{category}，兼具实用性和美观性",
                "usage_scenarios": ["日常使用", "装饰展示"],
                "maintenance_tips": ["定期清洁", "避免重压", "防潮防晒"]
            },
            "alternative_ideas": [
                {
                    "title": "简化版改造",
                    "description": "仅进行外观美化，不改变核心功能"
                },
                {
                    "title": "功能转换",
                    "description": "改变物品的使用用途，发挥新的实用价值"
                }
            ]
        } 