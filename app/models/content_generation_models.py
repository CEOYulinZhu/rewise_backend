"""
文案生成模型

定义文案生成相关的数据结构和响应模型
"""

from typing import Dict, Any, Optional

from pydantic import BaseModel, Field, validator


class ContentGenerationResult(BaseModel):
    """文案生成结果"""
    title: str = Field(..., description="二手交易平台标题")
    description: str = Field(..., description="二手交易平台描述")
    
    @validator('title')
    def validate_title(cls, v):
        """验证标题"""
        if not v or not v.strip():
            raise ValueError("标题不能为空")
        v = v.strip()
        if len(v) > 100:
            raise ValueError("标题长度不能超过100字符")
        return v
    
    @validator('description')
    def validate_description(cls, v):
        """验证描述"""
        if not v or not v.strip():
            raise ValueError("描述不能为空")
        v = v.strip()
        if len(v) > 1000:
            raise ValueError("描述长度不能超过1000字符")
        return v
    
    def to_dict(self) -> Dict[str, str]:
        """转换为字典格式"""
        return {
            "title": self.title,
            "description": self.description
        }


class ContentGenerationResponse(BaseModel):
    """文案生成响应"""
    success: bool = Field(..., description="是否成功")
    source: str = Field(default="content_generation_agent", description="数据来源")
    analysis_result: Optional[Dict[str, Any]] = Field(None, description="原始分析结果")
    content_result: Optional[ContentGenerationResult] = Field(None, description="文案生成结果")
    ai_raw_response: Optional[str] = Field(None, description="AI模型原始响应")
    error: Optional[str] = Field(None, description="错误信息")
    generation_source: str = Field(default="ai", description="生成来源：ai或fallback")
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        result = {
            "success": self.success,
            "source": self.source,
            "generation_source": self.generation_source
        }
        
        if self.analysis_result:
            result["analysis_result"] = self.analysis_result
            
        if self.content_result:
            result["content_result"] = self.content_result.to_dict()
            
        if self.ai_raw_response:
            result["ai_raw_response"] = self.ai_raw_response
            
        if self.error:
            result["error"] = self.error
            
        return result


class ContentGenerationDataConverter:
    """文案生成数据转换器"""
    
    @staticmethod
    def create_response(
        success: bool,
        content_result: Optional[ContentGenerationResult] = None,
        analysis_result: Optional[Dict[str, Any]] = None,
        ai_raw_response: Optional[str] = None,
        error: Optional[str] = None,
        generation_source: str = "ai"
    ) -> ContentGenerationResponse:
        """创建响应对象"""
        return ContentGenerationResponse(
            success=success,
            content_result=content_result,
            analysis_result=analysis_result,
            ai_raw_response=ai_raw_response,
            error=error,
            generation_source=generation_source
        )
    
    @staticmethod
    def create_content_result(title: str, description: str) -> ContentGenerationResult:
        """创建文案生成结果"""
        return ContentGenerationResult(
            title=title,
            description=description
        )
    
    @staticmethod
    def parse_ai_response(content: str) -> Optional[ContentGenerationResult]:
        """解析AI响应内容"""
        import json
        
        try:
            # 尝试直接解析JSON
            try:
                result = json.loads(content)
                title = result.get("title", "").strip()
                description = result.get("description", "").strip()
                
                if title and description:
                    return ContentGenerationResult(title=title, description=description)
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
                        title = result.get("title", "").strip()
                        description = result.get("description", "").strip()
                        
                        if title and description:
                            return ContentGenerationResult(title=title, description=description)
            
            # 尝试查找花括号内容
            first_brace = content.find('{')
            last_brace = content.rfind('}')
            if first_brace != -1 and last_brace != -1 and first_brace < last_brace:
                json_str = content[first_brace:last_brace + 1]
                result = json.loads(json_str)
                title = result.get("title", "").strip()
                description = result.get("description", "").strip()
                
                if title and description:
                    return ContentGenerationResult(title=title, description=description)
            
            return None
            
        except Exception:
            return None 