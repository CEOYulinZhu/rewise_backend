"""
Bilibili搜索Agent专用提示词模块

为Function Calling和关键词提取提供专业的提示词模板
"""

import json
from typing import Dict, Any


class BilibiliSearchPrompts:
    """Bilibili搜索Agent提示词管理类"""
    
    # Function Calling系统提示词
    FUNCTION_CALLING_SYSTEM_PROMPT = """你是一个专业的闲置物品处置助手，专门帮助用户找到合适的DIY改造或处置教程视频。

你的任务是：
1. 根据用户提供的物品分析结果，智能提取适合在B站搜索的关键词
2. 关键词应该有助于找到DIY改造、废物利用、创意制作等相关教程视频
3. 优先考虑物品的类型、材料、状态等特征
4. 添加"DIY"、"改造"、"手工"等相关词汇提高搜索精度

关键词提取原则：
- 物品类型：如"塑料瓶"、"纸箱"、"T恤"等
- 材料特征：如"塑料"、"纸质"、"棉布"等
- 改造方向：如"收纳"、"装饰"、"实用"等
- 技术关键词：如"DIY"、"改造"、"手工"、"创意"等
- 避免过于宽泛的词汇，确保搜索精准度

你可以使用的工具如下:
<APIs>
[{function_definition}]
</APIs>

如果用户提供了物品分析结果，请调用工具提取搜索关键词，输出格式为：
<APIs>[{{"name": "extract_search_keywords", "parameters": {{"keywords": ["关键词1", "关键词2"], "search_intent": "搜索意图说明"}}}}]</APIs>
否则直接回复用户。"""
    
    # 图片分析用户提示词模板
    IMAGE_ANALYSIS_USER_PROMPT_TEMPLATE = """请根据以下图片分析结果提取B站搜索关键词：

分析结果：
{analysis_result}

请提取3-5个最适合在B站搜索DIY改造教程的关键词，并说明搜索意图。"""
    
    # 文字分析用户提示词模板
    TEXT_ANALYSIS_USER_PROMPT_TEMPLATE = """请根据以下文字分析结果提取B站搜索关键词：

分析结果：
{analysis_result}

请提取3-5个最适合在B站搜索DIY改造教程的关键词，并说明搜索意图。"""
    
    # Function定义
    SEARCH_KEYWORDS_FUNCTION_DEFINITION = {
        "name": "extract_search_keywords",
        "description": "根据物品分析结果提取用于B站搜索的关键词，用于找到相关的DIY改造或处置教程视频",
        "parameters": {
            "type": "object",
            "properties": {
                "keywords": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "用于B站搜索的关键词列表，应包含物品类型、材料、DIY相关词汇等，3-5个关键词"
                },
                "search_intent": {
                    "type": "string",
                    "description": "搜索意图说明，比如'寻找旧衣服改造教程'、'学习废纸盒DIY方法'等"
                }
            },
            "required": ["keywords", "search_intent"]
        }
    }
    
    # 分类关键词映射
    CATEGORY_KEYWORDS_MAPPING = {
        "生活用品": ["生活用品", "日用品"],
        "服装": ["衣服", "服装"],
        "电子产品": ["电子产品", "数码"],
        "家具": ["家具", "木制品"],
        "玩具": ["玩具", "手工"],
        "文具": ["文具", "办公用品"],
        "厨具": ["厨具", "餐具"],
        "装饰品": ["装饰", "摆件"]
    }
    
    # 子分类关键词映射
    SUB_CATEGORY_KEYWORDS_MAPPING = {
        "塑料瓶": ["塑料瓶", "矿泉水瓶", "饮料瓶"],
        "纸箱": ["纸箱", "快递盒", "包装盒"],
        "T恤": ["T恤", "短袖", "旧衣"],
        "牛仔裤": ["牛仔裤", "裤子"],
        "手机": ["手机", "旧手机"],
        "鞋子": ["鞋子", "旧鞋"],
        "书籍": ["书", "旧书"],
        "玻璃瓶": ["玻璃瓶", "瓶子"]
    }
    
    # 材料关键词映射
    MATERIAL_KEYWORDS_MAPPING = {
        "塑料": ["塑料"],
        "纸质": ["纸", "纸质"],
        "棉布": ["棉布", "布料"],
        "牛仔": ["牛仔", "丹宁"],
        "玻璃": ["玻璃"],
        "金属": ["金属"],
        "木制": ["木头", "木制"]
    }
    
    # 搜索意图映射
    SEARCH_INTENT_MAPPING = {
        ("生活用品", "塑料瓶"): "寻找塑料瓶创意改造教程，制作收纳容器或装饰品",
        ("生活用品", "纸箱"): "学习纸箱DIY方法，制作收纳盒或儿童玩具",
        ("服装", "T恤"): "寻找旧T恤改造教程，制作购物袋或抹布",
        ("服装", "牛仔裤"): "学习牛仔裤改造技巧，制作包包或装饰品",
        ("电子产品", "手机"): "了解旧手机处理方法和创意利用",
        ("家具", ""): "寻找家具翻新和改造教程",
        ("玩具", ""): "学习玩具修复和创意改造方法",
        ("文具", ""): "寻找文具创意利用和收纳方法",
        ("厨具", ""): "学习厨具清洁保养和创意利用",
        ("装饰品", ""): "寻找装饰品改造和创意制作教程"
    }
    
    @classmethod
    def get_search_keywords_function_definition(cls) -> Dict[str, Any]:
        """获取搜索关键词提取的Function定义"""
        return cls.SEARCH_KEYWORDS_FUNCTION_DEFINITION
    
    @classmethod
    def get_system_prompt(cls) -> str:
        """获取Function Calling的系统提示词"""
        function_def = json.dumps(cls.SEARCH_KEYWORDS_FUNCTION_DEFINITION, ensure_ascii=False)
        return cls.FUNCTION_CALLING_SYSTEM_PROMPT.format(function_definition=function_def)
    
    @classmethod
    def get_user_prompt_for_image_analysis(cls, analysis_result: Dict[str, Any]) -> str:
        """获取图片分析结果的用户提示词"""
        analysis_json = json.dumps(analysis_result, ensure_ascii=False, indent=2)
        return cls.IMAGE_ANALYSIS_USER_PROMPT_TEMPLATE.format(analysis_result=analysis_json)
    
    @classmethod
    def get_user_prompt_for_text_analysis(cls, analysis_result: Dict[str, Any]) -> str:
        """获取文字分析结果的用户提示词"""
        analysis_json = json.dumps(analysis_result, ensure_ascii=False, indent=2)
        return cls.TEXT_ANALYSIS_USER_PROMPT_TEMPLATE.format(analysis_result=analysis_json)
    
    @classmethod
    def get_fallback_keywords_by_category(cls, category: str, sub_category: str = "", material: str = "") -> list:
        """根据分类获取备用关键词"""
        keywords = []
        
        # 添加分类关键词
        if category in cls.CATEGORY_KEYWORDS_MAPPING:
            keywords.extend(cls.CATEGORY_KEYWORDS_MAPPING[category])
        
        # 添加子分类关键词
        if sub_category in cls.SUB_CATEGORY_KEYWORDS_MAPPING:
            keywords.extend(cls.SUB_CATEGORY_KEYWORDS_MAPPING[sub_category])
        
        # 添加材料关键词
        if material in cls.MATERIAL_KEYWORDS_MAPPING:
            keywords.extend(cls.MATERIAL_KEYWORDS_MAPPING[material])
        
        # 添加通用DIY关键词
        keywords.extend(["DIY", "改造", "手工"])
        
        # 去重并限制数量
        unique_keywords = list(dict.fromkeys(keywords))[:5]
        
        return unique_keywords
    
    @classmethod
    def get_search_intent_by_category(cls, category: str, sub_category: str = "") -> str:
        """根据分类生成搜索意图说明"""
        # 精确匹配
        key = (category, sub_category)
        if key in cls.SEARCH_INTENT_MAPPING:
            return cls.SEARCH_INTENT_MAPPING[key]
        
        # 分类匹配
        key = (category, "")
        if key in cls.SEARCH_INTENT_MAPPING:
            return cls.SEARCH_INTENT_MAPPING[key]
        
        # 默认意图
        return f"寻找{category}相关的DIY改造和创意利用教程"
    
    @classmethod
    def get_all_prompts(cls) -> Dict[str, str]:
        """获取所有提示词"""
        return {
            "function_calling_system": cls.FUNCTION_CALLING_SYSTEM_PROMPT,
            "image_analysis_user": cls.IMAGE_ANALYSIS_USER_PROMPT_TEMPLATE,
            "text_analysis_user": cls.TEXT_ANALYSIS_USER_PROMPT_TEMPLATE,
        }
