"""
Bilibili搜索Agent

智能B站视频搜索代理，使用蓝心大模型的Function Calling功能，
基于物品分析结果提取搜索关键词并搜索相关教程视频
"""

import json
import httpx
import uuid
from typing import Dict, Any, List, Optional
from urllib.parse import urlencode, urlparse

from app.core.config import settings
from app.core.logger import app_logger
from app.services.crawler.bilibili.video_search import BilibiliVideoSearchService
from app.utils.vivo_auth import gen_sign_headers
from app.prompts.bilibili_search_prompts import BilibiliSearchPrompts


class BilibiliSearchAgent:
    """Bilibili搜索Agent - 基于分析结果的智能视频搜索"""
    
    def __init__(self):
        self.bilibili_service = BilibiliVideoSearchService()
        
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
    
    async def _call_function_calling_api(self, messages: List[Dict[str, Any]]) -> Dict[str, Any]:
        """调用蓝心大模型Function Calling API"""
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
                    "temperature": 0.1,
                    "top_p": 0.7,
                    "max_new_tokens": 500
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
            app_logger.error(f"Function Calling API调用失败: {e}")
            raise
    
    def _parse_function_call_response(self, content: str) -> Optional[Dict[str, Any]]:
        """解析Function Call响应"""
        try:
            # 查找 <APIs> 标签
            if "<APIs>" in content and "</APIs>" in content:
                start_idx = content.find("<APIs>") + len("<APIs>")
                end_idx = content.find("</APIs>")
                apis_content = content[start_idx:end_idx].strip()
                
                # 解析JSON
                function_calls = json.loads(apis_content)
                if isinstance(function_calls, list) and len(function_calls) > 0:
                    return function_calls[0]
                    
            return None
        except Exception as e:
            app_logger.error(f"解析Function Call响应失败: {e}")
            return None
    
    async def _extract_keywords_with_function_calling(
        self, 
        analysis_result: Dict[str, Any]
    ) -> Dict[str, Any]:
        """使用Function Calling提取搜索关键词"""
        try:
            # 构建消息
            system_prompt = BilibiliSearchPrompts.get_system_prompt()
            user_prompt = BilibiliSearchPrompts.get_user_prompt_for_analysis_result(analysis_result)
            
            messages = [
                {
                    "role": "system",
                    "content": system_prompt
                },
                {
                    "role": "user",
                    "content": user_prompt
                }
            ]
            
            app_logger.info("开始使用Function Calling提取关键词")
            
            # 调用API
            response_data = await self._call_function_calling_api(messages)
            content = response_data.get("content", "")
            
            # 解析Function Call
            function_call = self._parse_function_call_response(content)
            
            if function_call and function_call.get("name") == "extract_search_keywords":
                parameters = function_call.get("parameters", {})
                keywords = parameters.get("keywords", [])
                search_intent = parameters.get("search_intent", "")
                
                app_logger.info(f"Function Calling成功提取关键词: {keywords}")
                return {
                    "success": True,
                    "keywords": keywords,
                    "search_intent": search_intent,
                    "source": "function_calling",
                    "raw_response": content
                }
            else:
                app_logger.warning("Function Calling未返回有效的关键词提取结果")
                return {
                    "success": False,
                    "error": "Function Calling未返回有效结果",
                    "raw_response": content
                }
                
        except Exception as e:
            app_logger.error(f"Function Calling提取关键词失败: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def _extract_keywords_fallback(self, analysis_result: Dict[str, Any]) -> Dict[str, Any]:
        """备用关键词提取逻辑"""
        try:
            category = analysis_result.get("category", "")
            sub_category = analysis_result.get("sub_category", "")
            material = analysis_result.get("material", "")
            
            # 使用提示词模块的备用逻辑
            keywords = BilibiliSearchPrompts.get_fallback_keywords_by_category(
                category=category,
                sub_category=sub_category,
                material=material
            )
            
            # 生成搜索意图
            search_intent = BilibiliSearchPrompts.get_search_intent_by_category(
                category=category,
                sub_category=sub_category
            )
            
            app_logger.info(f"备用逻辑提取的关键词: {keywords}")
            return {
                "success": True,
                "keywords": keywords,
                "search_intent": search_intent,
                "source": "fallback"
            }
            
        except Exception as e:
            app_logger.error(f"备用关键词提取失败: {e}")
            return {
                "success": True,
                "keywords": ["DIY", "改造", "手工"],
                "search_intent": "寻找相关DIY教程",
                "source": "fallback_default"
            }
    
    async def search_from_analysis(
        self,
        analysis_result: Dict[str, Any],
        max_videos: int = 5
    ) -> Dict[str, Any]:
        """从分析结果搜索相关DIY教程视频
        
        Args:
            analysis_result: 物品分析结果，包含category、condition、description等信息
            max_videos: 返回的最大视频数量
            
        Returns:
            包含搜索结果的字典
        """
        try:
            app_logger.info("开始从分析结果搜索DIY教程视频")
            
            # 验证分析结果格式
            if not analysis_result or not isinstance(analysis_result, dict):
                return {
                    "success": False,
                    "error": "分析结果为空或格式错误",
                    "source": "analysis_validation"
                }
            
            # 1. 关键词提取
            app_logger.info("步骤1: 使用Function Calling提取搜索关键词")
            extraction_result = await self._extract_keywords_with_function_calling(analysis_result)
            
            # 2. 获取关键词
            if extraction_result.get("success"):
                keywords = extraction_result["keywords"]
                search_intent = extraction_result.get("search_intent", "")
            else:
                # 使用备用逻辑
                app_logger.warning("Function Calling失败，使用备用关键词提取")
                fallback_result = self._extract_keywords_fallback(analysis_result)
                keywords = fallback_result["keywords"]
                search_intent = fallback_result.get("search_intent", "寻找相关DIY教程")
                extraction_result = fallback_result
            
            # 3. 搜索B站视频
            app_logger.info(f"步骤2: 使用关键词搜索B站视频: {keywords}")
            search_query = " ".join(keywords)
            search_result = await self.bilibili_service.search_videos(
                keyword=search_query,
                page=1,
                page_size=max_videos
            )
            
            if search_result.get("error"):
                raise Exception(f"B站搜索失败: {search_result['error']}")
            
            # 4. 格式化结果
            videos = []
            for video in search_result.get("videos", []):
                videos.append({
                    "title": video.title,
                    "uploader": video.uploader_name,
                    "url": video.video_url,
                    "cover_url": video.cover_url,
                    "play_count": video.play_count,
                    "danmaku_count": video.danmaku_count,
                    "duration": video.duration,
                    "description": video.description[:100] + "..." if len(video.description) > 100 else video.description
                })
            
            app_logger.info(f"搜索完成，找到 {len(videos)} 个相关视频")
            return {
                "success": True,
                "source": "analysis_result",
                "analysis_result": analysis_result,
                "keywords": keywords,
                "search_intent": search_intent,
                "videos": videos,
                "total": search_result.get("total", 0),
                "function_call_result": extraction_result
            }
            
        except Exception as e:
            app_logger.error(f"从分析结果搜索视频失败: {e}")
            return {
                "success": False,
                "error": str(e),
                "source": "analysis_result"
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