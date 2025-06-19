"""
Bilibili搜索Agent

智能B站视频搜索代理，使用蓝心大模型的Function Calling功能，
直接接收图片/文字描述，内部完成分析和关键词提取，最终搜索相关教程视频
"""

import json
import httpx
import uuid
from typing import Dict, Any, List, Optional
from urllib.parse import urlencode, urlparse

from app.core.config import settings
from app.core.logger import app_logger
from app.services.llm.lanxin_service import LanxinService
from app.services.crawler.bilibili.video_search import BilibiliVideoSearchService
from app.utils.vivo_auth import gen_sign_headers
from app.prompts.bilibili_search_prompts import BilibiliSearchPrompts


class BilibiliSearchAgent:
    """Bilibili搜索Agent - 端到端搜索解决方案"""
    
    def __init__(self):
        self.lanxin_service = LanxinService()
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
        analysis_result: Dict[str, Any],
        source_type: str = "image"
    ) -> Dict[str, Any]:
        """使用Function Calling提取搜索关键词"""
        try:
            # 构建消息
            system_prompt = BilibiliSearchPrompts.get_system_prompt()
            
            if source_type == "image":
                user_prompt = BilibiliSearchPrompts.get_user_prompt_for_image_analysis(analysis_result)
            else:
                user_prompt = BilibiliSearchPrompts.get_user_prompt_for_text_analysis(analysis_result)
            
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
            
            app_logger.info(f"开始使用Function Calling提取关键词，来源: {source_type}")
            
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
    
    async def search_from_image(
        self,
        image_path: str,
        max_videos: int = 5
    ) -> Dict[str, Any]:
        """从图片文件搜索相关DIY教程视频（完整流程）
        
        Args:
            image_path: 图片文件路径
            max_videos: 返回的最大视频数量
            
        Returns:
            包含搜索结果的字典
        """
        try:
            app_logger.info(f"开始从图片搜索DIY教程视频: {image_path}")
            
            # 1. 图片分析
            app_logger.info("步骤1: 分析图片内容")
            analysis_result = await self.lanxin_service.analyze_image(image_path)
            
            if not analysis_result or analysis_result.get("category") == "错误":
                return {
                    "success": False,
                    "error": "图片分析失败",
                    "source": "image_analysis"
                }
            
            # 2. 关键词提取
            app_logger.info("步骤2: 使用Function Calling提取搜索关键词")
            extraction_result = await self._extract_keywords_with_function_calling(
                analysis_result=analysis_result,
                source_type="image"
            )
            
            # 3. 获取关键词
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
            
            # 4. 搜索B站视频
            app_logger.info(f"步骤3: 使用关键词搜索B站视频: {keywords}")
            search_query = " ".join(keywords)
            search_result = await self.bilibili_service.search_videos(
                keyword=search_query,
                page=1,
                page_size=max_videos
            )
            
            if search_result.get("error"):
                raise Exception(f"B站搜索失败: {search_result['error']}")
            
            # 5. 格式化结果
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
                "source": "image",
                "image_path": image_path,
                "analysis_result": analysis_result,
                "keywords": keywords,
                "search_intent": search_intent,
                "videos": videos,
                "total": search_result.get("total", 0),
                "function_call_result": extraction_result
            }
            
        except Exception as e:
            app_logger.error(f"从图片搜索视频失败: {e}")
            return {
                "success": False,
                "error": str(e),
                "source": "image",
                "image_path": image_path
            }
    
    async def search_from_text(
        self,
        text_description: str,
        max_videos: int = 5
    ) -> Dict[str, Any]:
        """从文字描述搜索相关DIY教程视频（完整流程）
        
        Args:
            text_description: 物品的文字描述
            max_videos: 返回的最大视频数量
            
        Returns:
            包含搜索结果的字典
        """
        try:
            app_logger.info(f"开始从文字描述搜索DIY教程视频: {text_description[:50]}...")
            
            # 1. 文字分析
            app_logger.info("步骤1: 分析文字内容")
            analysis_result = await self.lanxin_service.analyze_text(text_description)
            
            if not analysis_result:
                return {
                    "success": False,
                    "error": "文字分析失败",
                    "source": "text_analysis"
                }
            
            # 2. 关键词提取
            app_logger.info("步骤2: 使用Function Calling提取搜索关键词")
            extraction_result = await self._extract_keywords_with_function_calling(
                analysis_result=analysis_result,
                source_type="text"
            )
            
            # 3. 获取关键词
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
            
            # 4. 搜索B站视频
            app_logger.info(f"步骤3: 使用关键词搜索B站视频: {keywords}")
            search_query = " ".join(keywords)
            search_result = await self.bilibili_service.search_videos(
                keyword=search_query,
                page=1,
                page_size=max_videos
            )
            
            if search_result.get("error"):
                raise Exception(f"B站搜索失败: {search_result['error']}")
            
            # 5. 格式化结果
            videos = []
            for video in search_result.get("videos", []):
                videos.append({
                    "title": video.title,
                    "uploader": video.uploader_name,
                    "url": video.video_url,
                    "cover_url": video.cover_url,
                    "danmaku_count": video.danmaku_count,
                    "play_count": video.play_count,
                    "duration": video.duration,
                    "description": video.description[:100] + "..." if len(video.description) > 100 else video.description
                })
            
            app_logger.info(f"搜索完成，找到 {len(videos)} 个相关视频")
            return {
                "success": True,
                "source": "text",
                "original_text": text_description,
                "analysis_result": analysis_result,
                "keywords": keywords,
                "search_intent": search_intent,
                "videos": videos,
                "total": search_result.get("total", 0),
                "function_call_result": extraction_result
            }
            
        except Exception as e:
            app_logger.error(f"从文字描述搜索视频失败: {e}")
            return {
                "success": False,
                "error": str(e),
                "source": "text",
                "original_text": text_description
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
        await self.close() 