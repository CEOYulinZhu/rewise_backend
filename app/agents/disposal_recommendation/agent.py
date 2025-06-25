"""
三大处置路径推荐Agent

智能分析闲置物品的最佳处置方案，基于蓝心大模型分析，
为用户提供创意改造、回收捐赠、二手交易三大路径的推荐度和理由标签
"""

import json
import httpx
import uuid
from typing import Dict, Any, Optional
from urllib.parse import urlencode, urlparse

from app.core.config import settings
from app.core.logger import app_logger
from app.services.llm.lanxin_service import LanxinService
from app.utils.vivo_auth import gen_sign_headers
from app.prompts.disposal_recommendation_prompts import DisposalRecommendationPrompts


class DisposalRecommendationAgent:
    """三大处置路径推荐Agent - 智能处置方案分析"""
    
    def __init__(self):
        self.lanxin_service = LanxinService()
        
        # 蓝心大模型API配置
        self.app_id = settings.lanxin_app_id
        self.app_key = settings.lanxin_app_key
        self.base_url = settings.lanxin_api_base_url
        self.text_model = settings.lanxin_text_model
        
        self.client = httpx.AsyncClient(timeout=30.0)
    
    def _get_auth_headers(self, method: str, uri: str, query_params: Dict[str, str]) -> Dict[str, str]:
        """获取鉴权头部"""
        auth_headers = gen_sign_headers(
            app_id=self.app_id,
            app_key=self.app_key,
            method=method,
            uri=uri,
            query=query_params
        )
        auth_headers["Content-Type"] = "application/json"
        return auth_headers
    
    async def _call_lanxin_api(self, system_prompt: str, user_prompt: str) -> Dict[str, Any]:
        """调用蓝心大模型API"""
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
                "systemPrompt": system_prompt,
                "prompt": user_prompt,
                "extra": {
                    "temperature": 0.2,  # 较低的温度确保更稳定的输出
                    "top_p": 0.8,
                    "max_new_tokens": 1000
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
                raise Exception(f"API调用失败: {result.get('msg', '未知错误')}")
            
            return result["data"]
            
        except Exception as e:
            app_logger.error(f"蓝心大模型API调用失败: {e}")
            raise
    
    def _parse_recommendation_response(self, content: str) -> Optional[Dict[str, Any]]:
        """解析推荐结果响应"""
        try:
            # 尝试直接解析JSON
            try:
                recommendation_result = json.loads(content)
                app_logger.info("推荐结果解析成功 - 直接JSON解析")
                return recommendation_result
            except json.JSONDecodeError:
                pass
            
            # 尝试从代码块中提取JSON
            if "```json" in content:
                start_marker = "```json"
                end_marker = "```"
                start_index = content.find(start_marker)
                if start_index != -1:
                    start_index += len(start_marker)
                    end_index = content.find(end_marker, start_index)
                    if end_index != -1:
                        json_str = content[start_index:end_index].strip()
                        recommendation_result = json.loads(json_str)
                        app_logger.info("推荐结果解析成功 - 代码块JSON解析")
                        return recommendation_result
            
            # 尝试查找花括号内容
            first_brace = content.find('{')
            last_brace = content.rfind('}')
            if first_brace != -1 and last_brace != -1 and first_brace < last_brace:
                json_str = content[first_brace:last_brace + 1]
                recommendation_result = json.loads(json_str)
                app_logger.info("推荐结果解析成功 - 花括号内容解析")
                return recommendation_result
            
            app_logger.warning("无法解析推荐结果为有效JSON格式")
            return None
            
        except Exception as e:
            app_logger.error(f"解析推荐结果失败: {e}")
            return None
    
    def _validate_recommendation_result(self, result: Dict[str, Any]) -> bool:
        """验证推荐结果格式"""
        required_keys = ["creative_renovation", "recycling_donation", "secondhand_trading"]
        
        for key in required_keys:
            if key not in result:
                return False
            
            section = result[key]
            if not isinstance(section, dict):
                return False
            
            if "recommendation_score" not in section or "reason_tags" not in section:
                return False
            
            # 检查分数范围
            score = section.get("recommendation_score")
            if not isinstance(score, (int, float)) or score < 0 or score > 100:
                return False
            
            # 检查标签
            tags = section.get("reason_tags")
            if not isinstance(tags, list) or len(tags) == 0:
                return False
        
        return True
    
    async def recommend_from_image(self, image_path: str) -> Dict[str, Any]:
        """从图片分析获取处置路径推荐
        
        Args:
            image_path: 图片文件路径
            
        Returns:
            包含三大处置路径推荐的字典
        """
        try:
            app_logger.info(f"开始从图片分析处置路径推荐: {image_path}")
            
            # 1. 图片分析
            app_logger.info("步骤1: 分析图片内容")
            analysis_result = await self.lanxin_service.analyze_image(image_path)
            
            if not analysis_result or analysis_result.get("category") == "错误":
                return {
                    "success": False,
                    "error": "图片分析失败",
                    "source": "image_analysis"
                }
            
            # 2. 处置路径推荐
            app_logger.info("步骤2: 使用蓝心大模型分析处置路径推荐")
            recommendation_result = await self._get_disposal_recommendations(analysis_result)
            
            if not recommendation_result.get("success"):
                # 使用备用推荐逻辑
                app_logger.warning("大模型推荐失败，使用备用推荐逻辑")
                fallback_result = DisposalRecommendationPrompts.get_fallback_recommendations(
                    category=analysis_result.get("category", "未知"),
                    condition=analysis_result.get("condition", "八成新")
                )
                recommendation_result = {
                    "success": True,
                    "recommendations": fallback_result,
                    "source": "fallback"
                }
            
            app_logger.info("处置路径推荐分析完成")
            return {
                "success": True,
                "source": "image",
                "image_path": image_path,
                "analysis_result": analysis_result,
                "recommendations": recommendation_result["recommendations"],
                "recommendation_source": recommendation_result.get("source", "ai_model")
            }
            
        except Exception as e:
            app_logger.error(f"从图片分析处置路径推荐失败: {e}")
            return {
                "success": False,
                "error": str(e),
                "source": "image",
                "image_path": image_path
            }
    
    async def recommend_from_text(self, text_description: str) -> Dict[str, Any]:
        """从文字描述获取处置路径推荐
        
        Args:
            text_description: 物品的文字描述
            
        Returns:
            包含三大处置路径推荐的字典
        """
        try:
            app_logger.info(f"开始从文字描述分析处置路径推荐: {text_description[:50]}...")
            
            # 1. 文字分析
            app_logger.info("步骤1: 分析文字内容")
            analysis_result = await self.lanxin_service.analyze_text(text_description)
            
            if not analysis_result:
                return {
                    "success": False,
                    "error": "文字分析失败",
                    "source": "text_analysis"
                }
            
            # 2. 处置路径推荐
            app_logger.info("步骤2: 使用蓝心大模型分析处置路径推荐")
            recommendation_result = await self._get_disposal_recommendations(analysis_result)
            
            if not recommendation_result.get("success"):
                # 使用备用推荐逻辑
                app_logger.warning("大模型推荐失败，使用备用推荐逻辑")
                fallback_result = DisposalRecommendationPrompts.get_fallback_recommendations(
                    category=analysis_result.get("category", "未知"),
                    condition=analysis_result.get("condition", "八成新")
                )
                recommendation_result = {
                    "success": True,
                    "recommendations": fallback_result,
                    "source": "fallback"
                }
            
            app_logger.info("处置路径推荐分析完成")
            return {
                "success": True,
                "source": "text",
                "original_text": text_description,
                "analysis_result": analysis_result,
                "recommendations": recommendation_result["recommendations"],
                "recommendation_source": recommendation_result.get("source", "ai_model")
            }
            
        except Exception as e:
            app_logger.error(f"从文字描述分析处置路径推荐失败: {e}")
            return {
                "success": False,
                "error": str(e),
                "source": "text",
                "original_text": text_description
            }
    
    async def recommend_from_analysis(self, analysis_result: Dict[str, Any]) -> Dict[str, Any]:
        """从已有的分析结果获取处置路径推荐
        
        Args:
            analysis_result: 物品分析结果
            
        Returns:
            包含三大处置路径推荐的字典
        """
        try:
            app_logger.info("开始从分析结果生成处置路径推荐")
            
            # 处置路径推荐
            recommendation_result = await self._get_disposal_recommendations(analysis_result)
            
            if not recommendation_result.get("success"):
                # 使用备用推荐逻辑
                app_logger.warning("大模型推荐失败，使用备用推荐逻辑")
                fallback_result = DisposalRecommendationPrompts.get_fallback_recommendations(
                    category=analysis_result.get("category", "未知"),
                    condition=analysis_result.get("condition", "八成新")
                )
                recommendation_result = {
                    "success": True,
                    "recommendations": fallback_result,
                    "source": "fallback"
                }
            
            app_logger.info("处置路径推荐分析完成")
            return {
                "success": True,
                "source": "analysis_result",
                "analysis_result": analysis_result,
                "recommendations": recommendation_result["recommendations"],
                "recommendation_source": recommendation_result.get("source", "ai_model")
            }
            
        except Exception as e:
            app_logger.error(f"从分析结果生成处置路径推荐失败: {e}")
            return {
                "success": False,
                "error": str(e),
                "source": "analysis_result"
            }
    
    async def _get_disposal_recommendations(self, analysis_result: Dict[str, Any]) -> Dict[str, Any]:
        """获取处置路径推荐"""
        try:
            # 构建提示词
            system_prompt = DisposalRecommendationPrompts.get_system_prompt()
            user_prompt = DisposalRecommendationPrompts.get_user_prompt(analysis_result)
            
            app_logger.info("调用蓝心大模型进行处置路径推荐分析")
            
            # 调用API
            response_data = await self._call_lanxin_api(system_prompt, user_prompt)
            content = response_data.get("content", "")
            
            # 解析推荐结果
            recommendations = self._parse_recommendation_response(content)
            
            if recommendations and self._validate_recommendation_result(recommendations):
                app_logger.info("大模型推荐结果解析成功")
                return {
                    "success": True,
                    "recommendations": recommendations,
                    "source": "ai_model",
                    "raw_response": content
                }
            else:
                app_logger.warning("大模型推荐结果格式无效")
                return {
                    "success": False,
                    "error": "推荐结果格式无效",
                    "raw_response": content
                }
                
        except Exception as e:
            app_logger.error(f"获取处置路径推荐失败: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def close(self):
        """关闭Agent相关资源"""
        try:
            await self.client.aclose()
            await self.lanxin_service.__aexit__(None, None, None)
        except Exception as e:
            app_logger.warning(f"关闭Agent资源时出现警告: {e}")
    
    async def __aenter__(self):
        """异步上下文管理器入口"""
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """异步上下文管理器出口"""
 