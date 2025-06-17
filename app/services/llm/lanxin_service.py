"""
蓝心大模型服务（VIVO BlueLM）

封装与VIVO BlueLM大模型API的交互
"""

import json
import httpx
import uuid
from typing import Dict, Any, Optional, List
from urllib.parse import urlencode, urlparse
from app.core.config import settings
from app.core.logger import app_logger
from app.utils.vivo_auth import gen_sign_headers


class LanxinService:
    """VIVO BlueLM大模型服务类"""
    
    def __init__(self):
        self.app_id = settings.lanxin_app_id
        self.app_key = settings.lanxin_app_key
        self.base_url = settings.lanxin_api_base_url
        self.text_model = settings.lanxin_text_model
        
        self.client = httpx.AsyncClient(
            timeout=30.0
        )
    
    def _get_auth_headers(self, method: str, uri: str, query_params: Dict[str, str]) -> Dict[str, str]:
        """获取鉴权头部"""
        # 使用正确的VIVO API签名算法
        auth_headers = gen_sign_headers(
            app_id=self.app_id,
            app_key=self.app_key,
            method=method,
            uri=uri,
            query=query_params
        )
        
        # 添加Content-Type
        auth_headers["Content-Type"] = "application/json"
        
        return auth_headers
    
    async def analyze_text(self, text_description: str) -> Dict[str, Any]:
        """分析文字描述"""
        
        app_logger.info("开始分析文字描述")
        
        try:
            # 生成请求ID和会话ID
            request_id = str(uuid.uuid4())
            session_id = str(uuid.uuid4())
            
            # 构造请求参数
            url_params = {"requestId": request_id}
            
            # 构造请求体
            request_body = {
                "model": self.text_model,
                "sessionId": session_id,
                "systemPrompt": "你是一个专业的物品分析专家，擅长根据描述分析物品的详细信息。",
                "prompt": f"""请根据以下描述分析物品信息，并以JSON格式返回：
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
}}""",
                "extra": {
                    "temperature": 0.1,
                    "top_p": 0.7,
                    "max_new_tokens": 800
                }
            }
            
            # 获取鉴权头部
            parsed_url = urlparse(self.base_url)
            uri = parsed_url.path
            headers = self._get_auth_headers("POST", uri, url_params)
            
            # 发送请求
            url = f"{self.base_url}?{urlencode(url_params)}"
            response = await self.client.post(
                url,
                headers=headers,
                json=request_body
            )
            
            response.raise_for_status()
            result = response.json()
            
            # 检查响应状态
            if result.get("code") != 0:
                app_logger.error(f"API调用失败: {result.get('msg', '未知错误')}")
                raise Exception(f"API调用失败: {result.get('msg', '未知错误')}")
            
            # 解析返回的JSON
            content = result["data"]["content"]
            
            # 尝试解析JSON内容
            try:
                item_info = json.loads(content)
            except json.JSONDecodeError:
                # 如果返回的不是标准JSON，尝试提取关键信息
                app_logger.warning("返回内容不是标准JSON格式，使用默认解析")
                item_info = {
                    "category": "未知",
                    "sub_category": "未知",
                    "condition": "未知",
                    "keywords": text_description.split()[:3],
                    "description": content
                }
            
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
            # 生成请求ID和会话ID
            request_id = str(uuid.uuid4())
            session_id = str(uuid.uuid4())
            
            # 构造请求参数
            url_params = {"requestId": request_id}
            
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
            
            # 构造请求体
            request_body = {
                "model": self.text_model,
                "sessionId": session_id,
                "systemPrompt": "你是一个专业的物品处置和环保专家，能够为用户提供科学、实用的物品处置建议。",
                "prompt": prompt,
                "extra": {
                    "temperature": 0.3,
                    "top_p": 0.7,
                    "max_new_tokens": 2000
                }
            }
            
            # 获取鉴权头部
            parsed_url = urlparse(self.base_url)
            uri = parsed_url.path
            headers = self._get_auth_headers("POST", uri, url_params)
            
            # 发送请求
            url = f"{self.base_url}?{urlencode(url_params)}"
            response = await self.client.post(
                url,
                headers=headers,
                json=request_body
            )
            
            response.raise_for_status()
            result = response.json()
            
            # 检查响应状态
            if result.get("code") != 0:
                app_logger.error(f"API调用失败: {result.get('msg', '未知错误')}")
                raise Exception(f"API调用失败: {result.get('msg', '未知错误')}")
            
            content = result["data"]["content"]
            
            # 尝试解析JSON内容
            try:
                recommendations = json.loads(content)
            except json.JSONDecodeError:
                app_logger.warning("返回内容不是标准JSON格式，使用默认建议")
                recommendations = {
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
    
    async def chat_with_text(
        self,
        messages: List[Dict[str, str]],
        system_prompt: Optional[str] = None,
        **kwargs
    ) -> str:
        """通用文本对话接口"""
        
        app_logger.info("开始文本对话")
        
        try:
            # 生成请求ID和会话ID
            request_id = str(uuid.uuid4())
            session_id = str(uuid.uuid4())
            
            # 构造请求参数
            url_params = {"requestId": request_id}
            
            # 构造请求体
            request_body = {
                "model": self.text_model,
                "sessionId": session_id,
                "messages": messages,
                "extra": {
                    "temperature": kwargs.get("temperature", 0.7),
                    "top_p": kwargs.get("top_p", 0.7),
                    "max_new_tokens": kwargs.get("max_tokens", 1000)
                }
            }
            
            if system_prompt:
                request_body["systemPrompt"] = system_prompt
            
            # 获取鉴权头部
            parsed_url = urlparse(self.base_url)
            uri = parsed_url.path
            headers = self._get_auth_headers("POST", uri, url_params)
            
            # 发送请求
            url = f"{self.base_url}?{urlencode(url_params)}"
            response = await self.client.post(
                url,
                headers=headers,
                json=request_body
            )
            
            response.raise_for_status()
            result = response.json()
            
            # 检查响应状态
            if result.get("code") != 0:
                app_logger.error(f"API调用失败: {result.get('msg', '未知错误')}")
                raise Exception(f"API调用失败: {result.get('msg', '未知错误')}")
            
            content = result["data"]["content"]
            app_logger.info("文本对话完成")
            return content
            
        except Exception as e:
            app_logger.error(f"文本对话失败: {e}")
            return "抱歉，我现在无法处理您的请求，请稍后再试。"
    
    # 为了向后兼容，保留原有的analyze_image方法，但标记为不支持
    async def analyze_image(self, image_url: str) -> Dict[str, Any]:
        """分析图片中的物品（当前API不支持视觉功能）"""
        
        app_logger.warning("当前VIVO BlueLM API不支持图片分析功能")
        
        # 返回默认值
        return {
            "category": "未知",
            "sub_category": "未知",
            "condition": "未知",
            "keywords": [],
            "description": "当前API版本不支持图片分析，请使用文字描述"
        }
    
    async def __aenter__(self):
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.client.aclose() 