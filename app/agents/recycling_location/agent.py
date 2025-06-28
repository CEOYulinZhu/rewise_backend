"""
回收地点推荐Agent

智能分析闲置物品的回收类型并推荐附近的回收地点，
基于蓝心大模型分析物品类型，调用高德地图API搜索附近回收设施
"""

import json
import httpx
import uuid
from typing import Dict, Any, Optional, List
from urllib.parse import urlencode, urlparse

from app.core.config import get_settings
from app.core.logger import app_logger
from app.utils.vivo_auth import gen_sign_headers
from app.prompts.recycling_location_prompts import RecyclingLocationPrompts
from app.models.recycling_location_models import (
    RecyclingLocationResponse,
    RecyclingLocationDataConverter
)
from app.services.amap_service import amap_service

settings = get_settings()


class RecyclingLocationAgent:
    """回收地点推荐Agent - 智能回收类型分析与地点推荐"""
    
    # 支持的回收类型及对应的搜索关键词
    RECYCLING_TYPES = {
        "家电回收": "家电回收",
        "电脑回收": "电脑回收",
        "旧衣回收": "旧衣回收",
        "纸箱回收": "纸箱回收"
    }
    
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
                    "temperature": 0.1,  # 非常低的温度确保分类结果稳定
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
            app_logger.error(f"蓝心大模型API调用失败: {e}")
            raise
    
    def _parse_recycling_type_response(self, content: str) -> Optional[str]:
        """解析回收类型分析响应"""
        try:
            # 尝试直接解析JSON
            try:
                result = json.loads(content)
                recycling_type = result.get("recycling_type")
                if recycling_type in self.RECYCLING_TYPES:
                    app_logger.info(f"回收类型解析成功: {recycling_type}")
                    return recycling_type
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
                        recycling_type = result.get("recycling_type")
                        if recycling_type in self.RECYCLING_TYPES:
                            app_logger.info(f"回收类型解析成功 - 代码块解析: {recycling_type}")
                            return recycling_type
            
            # 尝试查找花括号内容
            first_brace = content.find('{')
            last_brace = content.rfind('}')
            if first_brace != -1 and last_brace != -1 and first_brace < last_brace:
                json_str = content[first_brace:last_brace + 1]
                result = json.loads(json_str)
                recycling_type = result.get("recycling_type")
                if recycling_type in self.RECYCLING_TYPES:
                    app_logger.info(f"回收类型解析成功 - 花括号内容解析: {recycling_type}")
                    return recycling_type
            
            # 尝试从文本中直接匹配回收类型
            for recycling_type in self.RECYCLING_TYPES.keys():
                if recycling_type in content:
                    app_logger.info(f"回收类型解析成功 - 文本匹配: {recycling_type}")
                    return recycling_type
            
            app_logger.warning("无法解析回收类型，响应内容中未找到有效的回收类型")
            return None
            
        except Exception as e:
            app_logger.error(f"解析回收类型失败: {e}")
            return None
    
    def _get_fallback_recycling_type(self, analysis_result: Dict[str, Any]) -> str:
        """根据分析结果获取备用回收类型判断"""
        category = analysis_result.get("category", "").lower()
        description = analysis_result.get("description", "").lower()
        
        # 基于关键词进行类型判断，添加更多关键词和类别匹配
        
        # 家电回收关键词
        appliance_keywords = ["电视", "冰箱", "洗衣机", "空调", "微波炉", "电饭煲", "热水器", 
                             "电风扇", "吹风机", "烤箱", "豆浆机", "榨汁机", "电磁炉", 
                             "净化器", "加湿器", "家用电器", "家电"]
        
        # 电脑回收关键词  
        computer_keywords = ["电脑", "笔记本", "台式机", "显示器", "键盘", "鼠标", "主机",
                            "打印机", "路由器", "平板", "手机", "相机", "摄像头", "电子产品"]
        
        # 旧衣回收关键词
        clothing_keywords = ["衣服", "裤子", "裙子", "外套", "内衣", "鞋子", "包包", "帽子",
                            "围巾", "床单", "被套", "窗帘", "毛巾", "服装", "羽绒服", 
                            "T恤", "连衣裙", "牛仔裤", "运动鞋", "靴子"]
        
        # 纸箱回收关键词
        paper_keywords = ["纸箱", "快递盒", "包装盒", "纸盒", "纸张", "书本", "报纸", 
                         "杂志", "笔记本", "卡片", "文件", "书籍", "图书"]
        
        # 检查各类关键词
        if (any(keyword in category or keyword in description for keyword in appliance_keywords) or
            "家用电器" in category or "家电" in category):
            return "家电回收"
        elif (any(keyword in category or keyword in description for keyword in computer_keywords) or
              "电子产品" in category):
            return "电脑回收"
        elif (any(keyword in category or keyword in description for keyword in clothing_keywords) or
              "服装" in category or "衣物" in category):
            return "旧衣回收"  
        elif (any(keyword in category or keyword in description for keyword in paper_keywords) or
              "书籍" in category or "纸制品" in category):
            return "纸箱回收"
        else:
            # 默认返回家电回收（最常见的回收类型）
            return "家电回收"
    
    async def _analyze_recycling_type(self, analysis_result: Dict[str, Any]) -> tuple[str, str]:
        """分析回收类型
        
        Returns:
            tuple[str, str]: (回收类型, 来源) - 来源可以是 'ai' 或 'fallback'
        """
        try:
            app_logger.info("开始AI回收类型分析")
            
            # 获取提示词
            system_prompt = RecyclingLocationPrompts.get_system_prompt()
            user_prompt = RecyclingLocationPrompts.get_user_prompt(analysis_result)
            
            # 调用AI模型
            ai_response = await self._call_lanxin_api(system_prompt, user_prompt)
            content = ai_response.get("content", "")
            
            app_logger.debug(f"AI回收类型分析原始响应: {content}")
            
            # 解析响应
            recycling_type = self._parse_recycling_type_response(content)
            
            if recycling_type:
                app_logger.info(f"AI分析成功，回收类型: {recycling_type}")
                return recycling_type, "ai"
            else:
                app_logger.warning("AI分析失败，使用备用判断逻辑")
                fallback_type = self._get_fallback_recycling_type(analysis_result)
                return fallback_type, "fallback"
                
        except Exception as e:
            app_logger.error(f"回收类型分析失败: {e}")
            app_logger.info("使用备用判断逻辑")
            fallback_type = self._get_fallback_recycling_type(analysis_result)
            return fallback_type, "fallback"
    
    async def analyze_and_recommend_locations(
        self,
        analysis_result: Dict[str, Any],
        user_location: str,
        radius: int = 50000,
        max_locations: int = 20
    ) -> RecyclingLocationResponse:
        """分析回收类型并推荐回收地点
        
        Args:
            analysis_result: 物品分析结果，包含category、description等信息
            user_location: 用户位置，格式为"经度,纬度"
            radius: 搜索半径（米），默认50公里
            max_locations: 最大返回地点数量，默认20个
            
        Returns:
            包含回收类型分析和地点推荐的响应对象
        """
        try:
            app_logger.info("开始回收类型分析和地点推荐")
            
            # 验证输入参数（在任何处理之前）
            if not analysis_result or not isinstance(analysis_result, dict):
                return RecyclingLocationDataConverter.create_response(
                    success=False,
                    error="分析结果为空或格式错误"
                )
            
            if not user_location:
                return RecyclingLocationDataConverter.create_response(
                    success=False,
                    error="用户位置不能为空"
                )
            
            # 步骤1: 分析回收类型（只有在所有输入验证通过后才执行）
            recycling_type, source = await self._analyze_recycling_type(analysis_result)
            app_logger.info(f"确定回收类型: {recycling_type} (来源: {source})")
            
            # 步骤2: 搜索回收地点
            search_keyword = self.RECYCLING_TYPES[recycling_type]
            app_logger.info(f"使用关键词搜索回收地点: {search_keyword}")
            
            try:
                recycling_locations = await amap_service.search_by_keyword(
                    location=user_location,
                    keywords=search_keyword,
                    radius=radius,
                    page_size=max_locations,
                    enable_filter=True,  # 启用筛选
                    sort_by_distance=True  # 按距离排序
                )
                
                app_logger.info(f"搜索到{len(recycling_locations)}个回收地点")
                
            except Exception as e:
                app_logger.error(f"搜索回收地点失败: {e}")
                return RecyclingLocationDataConverter.create_response(
                    success=False,
                    error=f"搜索回收地点失败: {str(e)}",
                    recycling_type=recycling_type,
                    analysis_result=analysis_result
                )
            
            # 创建成功响应
            return RecyclingLocationDataConverter.create_response(
                success=True,
                recycling_type=recycling_type,
                locations=recycling_locations,
                analysis_result=analysis_result,
                search_params={
                    "location": user_location,
                    "keyword": search_keyword,
                    "radius": radius,
                    "max_locations": max_locations
                }
            )
            
        except Exception as e:
            app_logger.error(f"回收类型分析和地点推荐失败: {e}")
            return RecyclingLocationDataConverter.create_response(
                success=False,
                error=f"处理失败: {str(e)}",
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
recycling_location_agent = RecyclingLocationAgent()


async def analyze_recycling_type_and_locations(
    analysis_result: Dict[str, Any],
    user_location: str,
    radius: int = 50000,
    max_locations: int = 20
) -> RecyclingLocationResponse:
    """分析回收类型并推荐回收地点的便捷函数
    
    Args:
        analysis_result: 物品分析结果
        user_location: 用户位置，格式为"经度,纬度"
        radius: 搜索半径（米），默认50公里
        max_locations: 最大返回地点数量，默认20个
        
    Returns:
        包含回收类型分析和地点推荐的响应对象
    """
    return await recycling_location_agent.analyze_and_recommend_locations(
        analysis_result=analysis_result,
        user_location=user_location,
        radius=radius,
        max_locations=max_locations
    ) 