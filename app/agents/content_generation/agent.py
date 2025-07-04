"""
文案生成Agent

智能分析闲置物品并生成适合二手交易平台的标题和描述文案，
基于蓝心大模型生成吸引人且真实可信的交易文案
"""

import json
import httpx
import uuid
from typing import Dict, Any, Optional
from urllib.parse import urlencode, urlparse

from app.core.config import get_settings
from app.core.logger import app_logger
from app.utils.vivo_auth import gen_sign_headers
from app.prompts.content_generation_prompts import ContentGenerationPrompts
from app.models.content_generation_models import (
    ContentGenerationResponse,
    ContentGenerationResult,
    ContentGenerationDataConverter
)

settings = get_settings()


class ContentGenerationAgent:
    """文案生成Agent - 智能生成二手交易平台文案"""
    
    def __init__(self):
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
                    "temperature": 0.3,  # 适中的温度保证创意和稳定性平衡
                    "top_p": 0.8,
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
                raise Exception(f"API调用失败: {result.get('msg', '未知错误')}")
            
            return result["data"]
            
        except Exception as e:
            app_logger.error(f"蓝心大模型API调用失败: {e}")
            raise
    
    def _parse_content_response(self, content: str) -> Optional[ContentGenerationResult]:
        """解析文案生成响应"""
        try:
            app_logger.debug(f"开始解析AI响应内容: {content[:200]}...")
            
            # 使用数据转换器解析响应
            result = ContentGenerationDataConverter.parse_ai_response(content)
            
            if result:
                app_logger.info(f"文案生成解析成功 - 标题: {result.title[:20]}..., 描述: {result.description[:30]}...")
                return result
            else:
                app_logger.warning("无法解析文案生成响应，响应内容格式不正确")
                return None
                
        except Exception as e:
            app_logger.error(f"解析文案生成响应失败: {e}")
            return None
    
    def _get_fallback_content(self, analysis_result: Dict[str, Any]) -> ContentGenerationResult:
        """获取备用文案内容"""
        try:
            app_logger.info("使用备用文案生成逻辑")
            
            # 使用提示词模块的备用逻辑
            fallback_data = ContentGenerationPrompts.get_fallback_content(analysis_result)
            
            return ContentGenerationDataConverter.create_content_result(
                title=fallback_data["title"],
                description=fallback_data["description"]
            )
            
        except Exception as e:
            app_logger.error(f"备用文案生成失败: {e}")
            # 最后的兜底方案
            category = analysis_result.get("category", "闲置物品")
            condition = analysis_result.get("condition", "九成新")
            
            return ContentGenerationDataConverter.create_content_result(
                title=f"{category} {condition} 诚信出售",
                description=f"出售{category}一件，成色{condition}，诚信交易，支持当面验货，有意请联系。"
            )
    
    async def generate_content(self, analysis_result: Dict[str, Any]) -> ContentGenerationResponse:
        """生成交易文案
        
        Args:
            analysis_result: 物品分析结果，包含category、description等信息
            
        Returns:
            包含标题和描述的文案生成响应对象
        """
        try:
            app_logger.info("开始文案生成")
            
            # 验证输入参数
            if not analysis_result or not isinstance(analysis_result, dict):
                return ContentGenerationDataConverter.create_response(
                    success=False,
                    error="分析结果为空或格式错误",
                    analysis_result=analysis_result
                )
            
            # 步骤1: 尝试AI生成文案
            try:
                app_logger.info("开始AI文案生成")
                
                # 获取提示词
                system_prompt = ContentGenerationPrompts.get_system_prompt()
                user_prompt = ContentGenerationPrompts.get_user_prompt(analysis_result)
                
                # 调用AI模型
                ai_response = await self._call_lanxin_api(system_prompt, user_prompt)
                content = ai_response.get("content", "")
                
                app_logger.debug(f"AI文案生成原始响应: {content}")
                
                # 解析响应
                content_result = self._parse_content_response(content)
                
                if content_result:
                    app_logger.info("AI文案生成成功")
                    return ContentGenerationDataConverter.create_response(
                        success=True,
                        content_result=content_result,
                        analysis_result=analysis_result,
                        ai_raw_response=content,
                        generation_source="ai"
                    )
                else:
                    app_logger.warning("AI文案生成失败，使用备用逻辑")
                    
            except Exception as e:
                app_logger.error(f"AI文案生成异常: {e}")
            
            # 步骤2: 使用备用文案生成
            fallback_result = self._get_fallback_content(analysis_result)
            
            return ContentGenerationDataConverter.create_response(
                success=True,
                content_result=fallback_result,
                analysis_result=analysis_result,
                generation_source="fallback"
            )
            
        except Exception as e:
            app_logger.error(f"文案生成失败: {e}")
            return ContentGenerationDataConverter.create_response(
                success=False,
                error=f"文案生成失败: {str(e)}",
                analysis_result=analysis_result
            )
    
    async def close(self):
        """关闭HTTP客户端"""
        if self.client:
            await self.client.aclose()
    
    async def __aenter__(self):
        """异步上下文管理器入口"""
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """异步上下文管理器退出"""
        await self.close()


# 全局Agent实例
content_generation_agent = ContentGenerationAgent()


async def generate_content_from_analysis(analysis_result: Dict[str, Any]) -> ContentGenerationResponse:
    """从分析结果生成交易文案的便捷函数
    
    Args:
        analysis_result: 物品分析结果
        
    Returns:
        包含标题和描述的文案生成响应对象
    """
    return await content_generation_agent.generate_content(analysis_result) 