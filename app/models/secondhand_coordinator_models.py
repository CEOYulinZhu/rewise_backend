"""
二手交易平台协调器数据模型

定义二手交易协调器的请求、响应和数据转换结构
"""

from typing import Dict, Any, Optional

from pydantic import BaseModel, Field

from app.models.content_generation_models import ContentGenerationResponse


class SecondhandTradingRequest(BaseModel):
    """二手交易协调器请求"""
    analysis_result: Dict[str, Any] = Field(..., description="物品分析结果")
    max_results_per_platform: int = Field(default=10, description="每个平台最大返回结果数")
    include_xianyu: bool = Field(default=True, description="是否包含闲鱼搜索")
    include_aihuishou: bool = Field(default=True, description="是否包含爱回收搜索")
    enable_parallel: bool = Field(default=True, description="是否启用并行处理")


class SecondhandTradingProcessingMetadata(BaseModel):
    """二手交易处理元数据"""
    processing_mode: str = Field(..., description="处理模式：parallel/serial")
    processing_time_seconds: float = Field(..., description="总处理时间（秒）")
    search_success: bool = Field(..., description="搜索是否成功")
    content_success: bool = Field(..., description="文案生成是否成功")
    search_error: Optional[str] = Field(None, description="搜索错误信息")
    content_error: Optional[str] = Field(None, description="文案生成错误信息")


class SecondhandTradingResponse(BaseModel):
    """二手交易协调器响应"""
    success: bool = Field(..., description="协调是否成功")
    source: str = Field(default="secondhand_trading_coordinator", description="数据来源")
    analysis_result: Optional[Dict[str, Any]] = Field(None, description="原始分析结果")
    
    # 搜索结果
    search_result: Optional[Dict[str, Any]] = Field(None, description="平台搜索结果")
    
    # 文案生成结果
    content_result: Optional[ContentGenerationResponse] = Field(None, description="文案生成结果")
    
    # 处理元数据
    processing_metadata: Optional[SecondhandTradingProcessingMetadata] = Field(None, description="处理元数据")
    
    # 错误信息
    error: Optional[str] = Field(None, description="错误信息")
    
    def has_search_results(self) -> bool:
        """检查是否有有效搜索结果"""
        return (self.search_result is not None and 
                self.search_result.get("success", False))
    
    def has_content_results(self) -> bool:
        """检查是否有有效文案结果"""
        return (self.content_result is not None and 
                self.content_result.success)
    
    def get_total_products(self) -> int:
        """获取搜索到的总商品数量"""
        if not self.has_search_results():
            return 0
        
        result = self.search_result.get("result", {})
        return result.get("total_products", 0)
    
    def get_generated_title(self) -> Optional[str]:
        """获取生成的标题"""
        if not self.has_content_results():
            return None
        
        content_result = self.content_result.content_result
        return content_result.title if content_result else None
    
    def get_generated_description(self) -> Optional[str]:
        """获取生成的描述"""
        if not self.has_content_results():
            return None
        
        content_result = self.content_result.content_result
        return content_result.description if content_result else None
    
    def get_processing_summary(self) -> Dict[str, Any]:
        """获取处理摘要信息"""
        if not self.processing_metadata:
            return {}
        
        return {
            "processing_mode": self.processing_metadata.processing_mode,
            "total_time_seconds": self.processing_metadata.processing_time_seconds,
            "search_success": self.processing_metadata.search_success,
            "content_success": self.processing_metadata.content_success,
            "total_products": self.get_total_products(),
            "has_content": self.has_content_results()
        }
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        result = {
            "success": self.success,
            "source": self.source
        }
        
        if self.analysis_result:
            result["analysis_result"] = self.analysis_result
        
        if self.search_result:
            result["search_result"] = self.search_result
        
        if self.content_result:
            result["content_result"] = self.content_result.to_dict()
        
        if self.processing_metadata:
            result["processing_metadata"] = self.processing_metadata.dict()
        
        if self.error:
            result["error"] = self.error
        
        return result


class SecondhandTradingDataConverter:
    """二手交易数据转换器"""
    
    @staticmethod
    def create_response(
        success: bool,
        analysis_result: Optional[Dict[str, Any]] = None,
        search_result: Optional[Dict[str, Any]] = None,
        content_result: Optional[ContentGenerationResponse] = None,
        processing_metadata: Optional[SecondhandTradingProcessingMetadata] = None,
        error: Optional[str] = None
    ) -> SecondhandTradingResponse:
        """创建响应对象"""
        return SecondhandTradingResponse(
            success=success,
            analysis_result=analysis_result,
            search_result=search_result,
            content_result=content_result,
            processing_metadata=processing_metadata,
            error=error
        )
    
    @staticmethod
    def create_processing_metadata(
        processing_mode: str,
        processing_time_seconds: float,
        search_success: bool,
        content_success: bool,
        search_error: Optional[str] = None,
        content_error: Optional[str] = None
    ) -> SecondhandTradingProcessingMetadata:
        """创建处理元数据"""
        return SecondhandTradingProcessingMetadata(
            processing_mode=processing_mode,
            processing_time_seconds=processing_time_seconds,
            search_success=search_success,
            content_success=content_success,
            search_error=search_error,
            content_error=content_error
        )
    
    @staticmethod
    def create_request(
        analysis_result: Dict[str, Any],
        max_results_per_platform: int = 10,
        include_xianyu: bool = True,
        include_aihuishou: bool = True,
        enable_parallel: bool = True
    ) -> SecondhandTradingRequest:
        """创建请求对象"""
        return SecondhandTradingRequest(
            analysis_result=analysis_result,
            max_results_per_platform=max_results_per_platform,
            include_xianyu=include_xianyu,
            include_aihuishou=include_aihuishou,
            enable_parallel=enable_parallel
        ) 