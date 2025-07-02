"""
平台推荐Agent

根据物品分析结果，调用RAG服务检索相关平台，
然后使用蓝心大模型生成个性化的平台推荐
"""

import json
import uuid
from typing import Dict, Any, Optional, List
from urllib.parse import urlencode, urlparse

import httpx

from app.core.config import settings
from app.core.logger import app_logger
from app.models.platform_recommendation_agent_models import (
    PlatformRecommendationResponse,
    PlatformRecommendationDataConverter
)
from app.models.platform_recommendation_models import ItemAnalysisModel, RAGSearchRequest
from app.prompts.platform_recommendation_prompts import PlatformRecommendationPrompts
from app.services.rag.platform_recommendation_service import PlatformRecommendationRAGService
from app.utils.vivo_auth import gen_sign_headers


class PlatformRecommendationAgent:
    """平台推荐Agent - 智能平台匹配推荐"""
    
    def __init__(self):
        # 蓝心大模型API配置
        self.app_id = settings.lanxin_app_id
        self.app_key = settings.lanxin_app_key
        self.base_url = settings.lanxin_api_base_url
        self.text_model = settings.lanxin_text_model
        
        self.client = httpx.AsyncClient(timeout=30.0)
        
        # RAG服务
        self.rag_service = PlatformRecommendationRAGService()
    
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
                    "temperature": 0.3,  # 稍低的温度确保更稳定的输出
                    "top_p": 0.8,
                    "max_new_tokens": 1500
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
    
    def _parse_ai_response(self, content: str) -> Optional[Dict[str, Any]]:
        """解析AI响应"""
        try:
            # 尝试直接解析JSON
            try:
                result = json.loads(content)
                app_logger.info("AI响应解析成功 - 直接JSON解析")
                return result
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
                        result = json.loads(json_str)
                        app_logger.info("AI响应解析成功 - 代码块JSON解析")
                        return result
            
            # 尝试查找花括号内容
            first_brace = content.find('{')
            last_brace = content.rfind('}')
            if first_brace != -1 and last_brace != -1 and first_brace < last_brace:
                json_str = content[first_brace:last_brace + 1]
                result = json.loads(json_str)
                app_logger.info("AI响应解析成功 - 花括号内容解析")
                return result
            
            app_logger.warning("无法解析AI响应为有效JSON格式")
            return None
            
        except Exception as e:
            app_logger.error(f"解析AI响应失败: {e}")
            return None
    
    def _validate_ai_result(self, result: Dict[str, Any]) -> bool:
        """验证AI结果格式"""
        if not result or "recommendations" not in result:
            return False
        
        recommendations = result["recommendations"]
        if not isinstance(recommendations, list) or len(recommendations) == 0 or len(recommendations) > 3:
            return False
        
        for rec in recommendations:
            if not isinstance(rec, dict):
                return False
            
            required_fields = ["platform_name", "suitability_score", "pros", "cons", "recommendation_reason"]
            for field in required_fields:
                if field not in rec:
                    return False
            
            # 检查分数范围
            score = rec.get("suitability_score")
            if not isinstance(score, (int, float)) or score < 0 or score > 10:
                return False
            
            # 检查优势和劣势
            pros = rec.get("pros", [])
            cons = rec.get("cons", [])
            if not isinstance(pros, list) or not isinstance(cons, list):
                return False
            if len(pros) == 0 or len(pros) > 3 or len(cons) == 0 or len(cons) > 2:
                return False
        
        return True
    
    def _extract_platform_details(self, platform_names: List[str], rag_results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """从RAG结果中提取推荐平台的完整数据"""
        platform_details = []
        
        for platform_name in platform_names:
            for rag_result in rag_results:
                raw_data = rag_result.get("raw_platform_data", {})
                if raw_data.get("platform_name") == platform_name:
                    platform_details.append(raw_data)
                    break
        
        return platform_details
    
    async def recommend_platforms(self, analysis_result: Dict[str, Any]) -> PlatformRecommendationResponse:
        """根据分析结果推荐平台
        
        Args:
            analysis_result: 物品分析结果
            
        Returns:
            平台推荐响应对象
        """
        try:
            app_logger.info("开始平台推荐分析")
            
            # 验证输入
            if not analysis_result or not isinstance(analysis_result, dict):
                return PlatformRecommendationDataConverter.create_response(
                    success=False,
                    error="分析结果为空或格式错误"
                )
            
            # 1. 调用RAG服务检索相关平台
            app_logger.info("调用RAG服务检索相关平台")
            rag_request = RAGSearchRequest(
                item_analysis=ItemAnalysisModel(**analysis_result),
                similarity_threshold=0.3,  # 较低的阈值确保有足够的候选平台
                max_results=5
            )
            
            rag_response = await self.rag_service.search_platforms(rag_request)
            
            if not rag_response.results:
                app_logger.warning("RAG服务未找到相关平台，使用备用推荐")
                fallback_result = PlatformRecommendationPrompts.get_fallback_recommendations(
                    analysis_result.get("category", "未知")
                )
                return PlatformRecommendationDataConverter.create_response(
                    success=True,
                    analysis_result=analysis_result,
                    ai_recommendations=fallback_result,
                    platform_details=[],
                    rag_metadata={"source": "fallback", "total_results": 0}
                )
            
            # 2. 调用AI生成个性化推荐
            app_logger.info(f"基于{len(rag_response.results)}个平台生成AI推荐")
            ai_result = await self._get_ai_recommendations(analysis_result, rag_response.results)
            
            if not ai_result.get("success"):
                app_logger.warning("AI推荐失败，使用备用推荐")
                fallback_result = PlatformRecommendationPrompts.get_fallback_recommendations(
                    analysis_result.get("category", "未知")
                )
                ai_result = {
                    "success": True,
                    "recommendations": fallback_result,
                    "source": "fallback"
                }
            
            # 3. 提取推荐平台的完整数据
            ai_recommendations = ai_result["recommendations"]
            recommended_platforms = [rec["platform_name"] for rec in ai_recommendations["recommendations"]]
            platform_details = self._extract_platform_details(recommended_platforms, rag_response.results)
            
            app_logger.info("平台推荐分析完成")
            return PlatformRecommendationDataConverter.create_response(
                success=True,
                analysis_result=analysis_result,
                ai_recommendations=ai_recommendations,
                platform_details=platform_details,
                rag_metadata={
                    "total_results": len(rag_response.results),
                    "similarity_threshold": rag_request.similarity_threshold,
                    "search_mode": rag_response.search_metadata.get("search_mode", "unknown")
                },
                ai_raw_response=ai_result.get("raw_response")
            )
            
        except Exception as e:
            app_logger.error(f"平台推荐失败: {e}")
            return PlatformRecommendationDataConverter.create_response(
                success=False,
                error=str(e)
            )
    
    async def _get_ai_recommendations(self, analysis_result: Dict[str, Any], rag_results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """获取AI推荐结果"""
        try:
            # 构建提示词
            system_prompt = PlatformRecommendationPrompts.get_system_prompt()
            user_prompt = PlatformRecommendationPrompts.get_user_prompt(analysis_result, rag_results)
            
            app_logger.info("调用蓝心大模型生成平台推荐")
            
            # 调用API
            response_data = await self._call_lanxin_api(system_prompt, user_prompt)
            content = response_data.get("content", "")
            
            # 解析AI响应
            ai_result = self._parse_ai_response(content)
            
            if ai_result and self._validate_ai_result(ai_result):
                app_logger.info("AI推荐结果解析成功")
                return {
                    "success": True,
                    "recommendations": ai_result,
                    "source": "ai_model",
                    "raw_response": content
                }
            else:
                app_logger.warning("AI推荐结果格式无效")
                return {
                    "success": False,
                    "error": "推荐结果格式无效",
                    "raw_response": content
                }
                
        except Exception as e:
            app_logger.error(f"获取AI推荐失败: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def close(self):
        """关闭Agent相关资源"""
        try:
            await self.client.aclose()
        except Exception as e:
            app_logger.warning(f"关闭Agent资源时出现警告: {e}")
    
    async def __aenter__(self):
        """异步上下文管理器入口"""
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """异步上下文管理器出口"""
        await self.close() 