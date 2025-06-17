"""
LLM模型提示词管理

集中管理各种LLM模型的提示词模板
"""

from typing import Dict, Any


class LLMPrompts:
    """LLM提示词管理类"""
    
    # 文本分析相关提示词
    TEXT_ANALYSIS_SYSTEM_PROMPT = "你是一个专业的物品分析专家，擅长根据描述分析物品的详细信息。"
    
    TEXT_ANALYSIS_USER_PROMPT_TEMPLATE = """请根据以下描述分析物品信息，并以JSON格式返回：
描述：{text_description}

请返回格式：
{{
    "category": "物品大类",
    "sub_category": "物品细分类",
    "brand": "品牌（如果能推断）",
    "condition": "物品状态",
    "material": "主要材质",
    "color": "主要颜色",
    "keywords": ["关键词1", "关键词2", "关键词3"],
    "description": "标准化描述",
    "estimated_age": "估计使用年限",
    "special_features": "特殊特征"
}}"""
    
    # 图像分析相关提示词
    IMAGE_ANALYSIS_PROMPT = """请仔细分析这张图片中的物品，并以JSON格式返回详细信息：

{
    "category": "物品大类",
    "sub_category": "物品细分类", 
    "brand": "品牌（如果能识别）",
    "condition": "物品状态（全新/九成新/八成新/七成新/有磨损/损坏）",
    "material": "主要材质",
    "color": "主要颜色",
    "keywords": ["关键词1", "关键词2", "关键词3"],
    "description": "详细描述",
    "estimated_age": "估计使用年限",
    "special_features": "特殊特征或功能"
}"""
    
    @classmethod
    def get_text_analysis_prompt(cls, text_description: str) -> str:
        """获取文本分析提示词"""
        return cls.TEXT_ANALYSIS_USER_PROMPT_TEMPLATE.format(
            text_description=text_description
        )
    
    @classmethod
    def get_image_analysis_prompt(cls) -> str:
        """获取图像分析提示词"""
        return cls.IMAGE_ANALYSIS_PROMPT
    
    @classmethod
    def get_text_analysis_system_prompt(cls) -> str:
        """获取文本分析系统提示词"""
        return cls.TEXT_ANALYSIS_SYSTEM_PROMPT
    
    @classmethod
    def get_all_prompts(cls) -> Dict[str, str]:
        """获取所有提示词"""
        return {
            "text_analysis_system": cls.TEXT_ANALYSIS_SYSTEM_PROMPT,
            "text_analysis_user": cls.TEXT_ANALYSIS_USER_PROMPT_TEMPLATE,
            "image_analysis": cls.IMAGE_ANALYSIS_PROMPT,
        }
    
