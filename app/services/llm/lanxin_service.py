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
from app.prompts.llm_prompts import LLMPrompts


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
                "systemPrompt": LLMPrompts.get_text_analysis_system_prompt(),
                "prompt": LLMPrompts.get_text_analysis_prompt(text_description),
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
    

    

    
    async def analyze_image(self, image_input: str) -> Dict[str, Any]:
        """分析图片中的物品（使用蓝心视觉大模型）
        
        Args:
            image_input: 图片输入，可以是本地文件路径或data URI格式的base64数据
        """
        
        app_logger.info("开始分析图片内容")
        
        try:
            import base64
            from pathlib import Path
            
            # 判断输入类型并获取base64数据
            if image_input.startswith("data:"):
                # data URI格式 (data:image/jpeg;base64,...)
                app_logger.info("检测到data URI格式图片")
                if ',' not in image_input:
                    raise ValueError("无效的data URI格式")
                
                header, image_data = image_input.split(',', 1)
                
                # 验证是否为base64格式
                if ';base64' not in header:
                    raise ValueError("data URI必须是base64编码格式")
                
                # image_data已经是base64编码的字符串
                app_logger.info("从data URI提取base64数据成功")
                
            else:
                # 本地文件路径
                app_logger.info("检测到本地文件路径")
                
                # 检查图片文件是否存在
                if not Path(image_input).exists():
                    raise FileNotFoundError(f"图片文件不存在: {image_input}")
                
                # 读取并编码图片
                with open(image_input, "rb") as image_file:
                    image_data = base64.b64encode(image_file.read()).decode('utf-8')
                
                app_logger.info("从本地文件读取并编码图片成功")
            
            # 生成请求ID和会话ID
            request_id = str(uuid.uuid4())
            session_id = str(uuid.uuid4())
            
            # 构造请求参数
            url_params = {"requestId": request_id}
            
            # 获取图像分析提示词
            prompt = LLMPrompts.get_image_analysis_prompt()
            
            # 构造请求体 - 按照参考代码的格式
            request_body = {
                "model": "BlueLM-Vision-prd",  # 使用视觉模型
                "sessionId": session_id,
                "requestId": request_id,
                "messages": [
                    {
                        "role": "user",
                        "content": f"data:image/JPEG;base64,{image_data}",
                        "contentType": "image"
                    },
                    {
                        "role": "user",
                        "content": prompt,
                        "contentType": "text"
                    }
                ],
                "extra": {
                    "temperature": 0.1,
                    "top_p": 0.7,
                    "max_tokens": 1000
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
                app_logger.error(f"视觉API调用失败: {result.get('msg', '未知错误')}")
                raise Exception(f"视觉API调用失败: {result.get('msg', '未知错误')}")
            
            # 解析返回的JSON
            content = result["data"]["content"]
            
            # 尝试解析JSON内容
            try:
                # 首先尝试直接解析
                item_info = json.loads(content)
                app_logger.info("图片分析完成，直接解析JSON成功")
            except json.JSONDecodeError:
                # 如果失败，尝试从代码块中提取JSON
                app_logger.info("尝试从代码块中提取JSON")
                try:
                    # 查找 ```json 代码块
                    if "```json" in content:
                        # 提取代码块中的JSON内容
                        start_marker = "```json"
                        end_marker = "```"
                        start_index = content.find(start_marker)
                        if start_index != -1:
                            start_index += len(start_marker)
                            end_index = content.find(end_marker, start_index)
                            if end_index != -1:
                                json_str = content[start_index:end_index].strip()
                                item_info = json.loads(json_str)
                                app_logger.info("图片分析完成，从代码块解析JSON成功")
                            else:
                                raise json.JSONDecodeError("找不到结束标记", content, 0)
                        else:
                            raise json.JSONDecodeError("找不到开始标记", content, 0)
                    else:
                        # 如果没有代码块，尝试查找第一个{和最后一个}之间的内容
                        first_brace = content.find('{')
                        last_brace = content.rfind('}')
                        if first_brace != -1 and last_brace != -1 and first_brace < last_brace:
                            json_str = content[first_brace:last_brace + 1]
                            item_info = json.loads(json_str)
                            app_logger.info("图片分析完成，提取花括号内容解析JSON成功")
                        else:
                            raise json.JSONDecodeError("找不到有效的JSON结构", content, 0)
                    
                except json.JSONDecodeError:
                    # 如果所有解析都失败，使用默认解析
                    app_logger.warning("视觉分析返回内容无法解析为JSON，使用默认解析")
                    item_info = {
                        "category": "未知",
                        "sub_category": "未知",
                        "condition": "未知", 
                        "keywords": [],
                        "description": content,
                        "analysis_result": content  # 保存原始分析结果
                    }
            
            app_logger.info("图片分析完成")
            return item_info
            
        except FileNotFoundError as e:
            app_logger.error(f"图片文件错误: {e}")
            return {
                "category": "错误",
                "sub_category": "文件不存在",
                "condition": "未知",
                "keywords": [],
                "description": f"图片文件不存在: {image_input}"
            }
        except Exception as e:
            app_logger.error(f"图片分析失败: {e}")
            return {
                "category": "未知",
                "sub_category": "未知",
                "condition": "未知",
                "keywords": [],
                "description": f"图片分析失败: {str(e)}"
            }
    

    
    async def __aenter__(self):
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.client.aclose() 