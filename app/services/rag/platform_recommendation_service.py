"""
二手交易平台推荐RAG服务

基于内存的检索增强生成服务，专门用于二手交易平台推荐
"""

import json
from typing import List, Dict, Any
from pathlib import Path

from app.core.config import BASE_DIR
from app.core.logger import app_logger
from app.models.platform_recommendation_models import (
    SecondhandPlatformModel,
    RAGSearchRequest,
    RAGSearchResponse,
    ItemAnalysisModel
)


class PlatformRecommendationRAGService:
    """二手交易平台推荐RAG服务"""
    
    def __init__(self):
        """初始化RAG服务"""
        self.data_file_path = BASE_DIR / "data" / "knowledge" / "secondhand_platforms.json"
        self.platforms_data: List[Dict[str, Any]] = []
        
        # 加载平台数据到内存
        self._load_platform_data()
        
        app_logger.info(f"平台推荐RAG服务初始化完成，加载了 {len(self.platforms_data)} 个平台")
    
    def _load_platform_data(self) -> None:
        """从JSON文件加载平台数据到内存"""
        try:
            if not self.data_file_path.exists():
                app_logger.error(f"平台数据文件不存在: {self.data_file_path}")
                self.platforms_data = []
                return
            
            with open(self.data_file_path, 'r', encoding='utf-8') as f:
                self.platforms_data = json.load(f)
            
            app_logger.info(f"成功加载 {len(self.platforms_data)} 个平台数据到内存")
            
        except Exception as e:
            app_logger.error(f"加载平台数据失败: {e}")
            self.platforms_data = []
    
    def _build_document_text(self, platform: Dict[str, Any]) -> str:
        """构建用于向量化的文档文本"""
        text_parts = [
            f"平台名称: {platform['platform_name']}",
            f"平台描述: {platform['description']}",
            f"主要品类: {', '.join(platform['focus_categories'])}",
            f"平台特色: {', '.join(platform['tags'])}",
            f"交易模式: {platform['transaction_model']}"
        ]
        
        # 添加用户数据信息
        user_data = platform.get('user_data', {})
        if user_data.get('registered_users'):
            text_parts.append(f"注册用户: {user_data['registered_users']}")
        if user_data.get('monthly_active_users'):
            text_parts.append(f"月活用户: {user_data['monthly_active_users']}")
        
        # 添加评分信息
        rating = platform.get('rating', {})
        rating_info = []
        if rating.get('app_store'):
            rating_info.append(f"App Store: {rating['app_store']}")
        if rating.get('yingyongbao'):
            rating_info.append(f"应用宝: {rating['yingyongbao']}")
        if rating.get('kuan'):
            rating_info.append(f"酷安: {rating['kuan']}")
        
        if rating_info:
            text_parts.append(f"用户评分: {', '.join(rating_info)}")
        
        return " | ".join(text_parts)
    
    async def search_platforms(self, request: RAGSearchRequest) -> RAGSearchResponse:
        """根据物品分析结果搜索相关平台"""
        try:
            item_analysis = request.item_analysis
            app_logger.info(f"开始平台搜索: 类别={item_analysis.category}, 子类别={item_analysis.sub_category}")
            
            return await self._search_by_analysis(request)
            
        except Exception as e:
            app_logger.error(f"平台搜索失败: {e}")
            raise
    
    async def _search_by_analysis(self, request: RAGSearchRequest) -> RAGSearchResponse:
        """基于物品分析结果的搜索"""
        item_analysis = request.item_analysis
        search_results = []
        
        app_logger.info(f"分析搜索: 类别={item_analysis.category}, 关键词={item_analysis.keywords}, 阈值={request.similarity_threshold}")
        
        for platform in self.platforms_data:
            # 计算匹配度
            score = self._calculate_platform_match(item_analysis, platform)
            
            app_logger.debug(f"平台 '{platform['platform_name']}' 得分: {score:.3f}")
            
            if score >= request.similarity_threshold:
                result_item = {
                    "platform_name": platform["platform_name"],
                    "document": self._build_document_text(platform),
                    "similarity": score,
                    "metadata": {
                        "platform_name": platform["platform_name"],
                        "description": platform["description"],
                        "focus_categories": platform["focus_categories"],
                        "tags": platform["tags"],
                        "transaction_model": platform["transaction_model"]
                    },
                    "raw_platform_data": platform
                }
                search_results.append(result_item)
                app_logger.info(f"匹配平台: {platform['platform_name']} (得分: {score:.3f})")
        
        # 按相似度排序
        search_results.sort(key=lambda x: x["similarity"], reverse=True)
        
        # 限制结果数量
        search_results = search_results[:request.max_results]
        
        response = RAGSearchResponse(
            results=search_results,
            search_metadata={
                "item_category": item_analysis.category,
                "item_sub_category": item_analysis.sub_category,
                "keywords": item_analysis.keywords,
                "total_results": len(search_results),
                "similarity_threshold": request.similarity_threshold,
                "max_results": request.max_results,
                "search_mode": "analysis_based"
            }
        )
        
        app_logger.info(f"分析搜索完成，返回 {len(search_results)} 个结果")
        return response
    
    def _calculate_platform_match(self, item_analysis: ItemAnalysisModel, platform: Dict[str, Any]) -> float:
        """计算物品与平台的匹配度"""
        score = 0.0
        
        # 1. 类别匹配 (权重: 40%)
        category_score = self._calculate_category_match(item_analysis, platform)
        score += category_score * 0.4
        
        # 2. 关键词匹配 (权重: 30%)
        keyword_score = self._calculate_keyword_match(item_analysis, platform)
        score += keyword_score * 0.3
        
        # 3. 品牌匹配 (权重: 20%)
        brand_score = self._calculate_brand_match(item_analysis, platform)
        score += brand_score * 0.2
        
        # 4. 特殊特性匹配 (权重: 10%)
        feature_score = self._calculate_feature_match(item_analysis, platform)
        score += feature_score * 0.1
        
        app_logger.debug(f"平台 {platform.get('platform_name')} 匹配详情: "
                        f"类别={category_score:.2f}, 关键词={keyword_score:.2f}, "
                        f"品牌={brand_score:.2f}, 特性={feature_score:.2f}, 总分={score:.2f}")
        
        return min(score, 1.0)
    
    def _calculate_category_match(self, item_analysis: ItemAnalysisModel, platform: Dict[str, Any]) -> float:
        """计算类别匹配度"""
        platform_categories = [cat.lower() for cat in platform.get('focus_categories', [])]
        item_category = item_analysis.category.lower()
        item_sub_category = (item_analysis.sub_category or "").lower()
        
        # 精确匹配
        if item_category in platform_categories or item_sub_category in platform_categories:
            return 1.0
        
        # 电子产品匹配
        if item_category in ['电子产品', '数码产品', '电子设备']:
            if any(cat in platform_categories for cat in ['电子产品', '3c数码', '数码', '手机', '电脑']):
                return 0.9
        
        # 手机特殊匹配
        if item_sub_category in ['手机', '智能手机']:
            if any(cat in platform_categories for cat in ['手机', '电子产品', '3c数码']):
                return 0.9
        
        # 图书匹配
        if item_category in ['图书', '书籍']:
            if any(cat in platform_categories for cat in ['图书', '古旧书', '二手书籍']):
                return 1.0
        
        # 全品类平台基础分
        if '全品类' in platform_categories:
            return 0.5
        
        return 0.0
    
    def _calculate_keyword_match(self, item_analysis: ItemAnalysisModel, platform: Dict[str, Any]) -> float:
        """计算关键词匹配度"""
        if not item_analysis.keywords:
            return 0.0
        
        platform_text = self._build_document_text(platform).lower()
        item_keywords = [kw.lower() for kw in item_analysis.keywords]
        
        matched_keywords = []
        for keyword in item_keywords:
            if keyword in platform_text:
                matched_keywords.append(keyword)
        
        return len(matched_keywords) / len(item_keywords) if item_keywords else 0.0
    
    def _calculate_brand_match(self, item_analysis: ItemAnalysisModel, platform: Dict[str, Any]) -> float:
        """计算品牌匹配度"""
        if not item_analysis.brand:
            return 0.5  # 无品牌信息时给中等分
        
        brand = item_analysis.brand.lower()
        platform_text = self._build_document_text(platform).lower()
        
        # 检查平台是否提及特定品牌
        if brand in platform_text:
            return 1.0
        
        # 苹果产品特殊处理
        if brand in ['苹果', 'apple']:
            platform_tags = [tag.lower() for tag in platform.get('tags', [])]
            if any('苹果' in tag or 'apple' in tag for tag in platform_tags):
                return 1.0
        
        return 0.5  # 默认分数
    
    def _calculate_feature_match(self, item_analysis: ItemAnalysisModel, platform: Dict[str, Any]) -> float:
        """计算特殊特性匹配度"""
        platform_tags = [tag.lower() for tag in platform.get('tags', [])]
        
        # 根据物品状况匹配平台特性
        condition = (item_analysis.condition or "").lower()
        if condition in ['全新', '未拆封']:
            if any('官方' in tag or '认证' in tag for tag in platform_tags):
                return 1.0
        
        # 根据特殊功能匹配
        special_features = (item_analysis.special_features or "").lower()
        if '认证' in special_features or '保修' in special_features:
            if any('认证' in tag or '质检' in tag for tag in platform_tags):
                return 1.0
        
        return 0.5  # 默认分数
    
    def get_all_platforms(self) -> List[SecondhandPlatformModel]:
        """获取所有平台数据"""
        try:
            platforms = []
            for platform_data in self.platforms_data:
                platform = SecondhandPlatformModel(**platform_data)
                platforms.append(platform)
            return platforms
        except Exception as e:
            app_logger.error(f"获取所有平台数据失败: {e}")
            return [] 