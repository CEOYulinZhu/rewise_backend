"""
文案生成提示词模块

为文案生成Agent提供专业的提示词模板
"""

from typing import Dict, Any


class ContentGenerationPrompts:
    """文案生成提示词管理器"""
    
    @staticmethod
    def get_system_prompt() -> str:
        """获取系统提示词"""
        return """你是一个专业的二手交易文案生成专家，专门为用户生成吸引人的二手交易平台标题和描述。

## 你的任务
根据用户提供的物品分析结果，生成适合在二手交易平台发布的标题和描述文案。

## 文案要求

### 标题要求 (title)
1. **字数限制**: 10-50字符，简洁有力
2. **关键信息**: 必须包含品牌、型号、成色等核心信息
3. **吸引力**: 突出卖点，使用吸引眼球的词汇
4. **真实性**: 不夸大不虚假，实事求是
5. **平台适配**: 适合主流二手交易平台的标题规范

### 描述要求 (description)
1. **字数限制**: 50-500字符，详细但不冗长
2. **结构清晰**: 包含物品详情、使用情况、交易说明
3. **卖点突出**: 强调物品优势和性价比
4. **诚信经营**: 如实描述瑕疵和使用痕迹
5. **交易信息**: 包含价格说明、交易方式等关键信息

## 文案风格
- **语言风格**: 简洁明了、亲和力强、可信度高
- **用词特点**: 避免夸大词汇，使用精准描述
- **情感色彩**: 温和友好，建立买家信任
- **专业性**: 体现对物品的了解和专业态度

## 输出格式要求
严格按照以下JSON格式输出，不要包含任何其他内容：

```json
{
  "title": "生成的标题内容",
  "description": "生成的描述内容"
}
```

## 注意事项
- 根据物品类别调整文案风格
- 突出物品的核心价值和卖点
- 如实反映物品状态，建立买家信任
- 符合二手交易平台的发布规范
- 避免使用违禁词汇和夸大宣传"""

    @staticmethod
    def get_user_prompt(analysis_result: Dict[str, Any]) -> str:
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
            item_info.append(f"详细描述: {analysis_result['description']}")
        if analysis_result.get("material"):
            item_info.append(f"材质: {analysis_result['material']}")
        if analysis_result.get("keywords"):
            item_info.append(f"关键词: {', '.join(analysis_result['keywords'])}")
        if analysis_result.get("special_features"):
            item_info.append(f"特殊功能: {analysis_result['special_features']}")
        
        item_description = "\n".join(item_info)
        
        return f"""## 待出售物品信息
{item_description}

请根据以上物品信息，生成适合在二手交易平台发布的标题和描述文案。

### 生成要求
1. **标题**: 简洁有力，突出品牌、型号、成色等关键信息
2. **描述**: 详细介绍物品状况、使用情况、交易说明等
3. **风格**: 真实可信，突出卖点，建立买家信任
4. **格式**: 严格按照JSON格式输出

请确保生成的文案既吸引买家又实事求是，符合二手交易平台的发布规范。"""

    @staticmethod
    def get_fallback_content(analysis_result: Dict[str, Any]) -> Dict[str, str]:
        """获取备用文案内容"""
        
        category = analysis_result.get("category", "闲置物品")
        brand = analysis_result.get("brand", "")
        condition = analysis_result.get("condition", "九成新")
        sub_category = analysis_result.get("sub_category", "")
        
        # 构建基础标题
        title_parts = []
        if brand:
            title_parts.append(brand)
        if sub_category:
            title_parts.append(sub_category)
        elif category:
            title_parts.append(category)
        title_parts.append(condition)
        title_parts.append("出售")
        
        title = " ".join(title_parts)
        if len(title) > 50:
            title = title[:47] + "..."
        
        # 构建基础描述
        description_parts = [
            f"出售{category}一件",
        ]
        
        if brand:
            description_parts.append(f"品牌：{brand}")
        
        if condition:
            description_parts.append(f"成色：{condition}")
        
        if analysis_result.get("description"):
            desc = analysis_result["description"]
            if len(desc) > 100:
                desc = desc[:97] + "..."
            description_parts.append(f"详情：{desc}")
        
        description_parts.extend([
            "诚信出售，实物拍摄",
            "支持当面交易，可小刀",
            "有意请私信联系"
        ])
        
        description = "，".join(description_parts) + "。"
        
        # 根据不同类别调整文案
        if category in ["电子产品", "3C数码", "手机", "电脑"]:
            if "功能正常" not in description and "使用正常" not in description:
                description = description.replace("详情：", "功能正常，详情：")
                
        elif category in ["服装", "鞋帽", "包包"]:
            if "无破损" not in description:
                description = description.replace("诚信出售", "无破损无异味，诚信出售")
                
        elif category in ["图书", "书籍"]:
            if "无划线" not in description:
                description = description.replace("诚信出售", "无划线无破页，诚信出售")
        
        return {
            "title": title,
            "description": description
        } 