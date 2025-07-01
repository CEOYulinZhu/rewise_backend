"""
二手平台搜索Agent

智能二手平台搜索代理，使用蓝心大模型的Function Calling功能，
基于物品分析结果提取搜索关键词并在闲鱼、爱回收等平台搜索相关商品
"""

import json
import httpx
import uuid
import asyncio
from typing import Dict, Any, List, Optional
from urllib.parse import urlencode, urlparse

from app.core.config import settings
from app.core.logger import app_logger
from app.services.xianyu_service import search_xianyu_products
from app.services.aihuishou_service import search_aihuishou_products
from app.utils.vivo_auth import gen_sign_headers
from app.prompts.secondhand_search_prompts import SecondhandSearchPrompts
from app.models.secondhand_search_models import (
    SecondhandSearchKeywords,
    SecondhandSearchResult,
    SecondhandSearchRequest
)


class SecondhandSearchAgent:
    """二手平台搜索Agent - 基于分析结果的智能商品搜索"""
    
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
            system_prompt = SecondhandSearchPrompts.get_system_prompt()
            user_prompt = SecondhandSearchPrompts.get_user_prompt_for_analysis_result(analysis_result)
            
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
            
            app_logger.info("开始使用Function Calling提取二手平台搜索关键词")
            
            # 调用API
            response_data = await self._call_function_calling_api(messages)
            content = response_data.get("content", "")
            
            # 解析Function Call
            function_call = self._parse_function_call_response(content)
            
            if function_call and function_call.get("name") == "extract_secondhand_keywords":
                parameters = function_call.get("parameters", {})
                keywords = parameters.get("keywords", [])
                search_intent = parameters.get("search_intent", "")
                platform_suggestions = parameters.get("platform_suggestions", {})
                
                app_logger.info(f"Function Calling成功提取关键词: {keywords}")
                return {
                    "success": True,
                    "keywords": keywords,
                    "search_intent": search_intent,
                    "platform_suggestions": platform_suggestions,
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
            brand = analysis_result.get("brand", "")
            model = analysis_result.get("model", "")
            condition = analysis_result.get("condition", "")
            
            # 使用提示词模块的备用逻辑
            fallback_result = SecondhandSearchPrompts.get_fallback_keywords_by_category(
                category=category,
                sub_category=sub_category,
                brand=brand,
                model=model,
                condition=condition
            )
            
            # 生成搜索意图
            search_intent = SecondhandSearchPrompts.get_search_intent_by_category(
                category=category,
                sub_category=sub_category
            )
            
            app_logger.info(f"备用逻辑提取的关键词: {fallback_result['keywords']}")
            return {
                "success": True,
                "keywords": fallback_result["keywords"],
                "search_intent": search_intent,
                "platform_suggestions": fallback_result["platform_suggestions"],
                "source": "fallback"
            }
            
        except Exception as e:
            app_logger.error(f"备用关键词提取失败: {e}")
            return {
                "success": True,
                "keywords": ["二手"],
                "search_intent": "寻找相关二手商品信息",
                "platform_suggestions": {
                    "xianyu": ["二手"],
                    "aihuishou": ["回收"]
                },
                "source": "fallback_default"
            }
    
    async def _search_xianyu_platform(
        self, 
        keywords: List[str], 
        max_results: int
    ) -> Optional[Dict[str, Any]]:
        """搜索闲鱼平台"""
        try:
            # 优化关键词
            optimized_keywords = SecondhandSearchPrompts.optimize_keywords_for_platform(
                keywords, "xianyu"
            )
            search_query = " ".join(optimized_keywords)
            
            app_logger.info(f"开始搜索闲鱼平台: {search_query}")
            
            # 调用闲鱼搜索服务
            result = await search_xianyu_products(
                keyword=search_query,
                page_number=1,
                rows_per_page=max_results,
                include_price_analysis=True
            )
            
            app_logger.info(f"闲鱼搜索完成: {result.get('total_products', 0)} 个产品")
            return result
            
        except Exception as e:
            app_logger.error(f"闲鱼平台搜索失败: {e}")
            return {
                "success": False,
                "error": str(e),
                "total_products": 0,
                "products": []
            }
    
    async def _search_aihuishou_platform(
        self, 
        keywords: List[str], 
        max_results: int
    ) -> Optional[Dict[str, Any]]:
        """搜索爱回收平台"""
        try:
            # 优化关键词
            optimized_keywords = SecondhandSearchPrompts.optimize_keywords_for_platform(
                keywords, "aihuishou"
            )
            search_query = " ".join(optimized_keywords)
            
            app_logger.info(f"开始搜索爱回收平台: {search_query}")
            
            # 调用爱回收搜索服务
            result = await search_aihuishou_products(
                keyword=search_query,
                city_id=103,  # 广州
                page_size=max_results,
                include_price_analysis=True
            )
            
            app_logger.info(f"爱回收搜索完成: {result.get('total_products', 0)} 个产品")
            return result
            
        except Exception as e:
            app_logger.error(f"爱回收平台搜索失败: {e}")
            return {
                "success": False,
                "error": str(e),
                "total_products": 0,
                "products": []
            }
    
    async def search_from_analysis(
        self,
        analysis_result: Dict[str, Any],
        max_results_per_platform: int = 10,
        include_xianyu: bool = True,
        include_aihuishou: bool = True
    ) -> Dict[str, Any]:
        """从分析结果搜索二手平台商品
        
        Args:
            analysis_result: 物品分析结果，包含category、condition、description等信息
            max_results_per_platform: 每个平台最大返回结果数
            include_xianyu: 是否包含闲鱼搜索
            include_aihuishou: 是否包含爱回收搜索
            
        Returns:
            包含搜索结果的字典
        """
        try:
            app_logger.info("开始从分析结果搜索二手平台商品")
            
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
                platform_suggestions = extraction_result.get("platform_suggestions", {})
            else:
                # 使用备用逻辑
                app_logger.warning("Function Calling失败，使用备用关键词提取")
                fallback_result = self._extract_keywords_fallback(analysis_result)
                keywords = fallback_result["keywords"]
                search_intent = fallback_result.get("search_intent", "寻找相关二手商品信息")
                platform_suggestions = fallback_result.get("platform_suggestions", {})
                extraction_result = fallback_result
            
            # 创建关键词对象
            keywords_obj = SecondhandSearchKeywords(
                keywords=keywords,
                search_intent=search_intent,
                platform_suggestions=platform_suggestions
            )
            
            # 3. 并行搜索多个平台
            app_logger.info(f"步骤2: 开始并行搜索平台，关键词: {keywords}")
            
            # 准备搜索任务
            search_tasks = []
            
            if include_xianyu:
                xianyu_task = self._search_xianyu_platform(keywords, max_results_per_platform)
                search_tasks.append(("xianyu", xianyu_task))
            
            if include_aihuishou:
                aihuishou_task = self._search_aihuishou_platform(keywords, max_results_per_platform)
                search_tasks.append(("aihuishou", aihuishou_task))
            
            # 并行执行搜索
            search_results = {}
            if search_tasks:
                results = await asyncio.gather(
                    *[task for _, task in search_tasks],
                    return_exceptions=True
                )
                
                for i, (platform, _) in enumerate(search_tasks):
                    result = results[i]
                    if isinstance(result, Exception):
                        app_logger.error(f"{platform}搜索异常: {result}")
                        search_results[platform] = {
                            "success": False,
                            "error": str(result),
                            "total_products": 0,
                            "products": []
                        }
                    else:
                        search_results[platform] = result
            
            # 4. 构建最终结果
            final_result = SecondhandSearchResult.from_platform_results(
                keywords=keywords_obj,
                xianyu_result=search_results.get("xianyu"),
                aihuishou_result=search_results.get("aihuishou")
            )
            
            app_logger.info(
                f"搜索完成，总共找到 {final_result.total_products} 个商品 "
                f"(闲鱼: {len(final_result.xianyu_products)}, "
                f"爱回收: {len(final_result.aihuishou_products)})"
            )
            
            # 5. 转换为字典格式返回
            from app.models.secondhand_search_models import SecondhandSearchDataConverter
            
            return {
                "success": final_result.success,
                "source": "analysis_result",
                "analysis_result": analysis_result,
                "result": SecondhandSearchDataConverter.to_unified_format(final_result),
                "function_call_result": extraction_result
            }
            
        except Exception as e:
            app_logger.error(f"从分析结果搜索二手平台失败: {e}")
            return {
                "success": False,
                "error": str(e),
                "source": "analysis_result"
            }
    
    async def search_with_request(self, request: SecondhandSearchRequest) -> SecondhandSearchResult:
        """使用请求对象进行搜索"""
        result_dict = await self.search_from_analysis(
            analysis_result=request.analysis_result,
            max_results_per_platform=request.max_results_per_platform,
            include_xianyu=request.include_xianyu,
            include_aihuishou=request.include_aihuishou
        )
        
        # 从result字典中提取SecondhandSearchResult
        if result_dict.get("success") and "result" in result_dict:
            # 这里需要从统一格式转换回SecondhandSearchResult
            # 为简化实现，直接返回基础结果
            pass
        
        # 返回基础的失败结果
        return SecondhandSearchResult(
            success=result_dict.get("success", False),
            error_message=result_dict.get("error", "搜索失败")
        )
    
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