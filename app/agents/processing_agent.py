"""
物品处置处理Agent

负责协调和编排整个物品处置建议的生成流程
"""

from typing import Optional, Dict, Any
from app.services.llm.lanxin_service import LanxinService
from app.services.rag.knowledge_service import KnowledgeService
from app.services.crawler.market_crawler import MarketCrawler
from app.core.logger import app_logger


class ProcessingAgent:
    """物品处置处理Agent"""
    
    def __init__(self):
        self.llm_service = LanxinService()
        self.knowledge_service = KnowledgeService()
        self.market_crawler = MarketCrawler()
    
    async def process_item(
        self,
        image_url: Optional[str] = None,
        text_description: Optional[str] = None,
        user_location: Optional[Any] = None
    ) -> Dict[str, Any]:
        """
        处理物品，生成处置建议
        
        Args:
            image_url: 物品图片URL
            text_description: 物品文字描述
            user_location: 用户地理位置
            
        Returns:
            处置建议结果
        """
        
        app_logger.info("开始处理物品处置请求")
        
        try:
            # 步骤1: 物品识别和描述
            item_info = await self._identify_item(image_url, text_description)
            app_logger.info(f"物品识别完成: {item_info.get('category', '未知')}")
            
            # 步骤2: 获取相关知识
            knowledge = await self._get_relevant_knowledge(item_info)
            app_logger.info("相关知识获取完成")
            
            # 步骤3: 市场数据分析
            market_data = await self._analyze_market(item_info)
            app_logger.info("市场数据分析完成")
            
            # 步骤4: 生成处置建议
            recommendations = await self._generate_recommendations(
                item_info, knowledge, market_data, user_location
            )
            app_logger.info("处置建议生成完成")
            
            # 步骤5: 构造最终结果
            result = await self._build_final_result(
                item_info, recommendations, market_data
            )
            
            app_logger.info("物品处置处理完成")
            return result
            
        except Exception as e:
            app_logger.error(f"处理物品时发生错误: {e}")
            raise
    
    async def _identify_item(
        self,
        image_url: Optional[str],
        text_description: Optional[str]
    ) -> Dict[str, Any]:
        """识别物品信息"""
        
        if image_url:
            # 使用图像识别
            return await self.llm_service.analyze_image(image_url)
        elif text_description:
            # 使用文本分析
            return await self.llm_service.analyze_text(text_description)
        else:
            raise ValueError("必须提供图片或文字描述")
    
    async def _get_relevant_knowledge(self, item_info: Dict[str, Any]) -> Dict[str, Any]:
        """获取相关知识"""
        
        # 从知识库搜索相关信息
        category = item_info.get('category', '')
        keywords = item_info.get('keywords', [])
        
        knowledge = await self.knowledge_service.search_knowledge(
            category=category,
            keywords=keywords
        )
        
        return knowledge
    
    async def _analyze_market(self, item_info: Dict[str, Any]) -> Dict[str, Any]:
        """分析市场数据"""
        
        category = item_info.get('category', '')
        brand = item_info.get('brand', '')
        condition = item_info.get('condition', '')
        
        # 爬取各平台的市场数据
        market_data = await self.market_crawler.get_market_analysis(
            category=category,
            brand=brand,
            condition=condition
        )
        
        return market_data
    
    async def _generate_recommendations(
        self,
        item_info: Dict[str, Any],
        knowledge: Dict[str, Any],
        market_data: Dict[str, Any],
        user_location: Optional[Any]
    ) -> Dict[str, Any]:
        """生成处置建议"""
        
        # 使用LLM综合分析生成建议
        recommendations = await self.llm_service.generate_disposal_recommendations(
            item_info=item_info,
            knowledge=knowledge,
            market_data=market_data,
            user_location=user_location
        )
        
        return recommendations
    
    async def _build_final_result(
        self,
        item_info: Dict[str, Any],
        recommendations: Dict[str, Any],
        market_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """构造最终结果"""
        
        # 构造标准化的返回格式
        result = {
            "overview": {
                "creative_makeover": {
                    "recommendation_score": recommendations.get("creative_score", 50),
                    "reason_tags": recommendations.get("creative_reasons", [])
                },
                "recycling_donation": {
                    "recommendation_score": recommendations.get("recycling_score", 50),
                    "reason_tags": recommendations.get("recycling_reasons", [])
                },
                "second_hand_trade": {
                    "recommendation_score": recommendations.get("trade_score", 50),
                    "reason_tags": recommendations.get("trade_reasons", [])
                }
            },
            "details": {
                "creative_makeover": recommendations.get("creative_details", {}),
                "recycling_donation": recommendations.get("recycling_details", {}),
                "second_hand_trade": recommendations.get("trade_details", {}),
                "item_info": item_info,
                "market_analysis": market_data
            }
        }
        
        return result 