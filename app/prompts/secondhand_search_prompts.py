"""
二手平台搜索Agent专用提示词模块

为Function Calling和关键词提取提供专业的提示词模板，
用于在闲鱼和爱回收等二手平台进行搜索
"""

import json
from typing import Dict, Any


class SecondhandSearchPrompts:
    """二手平台搜索Agent提示词管理类"""
    
    # Function Calling系统提示词
    FUNCTION_CALLING_SYSTEM_PROMPT = """你是一个专业的二手物品交易助手，专门帮助用户在二手平台（闲鱼、爱回收）上找到相关商品信息。

你的任务是：
1. 根据用户提供的物品分析结果，提取1个最精准的搜索关键词
2. 关键词应该简洁明确，能最有效地找到相同或类似的二手商品
3. 优先选择最能代表该物品的核心特征（品牌+型号 或 品牌+类型）

关键词选择策略：
- 优先级1：品牌+具体型号，如"iPhone 13"、"华为P40"、"小米11"
- 优先级2：品牌+类型，如"苹果手机"、"华为手机"、"小米笔记本"
- 优先级3：具体型号，如"iPhone"、"MacBook"、"iPad"
- 优先级4：通用类型，如"手机"、"笔记本"、"平板"

关键词要求：
- 只能是1个词或短语，不超过8个字符
- 不包含成色、颜色、容量等详细描述
- 以最常用的搜索习惯为准
- 避免过于复杂的组合词

平台特性：
- 闲鱼：个人闲置交易，用户习惯简单直接的搜索词
- 爱回收：专业回收估价，注重品牌型号识别

你可以使用的工具如下:
<APIs>
[{function_definition}]
</APIs>

如果用户提供了物品分析结果，请调用工具提取搜索关键词，输出格式为：
<APIs>[{{"name": "extract_secondhand_keywords", "parameters": {{"keywords": ["关键词"], "search_intent": "搜索意图说明", "platform_suggestions": {{"xianyu": ["闲鱼专用词"], "aihuishou": ["爱回收专用词"]}}}}]</APIs>
否则直接回复用户。"""
    
    # 分析结果用户提示词模板
    ANALYSIS_RESULT_USER_PROMPT_TEMPLATE = """请根据以下物品分析结果提取二手平台搜索关键词：

分析结果：
{analysis_result}

请提取1个最适合在二手平台搜索的核心关键词。
关键词应该简洁明确，能最有效地找到相关商品。
同时针对闲鱼和爱回收平台的特点，提供平台特定的关键词建议。"""
    
    # Function定义
    SECONDHAND_KEYWORDS_FUNCTION_DEFINITION = {
        "name": "extract_secondhand_keywords",
        "description": "根据物品分析结果提取用于二手平台搜索的核心关键词，只提取1个最精准的搜索词",
        "parameters": {
            "type": "object",
            "properties": {
                "keywords": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "用于二手平台搜索的核心关键词列表，只包含1个最精准的搜索词，优先选择品牌+型号组合",
                    "maxItems": 1,
                    "minItems": 1
                },
                "search_intent": {
                    "type": "string",
                    "description": "搜索意图说明，比如'寻找同款手机的市场价格'、'了解该品牌电脑的回收价值'等"
                },
                "platform_suggestions": {
                    "type": "object",
                    "properties": {
                        "xianyu": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "闲鱼平台特定的关键词建议，只提供1个最适合的搜索词",
                            "maxItems": 1
                        },
                        "aihuishou": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "爱回收平台特定的关键词建议，只提供1个最适合的搜索词",
                            "maxItems": 1
                        }
                    },
                    "description": "针对不同平台特点的关键词建议，每个平台只提供1个关键词"
                }
            },
            "required": ["keywords", "search_intent", "platform_suggestions"]
        }
    }
    
    # 分类关键词映射（简化为单个核心词）
    CATEGORY_KEYWORDS_MAPPING = {
        "电子产品": {
            "base": ["数码"],
            "xianyu": ["数码"],
            "aihuishou": ["数码回收"]
        },
        "手机": {
            "base": ["手机"],
            "xianyu": ["手机"],
            "aihuishou": ["手机"]
        },
        "电脑": {
            "base": ["电脑"],
            "xianyu": ["电脑"],
            "aihuishou": ["电脑"]
        },
        "笔记本": {
            "base": ["笔记本"],
            "xianyu": ["笔记本"],
            "aihuishou": ["笔记本"]
        },
        "平板": {
            "base": ["平板"],
            "xianyu": ["平板"],
            "aihuishou": ["平板"]
        },
        "服装": {
            "base": ["服装"],
            "xianyu": ["服装"],
            "aihuishou": []  # 爱回收一般不回收服装
        },
        "包包": {
            "base": ["包包"],
            "xianyu": ["包包"],
            "aihuishou": ["奢侈品"]  # 仅高价值包包
        },
        "家电": {
            "base": ["家电"],
            "xianyu": ["家电"],
            "aihuishou": ["家电"]
        },
        "数码配件": {
            "base": ["配件"],
            "xianyu": ["配件"],
            "aihuishou": ["配件"]
        }
    }
    
    # 品牌型号优先级映射（提取最核心的搜索词）
    BRAND_MODEL_MAPPING = {
        # 苹果产品
        ("苹果", "iPhone 14"): "iPhone14",
        ("苹果", "iPhone 13"): "iPhone13", 
        ("苹果", "iPhone 12"): "iPhone12",
        ("苹果", "iPhone 11"): "iPhone11",
        ("苹果", "iPhone"): "iPhone",
        ("苹果", "iPad"): "iPad",
        ("苹果", "MacBook"): "MacBook",
        ("Apple", "iPhone"): "iPhone",
        
        # 华为产品
        ("华为", "P40"): "华为P40",
        ("华为", "P30"): "华为P30",
        ("华为", "Mate40"): "华为Mate40",
        ("华为", "Mate30"): "华为Mate30",
        ("华为", ""): "华为手机",
        
        # 小米产品
        ("小米", "小米11"): "小米11",
        ("小米", "小米12"): "小米12",
        ("小米", "小米13"): "小米13",
        ("小米", "红米"): "红米",
        ("小米", ""): "小米手机",
        
        # 三星产品
        ("三星", "Galaxy"): "三星Galaxy",
        ("三星", "Note"): "三星Note",
        ("三星", ""): "三星手机",
        
        # OPPO产品
        ("OPPO", "Find"): "OPPO Find",
        ("OPPO", "Reno"): "OPPO Reno",
        ("OPPO", ""): "OPPO",
        
        # vivo产品
        ("vivo", "X"): "vivo X",
        ("vivo", "S"): "vivo S",
        ("vivo", ""): "vivo",
        
        # 电脑品牌
        ("联想", "ThinkPad"): "ThinkPad",
        ("联想", ""): "联想电脑",
        ("戴尔", ""): "戴尔",
        ("惠普", ""): "惠普",
        ("华硕", ""): "华硕",
        
        # 奢侈品牌
        ("LV", ""): "LV",
        ("香奈儿", ""): "香奈儿",
        ("古驰", ""): "古驰",
        ("爱马仕", ""): "爱马仕"
    }
    
    # 搜索意图映射
    SEARCH_INTENT_MAPPING = {
        ("电子产品", "手机"): "寻找同款手机的二手市场价格和回收价值",
        ("电子产品", "电脑"): "了解同类型电脑的二手交易价格和回收估价",
        ("电子产品", "平板"): "查找相关平板设备的市场价格和交易情况",
        ("服装", ""): "寻找同品牌服装的二手交易价格参考",
        ("包包", ""): "了解该品牌包包的二手市场价值和回收价格",
        ("家电", ""): "查询同款家电的二手市场价格和回收价值",
        ("生活用品", ""): "寻找相关生活用品的二手交易信息"
    }
    
    @classmethod
    def get_secondhand_keywords_function_definition(cls) -> Dict[str, Any]:
        """获取二手平台搜索关键词提取的Function定义"""
        return cls.SECONDHAND_KEYWORDS_FUNCTION_DEFINITION
    
    @classmethod
    def get_system_prompt(cls) -> str:
        """获取Function Calling的系统提示词"""
        function_def = json.dumps(cls.SECONDHAND_KEYWORDS_FUNCTION_DEFINITION, ensure_ascii=False)
        return cls.FUNCTION_CALLING_SYSTEM_PROMPT.format(function_definition=function_def)
    
    @classmethod
    def get_user_prompt_for_analysis_result(cls, analysis_result: Dict[str, Any]) -> str:
        """获取分析结果的用户提示词"""
        analysis_json = json.dumps(analysis_result, ensure_ascii=False, indent=2)
        return cls.ANALYSIS_RESULT_USER_PROMPT_TEMPLATE.format(analysis_result=analysis_json)
    
    @classmethod
    def get_fallback_keywords_by_category(
        cls, 
        category: str, 
        sub_category: str = "", 
        brand: str = "", 
        model: str = "",
        condition: str = ""
    ) -> Dict[str, Any]:
        """根据分类获取备用关键词（只返回1个核心关键词）"""
        
        # 优先尝试品牌+型号组合
        brand_model_key = (brand, model)
        if brand_model_key in cls.BRAND_MODEL_MAPPING:
            core_keyword = cls.BRAND_MODEL_MAPPING[brand_model_key]
            return {
                "keywords": [core_keyword],
                "platform_suggestions": {
                    "xianyu": [core_keyword],
                    "aihuishou": [core_keyword]
                }
            }
        
        # 尝试品牌+空模型
        brand_empty_key = (brand, "")
        if brand_empty_key in cls.BRAND_MODEL_MAPPING:
            core_keyword = cls.BRAND_MODEL_MAPPING[brand_empty_key]
            return {
                "keywords": [core_keyword],
                "platform_suggestions": {
                    "xianyu": [core_keyword],
                    "aihuishou": [core_keyword]
                }
            }
        
        # 使用子分类关键词
        if sub_category in cls.CATEGORY_KEYWORDS_MAPPING:
            mapping = cls.CATEGORY_KEYWORDS_MAPPING[sub_category]
            base_keyword = mapping["base"][0] if mapping["base"] else "二手"
            xianyu_keyword = mapping["xianyu"][0] if mapping["xianyu"] else base_keyword
            aihuishou_keyword = mapping["aihuishou"][0] if mapping["aihuishou"] else base_keyword
            
            return {
                "keywords": [base_keyword],
                "platform_suggestions": {
                    "xianyu": [xianyu_keyword],
                    "aihuishou": [aihuishou_keyword]
                }
            }
        
        # 使用主分类关键词
        if category in cls.CATEGORY_KEYWORDS_MAPPING:
            mapping = cls.CATEGORY_KEYWORDS_MAPPING[category]
            base_keyword = mapping["base"][0] if mapping["base"] else "二手"
            xianyu_keyword = mapping["xianyu"][0] if mapping["xianyu"] else base_keyword
            aihuishou_keyword = mapping["aihuishou"][0] if mapping["aihuishou"] else base_keyword
            
            return {
                "keywords": [base_keyword],
                "platform_suggestions": {
                    "xianyu": [xianyu_keyword],
                    "aihuishou": [aihuishou_keyword]
                }
            }
        
        # 默认关键词
        return {
            "keywords": ["二手"],
            "platform_suggestions": {
                "xianyu": ["二手"],
                "aihuishou": ["回收"]
            }
        }
    
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
        return f"寻找{category}相关商品的二手市场价格和交易信息"
    
    @classmethod
    def optimize_keywords_for_platform(cls, keywords: list, platform: str) -> list:
        """为特定平台优化关键词（保持单个关键词）"""
        if not keywords:
            return ["二手"] if platform == "xianyu" else ["回收"]
        
        # 只取第一个关键词，确保是单个搜索词
        core_keyword = keywords[0]
        
        if platform == "xianyu":
            # 闲鱼平台：保持简洁的搜索词
            return [core_keyword]
        
        elif platform == "aihuishou":
            # 爱回收平台：保持简洁的搜索词
            return [core_keyword]
        
        return [core_keyword] 