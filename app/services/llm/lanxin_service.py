"""
蓝心大模型服务

封装与蓝心大模型API的交互
"""

import json
import httpx
from typing import Dict, Any, Optional, List
from app.core.config import settings
from app.core.logger import app_logger


class LanxinService:
    """蓝心大模型服务类"""
    
    def __init__(self):
        self.api_key = settings.lanxin_api_key
        self.base_url = settings.lanxin_api_base_url
        self.vision_model = settings.lanxin_vision_model
        self.text_model = settings.lanxin_text_model
        
        self.client = httpx.AsyncClient(
            base_url=self.base_url,
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            },
            timeout=30.0
        )
    
    async def analyze_image(self, image_url: str) -> Dict[str, Any]:
        """分析图片中的物品"""
        
        app_logger.info(f"开始分析图片: {image_url}")
        
        try:
            # 构造视觉模型的请求
            messages = [
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": """请仔细分析这张图片中的物品，并以JSON格式返回以下信息：
{
    "category": "物品大类（如：服装、电器、家具、书籍等）",
    "sub_category": "物品细分类",
    "brand": "品牌（如果能识别）",
    "condition": "物品状态（全新/九成新/八成新/七成新/较旧/破损）",
    "material": "主要材质",
    "color": "主要颜色",
    "keywords": ["关键词1", "关键词2", "关键词3"],
    "description": "详细描述",
    "estimated_age": "估计使用年限",
    "special_features": "特殊特征或价值点"
}"""
                        },
                        {
                            "type": "image_url",
                            "image_url": {"url": image_url}
                        }
                    ]
                }
            ]
            
            response = await self.client.post(
                "/chat/completions",
                json={
                    "model": self.vision_model,
                    "messages": messages,
                    "max_tokens": 1000,
                    "temperature": 0.1
                }
            )
            
            response.raise_for_status()
            result = response.json()
            
            # 解析返回的JSON
            content = result["choices"][0]["message"]["content"]
            item_info = json.loads(content)
            
            app_logger.info("图片分析完成")
            return item_info
            
        except Exception as e:
            app_logger.error(f"图片分析失败: {e}")
            # 返回默认值
            return {
                "category": "未知",
                "sub_category": "未知",
                "condition": "未知",
                "keywords": [],
                "description": "无法识别物品信息"
            }
    
    async def analyze_text(self, text_description: str) -> Dict[str, Any]:
        """分析文字描述"""
        
        app_logger.info("开始分析文字描述")
        
        try:
            messages = [
                {
                    "role": "user",
                    "content": f"""请根据以下描述分析物品信息，并以JSON格式返回：
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
                }
            ]
            
            response = await self.client.post(
                "/chat/completions",
                json={
                    "model": self.text_model,
                    "messages": messages,
                    "max_tokens": 800,
                    "temperature": 0.1
                }
            )
            
            response.raise_for_status()
            result = response.json()
            
            content = result["choices"][0]["message"]["content"]
            item_info = json.loads(content)
            
            app_logger.info("文字分析完成")
            return item_info
            
        except Exception as e:
            app_logger.error(f"文字分析失败: {e}")
            return {
                "category": "未知",
                "sub_category": "未知",
                "condition": "未知",
                "keywords": text_description.split()[:3],
                "description": text_description
            }
    
    async def generate_disposal_recommendations(
        self,
        item_info: Dict[str, Any],
        knowledge: Dict[str, Any],
        market_data: Dict[str, Any],
        user_location: Optional[Any] = None
    ) -> Dict[str, Any]:
        """生成处置建议"""
        
        app_logger.info("开始生成处置建议")
        
        try:
            # 构造提示词
            prompt = f"""
作为物品处置专家，请根据以下信息为用户提供最优的处置建议：

物品信息：
{json.dumps(item_info, ensure_ascii=False, indent=2)}

相关知识：
{json.dumps(knowledge, ensure_ascii=False, indent=2)}

市场数据：
{json.dumps(market_data, ensure_ascii=False, indent=2)}

请从以下三个维度评估并给出建议：
1. 创意改造 (creative_makeover)
2. 回收捐赠 (recycling_donation)
3. 二手交易 (second_hand_trade)

返回JSON格式：
{{
    "creative_score": 0-100的评分,
    "creative_reasons": ["原因1", "原因2"],
    "creative_details": {{
        "overview": {{
            "step_count": 步骤数量,
            "estimated_time": "预计时间",
            "difficulty": "难度等级"
        }},
        "steps": [步骤详情],
        "materials_needed": ["所需材料"],
        "final_result": "改造后的效果"
    }},
    "recycling_score": 0-100的评分,
    "recycling_reasons": ["原因1", "原因2"],
    "recycling_details": {{
        "channels": [回收渠道],
        "donation_options": [捐赠选项],
        "environmental_impact": "环保影响"
    }},
    "trade_score": 0-100的评分,
    "trade_reasons": ["原因1", "原因2"],
    "trade_details": {{
        "estimated_price": "预估价格",
        "best_platforms": ["推荐平台"],
        "selling_tips": ["销售建议"]
    }}
}}
"""
            
            messages = [{"role": "user", "content": prompt}]
            
            response = await self.client.post(
                "/chat/completions",
                json={
                    "model": self.text_model,
                    "messages": messages,
                    "max_tokens": 2000,
                    "temperature": 0.3
                }
            )
            
            response.raise_for_status()
            result = response.json()
            
            content = result["choices"][0]["message"]["content"]
            recommendations = json.loads(content)
            
            app_logger.info("处置建议生成完成")
            return recommendations
            
        except Exception as e:
            app_logger.error(f"生成处置建议失败: {e}")
            # 返回默认建议
            return {
                "creative_score": 50,
                "creative_reasons": ["可以尝试改造"],
                "creative_details": {},
                "recycling_score": 70,
                "recycling_reasons": ["环保处理"],
                "recycling_details": {},
                "trade_score": 40,
                "trade_reasons": ["可以尝试出售"],
                "trade_details": {}
            }
    
    async def __aenter__(self):
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.client.aclose() 