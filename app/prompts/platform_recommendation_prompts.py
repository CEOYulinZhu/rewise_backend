"""
平台推荐提示词模块

为平台推荐Agent提供专业的提示词模板
"""

from typing import Dict, Any, List


class PlatformRecommendationPrompts:
    """平台推荐提示词管理器"""
    
    @staticmethod
    def get_system_prompt() -> str:
        """获取系统提示词"""
        return """你是一个专业的二手交易平台推荐专家，专门为用户推荐最合适的二手交易平台。

## 你的任务
根据用户提供的物品分析结果和检索到的平台信息，为用户推荐1-3个最适合的二手交易平台。

## 分析维度
1. **物品特性匹配度**: 平台是否专注于该类别物品
2. **用户群体适配**: 平台用户群体是否与物品目标用户匹配
3. **交易便利性**: 平台的交易流程和保障机制
4. **变现能力**: 平台的活跃度和成交能力
5. **手续费用**: 平台的费用结构

## 评分标准 (suitability_score: 0-10)
- 9-10: 完美匹配，强烈推荐
- 7-8: 高度匹配，推荐
- 5-6: 中等匹配，可考虑  
- 3-4: 低匹配度，不太推荐
- 0-2: 不匹配，不推荐

## 输出格式要求
严格按照以下JSON格式输出，不要包含任何其他内容：

```json
{
  "recommendations": [
    {
      "platform_name": "平台名称",
      "suitability_score": 评分数字,
      "pros": ["优势1", "优势2", "优势3"],
      "cons": ["劣势1", "劣势2"],
      "recommendation_reason": "推荐理由说明"
    }
  ]
}
```

## 注意事项
- 必须推荐1-3个平台
- 优势最多3个，劣势最多2个，每个描述不超过20字符
- 推荐理由要具体且有说服力
- 按适合度从高到低排序"""

    @staticmethod
    def get_user_prompt(analysis_result: Dict[str, Any], rag_results: List[Dict[str, Any]]) -> str:
        """获取用户提示词"""
        
        # 构建物品分析信息
        item_info = []
        if analysis_result.get("category"):
            item_info.append(f"类别: {analysis_result['category']}")
        if analysis_result.get("sub_category"):
            item_info.append(f"子类别: {analysis_result['sub_category']}")
        if analysis_result.get("brand"):
            item_info.append(f"品牌: {analysis_result['brand']}")
        if analysis_result.get("condition"):
            item_info.append(f"成色: {analysis_result['condition']}")
        if analysis_result.get("description"):
            item_info.append(f"描述: {analysis_result['description']}")
        if analysis_result.get("keywords"):
            item_info.append(f"关键词: {', '.join(analysis_result['keywords'])}")
        
        item_description = "\n".join(item_info)
        
        # 构建平台信息
        platform_info = []
        for i, platform in enumerate(rag_results, 1):
            platform_data = platform.get("raw_platform_data", {})
            metadata = platform.get("metadata", {})
            
            platform_desc = [
                f"## 平台 {i}: {platform_data.get('platform_name', 'Unknown')}",
                f"描述: {platform_data.get('description', '')}",
                f"主要品类: {', '.join(platform_data.get('focus_categories', []))}",
                f"平台特色: {', '.join(platform_data.get('tags', []))}",
                f"交易模式: {platform_data.get('transaction_model', '')}",
                f"相似度得分: {platform.get('similarity', 0):.3f}"
            ]
            
            # 添加用户数据
            user_data = platform_data.get('user_data', {})
            if user_data.get('monthly_active_users'):
                platform_desc.append(f"月活用户: {user_data['monthly_active_users']}")
            
            # 添加评分信息
            rating = platform_data.get('rating', {})
            if rating:
                rating_info = []
                for store, score in rating.items():
                    if score:
                        rating_info.append(f"{store}: {score}")
                if rating_info:
                    platform_desc.append(f"用户评分: {', '.join(rating_info)}")
            
            platform_info.append("\n".join(platform_desc))
        
        platforms_description = "\n\n".join(platform_info)
        
        return f"""## 待出售物品信息
{item_description}

## 检索到的相关平台信息
{platforms_description}

请根据以上物品信息和平台信息，为用户推荐1-3个最适合的二手交易平台。考虑物品特性、平台特色、用户群体、交易便利性等因素，给出专业的推荐建议。"""

    @staticmethod
    def get_fallback_recommendations(category: str) -> Dict[str, Any]:
        """获取备用推荐结果"""
        
        # 根据类别提供基础推荐
        if category in ["电子产品", "3C数码", "手机", "电脑", "数码产品"]:
            return {
                "recommendations": [
                    {
                        "platform_name": "闲鱼",
                        "suitability_score": 8.5,
                        "pros": ["用户量大", "交易便捷", "支付宝保障"],
                        "cons": ["竞争激烈", "价格透明度低"],
                        "recommendation_reason": "电子产品在闲鱼有庞大的用户群体，交易活跃度高"
                    },
                    {
                        "platform_name": "转转",
                        "suitability_score": 7.8,
                        "pros": ["官方验机", "AI检测", "专业保障"],
                        "cons": ["手续费较高"],
                        "recommendation_reason": "专注3C数码，提供专业的验机服务，适合高价值电子产品"
                    }
                ]
            }
        elif category in ["图书", "书籍", "古籍"]:
            return {
                "recommendations": [
                    {
                        "platform_name": "孔夫子旧书网",
                        "suitability_score": 9.0,
                        "pros": ["专业图书平台", "收藏价值高", "文化氛围浓"],
                        "cons": ["用户群体较小"],
                        "recommendation_reason": "专业的古旧书交易平台，对图书收藏者具有很强的吸引力"
                    },
                    {
                        "platform_name": "多抓鱼",
                        "suitability_score": 7.5,
                        "pros": ["回收便捷", "质量保证", "环保理念"],
                        "cons": ["价格较低"],
                        "recommendation_reason": "专注二手书循环，提供便捷的回收和销售服务"
                    }
                ]
            }
        else:
            # 通用推荐
            return {
                "recommendations": [
                    {
                        "platform_name": "闲鱼",
                        "suitability_score": 7.5,
                        "pros": ["全品类覆盖", "用户量大", "交易便捷"],
                        "cons": ["竞争激烈"],
                        "recommendation_reason": "作为全品类平台，适合各种类型的二手物品交易"
                    }
                ]
            } 