"""
三大处置路径推荐提示词管理

集中管理处置路径推荐相关的LLM提示词模板
"""

from typing import Dict, Any, List


class DisposalRecommendationPrompts:
    """处置路径推荐提示词管理类"""
    
    # 系统提示词
    SYSTEM_PROMPT = """你是一个专业的闲置物品处置顾问，擅长根据物品的详细信息分析最佳的处置方案。

你需要评估三种处置路径：
1. 创意改造：将物品进行DIY改造，赋予新的功能或美化外观
2. 回收捐赠：将物品回收或捐赠给需要的人/机构  
3. 二手交易：在二手平台出售获得经济收益

你的分析应该基于以下因素：
- 物品的类别、状态、材质和价值
- 物品的改造潜力和难度
- 物品的市场需求和价值
- 物品的环保回收价值
- 用户可能的处置偏好

请始终以JSON格式返回结果，包含每种路径的推荐度和具体的推荐理由标签。"""

    # 用户提示词模板
    USER_PROMPT_TEMPLATE = """请根据以下物品分析信息，评估三大处置路径的推荐度和推荐理由：

物品分析结果：
{analysis_result}

请以JSON格式返回分析结果：
{{
    "creative_renovation": {{
        "recommendation_score": 推荐度百分比(0-100),
        "reason_tags": ["标签1", "标签2", "标签3"],
        "difficulty_level": "简单/中等/困难",
        "estimated_time": "预估耗时",
        "estimated_cost": "预估成本"
    }},
    "recycling_donation": {{
        "recommendation_score": 推荐度百分比(0-100),
        "reason_tags": ["标签1", "标签2", "标签3"],
        "environmental_impact": "环保影响评分(1-5)",
        "social_value": "社会价值评分(1-5)"
    }},
    "secondhand_trading": {{
        "recommendation_score": 推荐度百分比(0-100),
        "reason_tags": ["标签1", "标签2", "标签3"],
        "estimated_price_range": "预估价格区间",
        "market_demand": "市场需求(低/中/高)",
        "selling_difficulty": "销售难度(易/中/难)"
    }},
    "overall_recommendation": {{
        "primary_choice": "最推荐的处置方式",
        "reason": "推荐原因简述"
    }}
}}

注意事项：
- 每个推荐理由标签不超过7个字
- 推荐度总和应接近100%
- 标签要具体、实用、易懂
- 考虑物品的实际价值和处置可行性"""

    # 不同物品类别的处置倾向配置
    CATEGORY_DISPOSAL_PREFERENCES = {
        "电子产品": {
            "creative_renovation": {"base_score": 20, "tags": ["科技改造", "智能升级", "零件利用"]},
            "recycling_donation": {"base_score": 60, "tags": ["环保回收", "数据安全", "专业处理"]},
            "secondhand_trading": {"base_score": 70, "tags": ["保值性好", "需求量大", "快速变现"]}
        },
        "家具": {
            "creative_renovation": {"base_score": 80, "tags": ["翻新改造", "个性定制", "空间利用"]},
            "recycling_donation": {"base_score": 50, "tags": ["公益捐赠", "环保处理", "帮助他人"]},
            "secondhand_trading": {"base_score": 60, "tags": ["实用性强", "运输方便", "价格亲民"]}
        },
        "服装": {
            "creative_renovation": {"base_score": 70, "tags": ["时尚改造", "尺寸调整", "创意设计"]},
            "recycling_donation": {"base_score": 80, "tags": ["爱心捐赠", "循环利用", "温暖传递"]},
            "secondhand_trading": {"base_score": 40, "tags": ["款式过时", "个人用品", "卫生考虑"]}
        },
        "书籍": {
            "creative_renovation": {"base_score": 30, "tags": ["装饰利用", "手工材料", "艺术创作"]},
            "recycling_donation": {"base_score": 90, "tags": ["知识传递", "公益价值", "环保回收"]},
            "secondhand_trading": {"base_score": 50, "tags": ["知识价值", "收藏潜力", "学习需求"]}
        },
        "玩具": {
            "creative_renovation": {"base_score": 60, "tags": ["儿童创作", "教育改造", "亲子活动"]},
            "recycling_donation": {"base_score": 85, "tags": ["儿童公益", "爱心传递", "快乐分享"]},
            "secondhand_trading": {"base_score": 45, "tags": ["安全考虑", "使用痕迹", "个人物品"]}
        }
    }

    # 物品状态对推荐度的影响系数
    CONDITION_MODIFIERS = {
        "全新": {"creative": 0.8, "recycling": 0.9, "trading": 1.2},
        "九成新": {"creative": 1.0, "recycling": 1.0, "trading": 1.1},
        "八成新": {"creative": 1.1, "recycling": 1.0, "trading": 1.0},
        "七成新": {"creative": 1.2, "recycling": 1.0, "trading": 0.8},
        "有磨损": {"creative": 1.3, "recycling": 1.1, "trading": 0.6},
        "损坏": {"creative": 1.5, "recycling": 1.2, "trading": 0.3}
    }

    @classmethod
    def get_system_prompt(cls) -> str:
        """获取系统提示词"""
        return cls.SYSTEM_PROMPT

    @classmethod
    def get_user_prompt(cls, analysis_result: Dict[str, Any]) -> str:
        """获取用户提示词"""
        # 将分析结果格式化为可读的文本
        formatted_result = cls._format_analysis_result(analysis_result)
        return cls.USER_PROMPT_TEMPLATE.format(analysis_result=formatted_result)

    @classmethod
    def _format_analysis_result(cls, analysis_result: Dict[str, Any]) -> str:
        """格式化分析结果为文本"""
        formatted_parts = []
        
        for key, value in analysis_result.items():
            if isinstance(value, list):
                formatted_parts.append(f"{key}: {', '.join(map(str, value))}")
            else:
                formatted_parts.append(f"{key}: {value}")
        
        return "\n".join(formatted_parts)

    @classmethod
    def get_fallback_recommendations(
        cls, 
        category: str, 
        condition: str = "八成新"
    ) -> Dict[str, Any]:
        """获取基于类别和状态的备用推荐"""
        
        # 获取类别偏好
        category_prefs = cls.CATEGORY_DISPOSAL_PREFERENCES.get(
            category, 
            cls.CATEGORY_DISPOSAL_PREFERENCES["家具"]  # 默认使用家具的配置
        )
        
        # 获取状态修正系数
        condition_mod = cls.CONDITION_MODIFIERS.get(
            condition,
            cls.CONDITION_MODIFIERS["八成新"]  # 默认八成新
        )
        
        # 计算调整后的推荐度
        creative_score = min(100, max(0, int(
            category_prefs["creative_renovation"]["base_score"] * condition_mod["creative"]
        )))
        recycling_score = min(100, max(0, int(
            category_prefs["recycling_donation"]["base_score"] * condition_mod["recycling"]
        )))
        trading_score = min(100, max(0, int(
            category_prefs["secondhand_trading"]["base_score"] * condition_mod["trading"]
        )))
        
        # 归一化确保总和约为100%
        total = creative_score + recycling_score + trading_score
        if total > 0:
            creative_score = int((creative_score / total) * 100)
            recycling_score = int((recycling_score / total) * 100)
            trading_score = 100 - creative_score - recycling_score
        
        # 确定主要推荐
        scores = {
            "创意改造": creative_score,
            "回收捐赠": recycling_score,
            "二手交易": trading_score
        }
        primary_choice = max(scores, key=scores.get)
        
        return {
            "creative_renovation": {
                "recommendation_score": creative_score,
                "reason_tags": category_prefs["creative_renovation"]["tags"],
                "difficulty_level": "中等",
                "estimated_time": "1-3天",
                "estimated_cost": "50-200元"
            },
            "recycling_donation": {
                "recommendation_score": recycling_score,
                "reason_tags": category_prefs["recycling_donation"]["tags"],
                "environmental_impact": 4,
                "social_value": 4
            },
            "secondhand_trading": {
                "recommendation_score": trading_score,
                "reason_tags": category_prefs["secondhand_trading"]["tags"],
                "estimated_price_range": "待评估",
                "market_demand": "中",
                "selling_difficulty": "中"
            },
            "overall_recommendation": {
                "primary_choice": primary_choice,
                "reason": f"基于{category}类别和{condition}状态的综合评估"
            }
        }

    @classmethod
    def get_all_prompts(cls) -> Dict[str, str]:
        """获取所有提示词"""
        return {
            "system": cls.SYSTEM_PROMPT,
            "user_template": cls.USER_PROMPT_TEMPLATE
        } 