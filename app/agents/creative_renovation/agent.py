"""
创意改造步骤Agent

智能分析闲置物品并生成详细的创意改造步骤指导，
基于蓝心大模型分析，为用户提供可行的改造方案和逐步操作指南
"""

import json
import httpx
import uuid
from typing import Dict, Any, Optional
from urllib.parse import urlencode, urlparse

from app.core.config import settings
from app.core.logger import app_logger
from app.services.llm.lanxin_service import LanxinService
from app.services.renovation_summary_service import RenovationSummaryService
from app.utils.vivo_auth import gen_sign_headers
from app.prompts.creative_renovation_prompts import CreativeRenovationPrompts


class CreativeRenovationAgent:
    """创意改造步骤Agent - 智能改造方案生成"""
    
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
                    "temperature": 0.3,  # 适中的温度，确保创意性和稳定性平衡
                    "top_p": 0.8,
                    "max_new_tokens": 1500  # 增加token限制以支持详细步骤
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
    
    def _parse_renovation_response(self, content: str) -> Optional[Dict[str, Any]]:
        """解析改造方案响应"""
        try:
            # 尝试直接解析JSON
            try:
                renovation_plan = json.loads(content)
                app_logger.info("改造方案解析成功 - 直接JSON解析")
                return renovation_plan
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
                        renovation_plan = json.loads(json_str)
                        app_logger.info("改造方案解析成功 - 代码块JSON解析")
                        return renovation_plan
            
            # 尝试查找花括号内容
            first_brace = content.find('{')
            last_brace = content.rfind('}')
            if first_brace != -1 and last_brace != -1 and first_brace < last_brace:
                json_str = content[first_brace:last_brace + 1]
                renovation_plan = json.loads(json_str)
                app_logger.info("改造方案解析成功 - 花括号内容解析")
                return renovation_plan
            
            app_logger.warning("无法解析改造方案为有效JSON格式")
            return None
            
        except Exception as e:
            app_logger.error(f"解析改造方案失败: {e}")
            return None
    
    def _validate_renovation_plan(self, plan: Dict[str, Any]) -> bool:
        """验证改造方案格式"""
        required_keys = [
            "project_title", "project_description", "difficulty_level",
            "estimated_cost_range", "required_skills",
            "safety_warnings", "steps", "final_result"
        ]
        
        # 检查必要字段
        for key in required_keys:
            if key not in plan:
                app_logger.warning(f"改造方案缺少必要字段: {key}")
                return False
        
        # 检查步骤格式
        steps = plan.get("steps", [])
        if not isinstance(steps, list) or len(steps) == 0:
            app_logger.warning("改造方案缺少步骤信息")
            return False
        
        # 检查每个步骤的格式
        for i, step in enumerate(steps):
            if not isinstance(step, dict):
                app_logger.warning(f"步骤{i+1}格式错误")
                return False
            
            step_required = ["step_number", "title", "description", "tools_needed", "materials_needed", "estimated_time_minutes", "difficulty"]
            for key in step_required:
                if key not in step:
                    app_logger.warning(f"步骤{i+1}缺少字段: {key}")
                    return False
        
        return True
    
    async def generate_from_image(self, image_path: str) -> Dict[str, Any]:
        """从图片分析生成创意改造步骤
        
        Args:
            image_path: 图片文件路径
            
        Returns:
            包含详细改造步骤的字典
        """
        try:
            app_logger.info(f"开始从图片生成创意改造步骤: {image_path}")
            
            # 1. 图片分析
            app_logger.info("步骤1: 分析图片内容")
            analysis_result = await self.lanxin_service.analyze_image(image_path)
            
            if not analysis_result or analysis_result.get("category") == "错误":
                return {
                    "success": False,
                    "error": "图片分析失败",
                    "source": "image_analysis"
                }
            
            # 2. 生成改造步骤
            app_logger.info("步骤2: 使用蓝心大模型生成创意改造步骤")
            renovation_result = await self._generate_renovation_steps(analysis_result)
            
            if not renovation_result.get("success"):
                # 使用备用改造方案
                app_logger.warning("大模型改造方案生成失败，使用备用改造方案")
                fallback_plan = CreativeRenovationPrompts.get_fallback_renovation_plan(
                    category=analysis_result.get("category", "未知"),
                    condition=analysis_result.get("condition", "八成新"),
                    description=analysis_result.get("description", "")
                )
                renovation_result = {
                    "success": True,
                    "renovation_plan": fallback_plan,
                    "source": "fallback"
                }
            
            app_logger.info("创意改造步骤生成完成")
            return {
                "success": True,
                "source": "image",
                "image_path": image_path,
                "analysis_result": analysis_result,
                "renovation_plan": renovation_result["renovation_plan"],
                "generation_source": renovation_result.get("source", "ai_model")
            }
            
        except Exception as e:
            app_logger.error(f"从图片生成创意改造步骤失败: {e}")
            return {
                "success": False,
                "error": str(e),
                "source": "image",
                "image_path": image_path
            }
    
    async def generate_from_text(self, text_description: str) -> Dict[str, Any]:
        """从文字描述生成创意改造步骤
        
        Args:
            text_description: 物品的文字描述
            
        Returns:
            包含详细改造步骤的字典
        """
        try:
            app_logger.info(f"开始从文字描述生成创意改造步骤: {text_description[:50]}...")
            
            # 1. 文字分析
            app_logger.info("步骤1: 分析文字内容")
            analysis_result = await self.lanxin_service.analyze_text(text_description)
            
            if not analysis_result:
                return {
                    "success": False,
                    "error": "文字分析失败",
                    "source": "text_analysis"
                }
            
            # 2. 生成改造步骤
            app_logger.info("步骤2: 使用蓝心大模型生成创意改造步骤")
            renovation_result = await self._generate_renovation_steps(analysis_result)
            
            if not renovation_result.get("success"):
                # 使用备用改造方案
                app_logger.warning("大模型改造方案生成失败，使用备用改造方案")
                fallback_plan = CreativeRenovationPrompts.get_fallback_renovation_plan(
                    category=analysis_result.get("category", "未知"),
                    condition=analysis_result.get("condition", "八成新"),
                    description=analysis_result.get("description", text_description)
                )
                renovation_result = {
                    "success": True,
                    "renovation_plan": fallback_plan,
                    "source": "fallback"
                }
            
            app_logger.info("创意改造步骤生成完成")
            return {
                "success": True,
                "source": "text",
                "original_text": text_description,
                "analysis_result": analysis_result,
                "renovation_plan": renovation_result["renovation_plan"],
                "generation_source": renovation_result.get("source", "ai_model")
            }
            
        except Exception as e:
            app_logger.error(f"从文字描述生成创意改造步骤失败: {e}")
            return {
                "success": False,
                "error": str(e),
                "source": "text",
                "original_text": text_description
            }
    
    async def generate_from_analysis(self, analysis_result: Dict[str, Any]) -> Dict[str, Any]:
        """从已有的分析结果生成创意改造步骤
        
        Args:
            analysis_result: 物品分析结果
            
        Returns:
            包含详细改造步骤的字典
        """
        try:
            app_logger.info("开始从分析结果生成创意改造步骤")
            
            # 生成改造步骤
            renovation_result = await self._generate_renovation_steps(analysis_result)
            
            if not renovation_result.get("success"):
                # 使用备用改造方案
                app_logger.warning("大模型改造方案生成失败，使用备用改造方案")
                fallback_plan = CreativeRenovationPrompts.get_fallback_renovation_plan(
                    category=analysis_result.get("category", "未知"),
                    condition=analysis_result.get("condition", "八成新"),
                    description=analysis_result.get("description", "")
                )
                renovation_result = {
                    "success": True,
                    "renovation_plan": fallback_plan,
                    "source": "fallback"
                }
            
            app_logger.info("创意改造步骤生成完成")
            return {
                "success": True,
                "source": "analysis_result",
                "analysis_result": analysis_result,
                "renovation_plan": renovation_result["renovation_plan"],
                "generation_source": renovation_result.get("source", "ai_model")
            }
            
        except Exception as e:
            app_logger.error(f"从分析结果生成创意改造步骤失败: {e}")
            return {
                "success": False,
                "error": str(e),
                "source": "analysis_result"
            }
    
    async def _generate_renovation_steps(self, analysis_result: Dict[str, Any]) -> Dict[str, Any]:
        """生成改造步骤"""
        try:
            # 构建提示词
            system_prompt = CreativeRenovationPrompts.get_system_prompt()
            user_prompt = CreativeRenovationPrompts.get_user_prompt(analysis_result)
            
            app_logger.info("调用蓝心大模型进行创意改造步骤生成")
            
            # 调用API
            response_data = await self._call_lanxin_api(system_prompt, user_prompt)
            content = response_data.get("content", "")
            
            # 解析改造方案
            renovation_plan = self._parse_renovation_response(content)
            
            if renovation_plan and self._validate_renovation_plan(renovation_plan):
                app_logger.info("大模型改造方案生成成功")
                return {
                    "success": True,
                    "renovation_plan": renovation_plan,
                    "source": "ai_model",
                    "raw_response": content
                }
            else:
                app_logger.warning("大模型改造方案格式无效")
                return {
                    "success": False,
                    "error": "改造方案格式无效",
                    "raw_response": content
                }
                
        except Exception as e:
            app_logger.error(f"生成改造步骤失败: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def get_step_summary(self, renovation_plan: Dict[str, Any]) -> Dict[str, Any]:
        """获取改造步骤摘要信息（使用新的概览服务）"""
        try:
            # 使用新的概览服务
            overview = RenovationSummaryService.extract_overview(renovation_plan)
            
            # 保持原有接口兼容性，同时提供更丰富的信息
            legacy_format = {
                "total_steps": overview.get("steps_summary", {}).get("total_steps", 0),
                "project_title": overview.get("project_title", ""),
                "difficulty_level": overview.get("overall_difficulty", ""),
                "required_tools": overview.get("resources_summary", {}).get("tools_list", []),
                "required_materials": overview.get("resources_summary", {}).get("materials_list", []),
                "required_skills": overview.get("difficulty_analysis", {}).get("skill_requirements", []),
                "safety_warnings_count": overview.get("safety_warnings_count", 0),
                "has_alternative_ideas": overview.get("has_alternative_ideas", False)
            }
            
            # 添加新的详细信息
            legacy_format.update({
                "detailed_overview": overview,
                "total_minutes": overview.get("time_summary", {}).get("total_minutes", 0),
                "total_hours": overview.get("time_summary", {}).get("total_hours", 0),
                "time_range": overview.get("time_summary", {}).get("time_range", "未知"),
                "cost_range": overview.get("cost_summary", {}),
                "beginner_friendly": overview.get("difficulty_analysis", {}).get("beginner_friendly", False),
                "complexity_score": overview.get("difficulty_analysis", {}).get("complexity_score", 0)
            })
            
            return legacy_format
            
        except Exception as e:
            app_logger.error(f"获取改造步骤摘要失败: {e}")
            return {
                "total_steps": 0,
                "project_title": "改造方案摘要获取失败",
                "error": str(e)
            }
    
    def get_detailed_overview(self, renovation_plan: Dict[str, Any]) -> Dict[str, Any]:
        """获取详细的改造方案概览"""
        return RenovationSummaryService.extract_overview(renovation_plan)
    
    def generate_summary_text(self, renovation_plan: Dict[str, Any]) -> str:
        """生成改造方案的文本摘要"""
        overview = RenovationSummaryService.extract_overview(renovation_plan)
        return RenovationSummaryService.generate_summary_text(overview)
    
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