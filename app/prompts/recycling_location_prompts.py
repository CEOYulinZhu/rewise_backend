"""
回收地点推荐提示词管理

集中管理回收类型分析相关的LLM提示词模板
"""

from typing import Dict, Any, List


class RecyclingLocationPrompts:
    """回收地点推荐提示词管理类"""
    
    # 系统提示词
    SYSTEM_PROMPT = """你是一个专业的回收分类专家，擅长根据物品的详细信息判断其所属的回收类型。

你需要根据物品分析结果，准确判断物品所属的回收类型。回收类型固定为以下四种，每个物品只能属于其中一种：

1. 家电回收：包括电视、冰箱、洗衣机、空调、微波炉、电饭煲、热水器、电风扇、吹风机等各类家用电器
2. 电脑回收：包括台式电脑、笔记本电脑、显示器、键盘、鼠标、打印机、路由器、平板电脑等电脑及配件
3. 旧衣回收：包括各类服装、鞋子、包包、帽子、围巾、床单、窗帘等纺织品
4. 纸箱回收：包括纸箱、快递盒、包装盒、书本、报纸、杂志、纸张等纸制品

分类标准：
- 优先考虑物品的主要功能和材质
- 电子产品按功能细分为家电回收和电脑回收
- 纺织品统一归为旧衣回收
- 纸制品统一归为纸箱回收
- 如果物品信息不明确，选择最可能的分类

请严格按照JSON格式返回结果，确保回收类型的准确性。"""

    # 用户提示词模板
    USER_PROMPT_TEMPLATE = """请根据以下物品分析信息，判断其所属的回收类型：

物品分析结果：
{analysis_result}

请严格按照以下JSON格式返回分析结果：
{{
    "recycling_type": "回收类型名称"
}}

回收类型必须是以下四种之一：
- 家电回收
- 电脑回收  
- 旧衣回收
- 纸箱回收

注意事项：
- 每个物品只能属于一种回收类型
- 必须选择最合适的分类，不能返回其他类型
- 返回的JSON格式必须严格正确
- 如果信息不够明确，请根据常识进行判断"""

    # 不同物品类别的回收类型映射
    CATEGORY_RECYCLING_MAPPING = {
        # 家电类
        "电视": "家电回收",
        "冰箱": "家电回收", 
        "洗衣机": "家电回收",
        "空调": "家电回收",
        "微波炉": "家电回收",
        "电饭煲": "家电回收",
        "热水器": "家电回收",
        "电风扇": "家电回收",
        "吹风机": "家电回收",
        "烤箱": "家电回收",
        "豆浆机": "家电回收",
        "榨汁机": "家电回收",
        "电磁炉": "家电回收",
        "净化器": "家电回收",
        "加湿器": "家电回收",
        
        # 电脑类
        "电脑": "电脑回收",
        "笔记本": "电脑回收",
        "台式机": "电脑回收",
        "显示器": "电脑回收",
        "键盘": "电脑回收",
        "鼠标": "电脑回收",
        "主机": "电脑回收",
        "打印机": "电脑回收",
        "路由器": "电脑回收",
        "平板": "电脑回收",
        "手机": "电脑回收",  # 智能设备归为电脑回收
        "相机": "电脑回收",
        "摄像头": "电脑回收",
        
        # 服装类
        "衣服": "旧衣回收",
        "裤子": "旧衣回收",
        "裙子": "旧衣回收",
        "外套": "旧衣回收",
        "内衣": "旧衣回收",
        "鞋子": "旧衣回收",
        "靴子": "旧衣回收",
        "包包": "旧衣回收",
        "帽子": "旧衣回收",
        "围巾": "旧衣回收",
        "床单": "旧衣回收",
        "被套": "旧衣回收",
        "窗帘": "旧衣回收",
        "毛巾": "旧衣回收",
        
        # 纸制品类
        "纸箱": "纸箱回收",
        "快递盒": "纸箱回收",
        "包装盒": "纸箱回收",
        "纸盒": "纸箱回收",
        "书本": "纸箱回收",
        "书籍": "纸箱回收",
        "报纸": "纸箱回收",
        "杂志": "纸箱回收",
        "纸张": "纸箱回收",
        "笔记本": "纸箱回收",  # 纸质笔记本
        "卡片": "纸箱回收",
        "文件": "纸箱回收"
    }
    
    # 关键词权重配置
    KEYWORD_WEIGHTS = {
        "家电回收": [
            "电器", "家电", "电源", "插头", "遥控", "制冷", "加热", "清洁"
        ],
        "电脑回收": [
            "数码", "电子", "智能", "屏幕", "处理器", "内存", "硬盘", "软件", "网络"
        ],
        "旧衣回收": [
            "布料", "纤维", "棉", "丝", "毛", "穿戴", "时尚", "款式", "尺寸"
        ],
        "纸箱回收": [
            "纸质", "印刷", "书写", "阅读", "包装", "储存", "文档", "资料"
        ]
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
    def get_fallback_recycling_type(cls, analysis_result: Dict[str, Any]) -> str:
        """获取基于规则的备用回收类型判断
        
        Args:
            analysis_result: 物品分析结果
            
        Returns:
            推断的回收类型
        """
        category = analysis_result.get("category", "").lower()
        description = analysis_result.get("description", "").lower()
        combined_text = f"{category} {description}".lower()
        
        # 计算每种回收类型的匹配分数
        type_scores = {}
        
        for recycling_type in ["家电回收", "电脑回收", "旧衣回收", "纸箱回收"]:
            score = 0
            
            # 检查直接映射关键词
            for keyword, mapped_type in cls.CATEGORY_RECYCLING_MAPPING.items():
                if mapped_type == recycling_type and keyword in combined_text:
                    score += 10  # 直接匹配得高分
            
            # 检查权重关键词
            if recycling_type in cls.KEYWORD_WEIGHTS:
                for keyword in cls.KEYWORD_WEIGHTS[recycling_type]:
                    if keyword in combined_text:
                        score += 1
            
            type_scores[recycling_type] = score
        
        # 返回得分最高的类型
        best_type = max(type_scores, key=type_scores.get)
        
        # 如果所有类型得分都为0，返回默认类型
        if type_scores[best_type] == 0:
            return "家电回收"  # 默认类型
        
        return best_type

    @classmethod
    def validate_recycling_type(cls, recycling_type: str) -> bool:
        """验证回收类型是否有效
        
        Args:
            recycling_type: 待验证的回收类型
            
        Returns:
            是否为有效的回收类型
        """
        valid_types = ["家电回收", "电脑回收", "旧衣回收", "纸箱回收"]
        return recycling_type in valid_types

    @classmethod
    def get_recycling_type_description(cls, recycling_type: str) -> str:
        """获取回收类型的描述信息
        
        Args:
            recycling_type: 回收类型
            
        Returns:
            回收类型的描述信息
        """
        descriptions = {
            "家电回收": "家用电器及相关设备的专业回收处理",
            "电脑回收": "电脑、数码设备及电子配件的环保回收",
            "旧衣回收": "服装、纺织品及配饰的公益回收利用",
            "纸箱回收": "纸制品、包装材料及书籍的循环回收"
        }
        return descriptions.get(recycling_type, "未知回收类型")

    @classmethod
    def get_search_keywords(cls, recycling_type: str) -> List[str]:
        """获取回收类型对应的搜索关键词
        
        Args:
            recycling_type: 回收类型
            
        Returns:
            搜索关键词列表
        """
        keywords_map = {
            "家电回收": ["家电回收", "电器回收", "废旧家电", "家电处理"],
            "电脑回收": ["电脑回收", "数码回收", "电子产品回收", "IT设备回收"],
            "旧衣回收": ["旧衣回收", "服装回收", "衣物捐赠", "纺织品回收"],
            "纸箱回收": ["纸箱回收", "废纸回收", "纸制品回收", "包装回收"]
        }
        return keywords_map.get(recycling_type, [recycling_type]) 