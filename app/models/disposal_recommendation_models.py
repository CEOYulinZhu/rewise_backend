"""
三大处置路径推荐数据模型

定义处置推荐Agent返回的结构化数据模型
"""

from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any


@dataclass
class DisposalPathRecommendation:
    """单个处置路径推荐数据模型"""
    recommendation_score: int           # 推荐度分数（0-100）
    reason_tags: List[str] = field(default_factory=list)  # 推荐理由标签
    
    def __post_init__(self):
        """数据验证"""
        # 验证推荐度范围
        if not (0 <= self.recommendation_score <= 100):
            raise ValueError(f"推荐度分数必须在0-100之间，当前值: {self.recommendation_score}")
        
        # 验证标签数量和长度
        if len(self.reason_tags) > 5:
            raise ValueError(f"推荐标签数量不能超过5个，当前数量: {len(self.reason_tags)}")
        
        for tag in self.reason_tags:
            if len(tag) > 7:
                raise ValueError(f"推荐标签长度不能超过7个字符，当前标签: {tag}")


@dataclass
class OverallRecommendation:
    """总体推荐数据模型"""
    primary_choice: str                 # 首选方案
    reason: str                         # 推荐理由
    
    def __post_init__(self):
        """数据验证"""
        valid_choices = ["创意改造", "回收捐赠", "二手交易"]
        if self.primary_choice not in valid_choices:
            raise ValueError(f"首选方案必须是以下之一: {valid_choices}，当前值: {self.primary_choice}")


@dataclass
class DisposalRecommendations:
    """完整的处置路径推荐数据模型"""
    creative_renovation: DisposalPathRecommendation     # 创意改造推荐
    recycling_donation: DisposalPathRecommendation      # 回收捐赠推荐
    secondhand_trading: DisposalPathRecommendation      # 二手交易推荐
    overall_recommendation: Optional[OverallRecommendation] = None  # 总体推荐
    
    def __post_init__(self):
        """数据验证"""
        # 验证推荐度总和是否合理（允许一定误差）
        total_score = (self.creative_renovation.recommendation_score + 
                      self.recycling_donation.recommendation_score + 
                      self.secondhand_trading.recommendation_score)
        
        # 推荐度总和应该在合理范围内（80-120）
        if not (80 <= total_score <= 120):
            from app.core.logger import app_logger
            app_logger.warning(f"推荐度总和异常: {total_score}，建议检查推荐算法")
    
    def get_sorted_recommendations(self) -> List[tuple]:
        """获取按推荐度排序的推荐列表
        
        Returns:
            排序后的(路径名称, 推荐对象)元组列表
        """
        recommendations = [
            ("创意改造", self.creative_renovation),
            ("回收捐赠", self.recycling_donation),
            ("二手交易", self.secondhand_trading)
        ]
        return sorted(recommendations, key=lambda x: x[1].recommendation_score, reverse=True)
    
    def get_highest_recommendation(self) -> tuple:
        """获取推荐度最高的路径
        
        Returns:
            (路径名称, 推荐对象)元组
        """
        return self.get_sorted_recommendations()[0]
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式（用于JSON序列化）"""
        result = {
            "creative_renovation": {
                "recommendation_score": self.creative_renovation.recommendation_score,
                "reason_tags": self.creative_renovation.reason_tags
            },
            "recycling_donation": {
                "recommendation_score": self.recycling_donation.recommendation_score,
                "reason_tags": self.recycling_donation.reason_tags
            },
            "secondhand_trading": {
                "recommendation_score": self.secondhand_trading.recommendation_score,
                "reason_tags": self.secondhand_trading.reason_tags
            }
        }
        
        if self.overall_recommendation:
            result["overall_recommendation"] = {
                "primary_choice": self.overall_recommendation.primary_choice,
                "reason": self.overall_recommendation.reason
            }
        
        return result


@dataclass
class DisposalRecommendationResponse:
    """处置推荐完整响应数据模型"""
    success: bool                       # 操作是否成功
    source: str                         # 数据来源（如：analysis_result）
    analysis_result: Optional[Dict[str, Any]] = None    # 输入的分析结果
    recommendations: Optional[DisposalRecommendations] = None  # 推荐结果
    recommendation_source: Optional[str] = None         # 推荐来源（ai_model/fallback）
    error: Optional[str] = None         # 错误信息（失败时）
    raw_response: Optional[str] = None  # 原始AI响应（调试用）
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式（用于JSON序列化）"""
        result = {
            "success": self.success,
            "source": self.source,
            "error": self.error
        }
        
        if self.analysis_result:
            result["analysis_result"] = self.analysis_result
        
        if self.recommendations:
            result["recommendations"] = self.recommendations.to_dict()
        
        if self.recommendation_source:
            result["recommendation_source"] = self.recommendation_source
        
        if self.raw_response:
            result["raw_response"] = self.raw_response
        
        return result


class DisposalRecommendationDataConverter:
    """处置推荐数据转换器 - 将原始数据转换为结构化模型"""
    
    @staticmethod
    def convert_from_dict(raw_data: Dict[str, Any]) -> Optional[DisposalRecommendations]:
        """从字典数据转换为推荐模型
        
        Args:
            raw_data: 包含推荐数据的字典
            
        Returns:
            结构化的推荐对象，转换失败时返回None
        """
        try:
            if not raw_data or not isinstance(raw_data, dict):
                return None
            
            # 转换创意改造推荐
            creative_data = raw_data.get("creative_renovation", {})
            creative_renovation = DisposalPathRecommendation(
                recommendation_score=creative_data.get("recommendation_score", 0),
                reason_tags=creative_data.get("reason_tags", [])
            )
            
            # 转换回收捐赠推荐
            recycling_data = raw_data.get("recycling_donation", {})
            recycling_donation = DisposalPathRecommendation(
                recommendation_score=recycling_data.get("recommendation_score", 0),
                reason_tags=recycling_data.get("reason_tags", [])
            )
            
            # 转换二手交易推荐
            trading_data = raw_data.get("secondhand_trading", {})
            secondhand_trading = DisposalPathRecommendation(
                recommendation_score=trading_data.get("recommendation_score", 0),
                reason_tags=trading_data.get("reason_tags", [])
            )
            
            # 转换总体推荐（可选）
            overall_recommendation = None
            overall_data = raw_data.get("overall_recommendation")
            if overall_data and isinstance(overall_data, dict):
                overall_recommendation = OverallRecommendation(
                    primary_choice=overall_data.get("primary_choice", ""),
                    reason=overall_data.get("reason", "")
                )
            
            return DisposalRecommendations(
                creative_renovation=creative_renovation,
                recycling_donation=recycling_donation,
                secondhand_trading=secondhand_trading,
                overall_recommendation=overall_recommendation
            )
            
        except Exception as e:
            from app.core.logger import app_logger
            app_logger.error(f"转换处置推荐数据失败: {e}")
            return None
    
    @staticmethod
    def create_response(
        success: bool,
        source: str,
        analysis_result: Optional[Dict[str, Any]] = None,
        recommendations_dict: Optional[Dict[str, Any]] = None,
        recommendation_source: Optional[str] = None,
        error: Optional[str] = None,
        raw_response: Optional[str] = None
    ) -> DisposalRecommendationResponse:
        """创建响应对象
        
        Args:
            success: 是否成功
            source: 数据来源
            analysis_result: 分析结果
            recommendations_dict: 推荐结果字典
            recommendation_source: 推荐来源
            error: 错误信息
            raw_response: 原始响应
            
        Returns:
            完整的响应对象
        """
        recommendations = None
        if recommendations_dict:
            recommendations = DisposalRecommendationDataConverter.convert_from_dict(recommendations_dict)
        
        return DisposalRecommendationResponse(
            success=success,
            source=source,
            analysis_result=analysis_result,
            recommendations=recommendations,
            recommendation_source=recommendation_source,
            error=error,
            raw_response=raw_response
        ) 