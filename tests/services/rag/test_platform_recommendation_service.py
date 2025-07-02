"""
测试二手交易平台推荐RAG服务
"""

import asyncio
import json

import pytest

from app.models.platform_recommendation_models import (
    RAGSearchRequest,
    ItemAnalysisModel
)
from app.services.rag.platform_recommendation_service import PlatformRecommendationRAGService


class TestPlatformRecommendationRAGService:
    """测试平台推荐RAG服务"""
    
    @pytest.fixture
    def service(self):
        """创建服务实例"""
        return PlatformRecommendationRAGService()
    
    @pytest.fixture
    def sample_item_analysis(self):
        """示例物品分析结果"""
        return ItemAnalysisModel(
            category="电子产品",
            sub_category="智能手机",
            brand="苹果",
            condition="九成新",
            material="金属和玻璃",
            color="黑色",
            keywords=["iPhone", "智能手机", "黑色", "苹果"],
            description="一台黑色的苹果iPhone手机，九成新。",
            estimated_age="1年",
            special_features="官方认证"
        )
    
    @pytest.fixture
    def sample_search_request(self, sample_item_analysis):
        """示例搜索请求"""
        return RAGSearchRequest(
            item_analysis=sample_item_analysis,
            max_results=5,
            similarity_threshold=0.1
        )
    
    def test_service_initialization(self, service):
        """测试服务初始化"""
        assert service is not None
        assert hasattr(service, 'platforms_data')
        assert len(service.platforms_data) > 0
    
    def test_data_file_exists(self, service):
        """测试数据文件是否存在"""
        assert service.data_file_path.exists(), f"数据文件不存在: {service.data_file_path}"
        
        # 验证JSON格式
        with open(service.data_file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        assert isinstance(data, list), "数据应该是列表格式"
        assert len(data) > 0, "数据不能为空"
        
        # 验证数据结构
        for platform in data:
            assert "platform_name" in platform
            assert "description" in platform
            assert "focus_categories" in platform
            assert "tags" in platform
    
    def test_build_document_text(self, service):
        """测试文档文本构建"""
        platform_data = {
            "platform_name": "测试平台",
            "description": "测试描述",
            "focus_categories": ["电子产品", "数码"],
            "tags": ["认证", "快速"],
            "transaction_model": "C2C",
            "user_data": {
                "registered_users": "100万",
                "monthly_active_users": "50万"
            },
            "rating": {
                "app_store": 4.5,
                "yingyongbao": 4.3
            }
        }
        
        doc_text = service._build_document_text(platform_data)
        
        assert "测试平台" in doc_text
        assert "测试描述" in doc_text
        assert "电子产品" in doc_text
        assert "认证" in doc_text
        assert "C2C" in doc_text
        assert "100万" in doc_text
        assert "4.5" in doc_text
    
    @pytest.mark.asyncio
    async def test_search_platforms(self, service, sample_search_request):
        """测试平台搜索"""
        try:
            response = await service.search_platforms(sample_search_request)
            
            assert response is not None
            assert hasattr(response, 'results')
            assert hasattr(response, 'search_metadata')
            assert response.search_metadata['item_category'] == sample_search_request.item_analysis.category
            
            print(f"\n=== 搜索返回 {len(response.results)} 个结果 ===")
            
            # 详细输出返回数据格式
            print("\n【返回数据结构】:")
            print(f"response.search_metadata = {response.search_metadata}")
            
            for i, result in enumerate(response.results, 1):
                print(f"\n--- 结果 {i}: {result['platform_name']} (匹配度: {result['similarity']:.3f}) ---")
                
                # 显示返回给上层Agent的关键数据
                print("【平台基本信息】:")
                platform_data = result["raw_platform_data"]
                print(f"  平台名称: {platform_data['platform_name']}")
                print(f"  平台图标: {platform_data['platform_icon']}")
                print(f"  平台描述: {platform_data['description']}")
                print(f"  主要类别: {platform_data['focus_categories']}")
                print(f"  特色标签: {platform_data['tags']}")
                print(f"  交易模式: {platform_data['transaction_model']}")
                
                print("【用户数据】:")
                user_data = platform_data.get('user_data', {})
                for key, value in user_data.items():
                    if value:
                        print(f"  {key}: {value}")
                
                print("【评分信息】:")
                rating = platform_data.get('rating', {})
                for key, value in rating.items():
                    if value:
                        print(f"  {key}: {value}")
                
                # 验证结果结构
                assert "platform_name" in result
                assert "similarity" in result
                assert "raw_platform_data" in result
                assert 0 <= result["similarity"] <= 1
                
        except Exception as e:
            print(f"搜索测试失败: {e}")
            raise
    
    def test_get_all_platforms(self, service):
        """测试获取所有平台"""
        platforms = service.get_all_platforms()
        
        assert len(platforms) > 0
        for platform in platforms:
            assert hasattr(platform, 'platform_name')
            assert hasattr(platform, 'description')
            assert hasattr(platform, 'focus_categories')
    
    def test_calculate_platform_match(self, service, sample_item_analysis):
        """测试平台匹配度计算"""
        if len(service.platforms_data) > 0:
            platform = service.platforms_data[0]
            score = service._calculate_platform_match(sample_item_analysis, platform)
            assert 0 <= score <= 1
            print(f"匹配度得分: {score:.3f}")
    
    def test_calculate_category_match(self, service, sample_item_analysis):
        """测试类别匹配度计算"""
        if len(service.platforms_data) > 0:
            platform = service.platforms_data[0]
            score = service._calculate_category_match(sample_item_analysis, platform)
            assert 0 <= score <= 1
            print(f"类别匹配度: {score:.3f}")
    
    @pytest.mark.asyncio
    async def test_different_scenarios(self, service):
        """测试不同场景下的搜索结果"""
        
        print("\n" + "="*60)
        print("【场景1：苹果手机】")
        print("="*60)
        
        iphone_analysis = ItemAnalysisModel(
            category="电子产品",
            sub_category="智能手机",
            brand="苹果",
            condition="九成新",
            material="金属和玻璃",
            color="黑色",
            keywords=["iPhone", "智能手机", "苹果", "手机"],
            description="一台黑色的苹果iPhone手机，九成新。"
        )
        
        request = RAGSearchRequest(
            item_analysis=iphone_analysis,
            max_results=3,
            similarity_threshold=0.1
        )
        
        response = await service.search_platforms(request)
        self._print_search_results("苹果手机", response)
        
        print("\n" + "="*60)
        print("【场景2：古旧书籍】")
        print("="*60)
        
        book_analysis = ItemAnalysisModel(
            category="图书",
            sub_category="古籍",
            brand=None,
            condition="良好",
            material="纸质",
            color=None,
            keywords=["古籍", "书籍", "图书", "文献"],
            description="一本古代文献书籍。"
        )
        
        request = RAGSearchRequest(
            item_analysis=book_analysis,
            max_results=3,
            similarity_threshold=0.1
        )
        
        response = await service.search_platforms(request)
        self._print_search_results("古旧书籍", response)
        
        print("\n" + "="*60)
        print("【场景3：奢侈品包包】")
        print("="*60)
        
        luxury_analysis = ItemAnalysisModel(
            category="奢侈品",
            sub_category="包包",
            brand="LV",
            condition="全新",
            material="皮革",
            color="棕色",
            keywords=["LV", "包包", "奢侈品", "皮包"],
            description="一个棕色的LV皮包，全新未使用。"
        )
        
        request = RAGSearchRequest(
            item_analysis=luxury_analysis,
            max_results=3,
            similarity_threshold=0.1
        )
        
        response = await service.search_platforms(request)
        self._print_search_results("奢侈品包包", response)
    
    def _print_search_results(self, scenario_name: str, response):
        """打印搜索结果"""
        print(f"\n{scenario_name}搜索结果：")
        print(f"匹配到 {len(response.results)} 个平台")
        
        for i, result in enumerate(response.results, 1):
            platform_data = result["raw_platform_data"]
            print(f"\n{i}. {platform_data['platform_name']} (匹配度: {result['similarity']:.3f})")
            print(f"   描述: {platform_data['description']}")
            print(f"   主要类别: {platform_data['focus_categories']}")
            print(f"   特色: {platform_data['tags'][:2]}...")  # 只显示前2个标签
            
            # 重点：这就是返回给上层Agent的完整JSON数据
            print(f"   [返回给Agent的完整数据大小: {len(str(platform_data))} 字符]")
    
    def test_show_complete_json_structure(self, service):
        """展示返回给上层Agent的完整JSON数据结构"""
        platforms = service.get_all_platforms()
        if platforms:
            print("\n" + "="*80)
            print("【完整JSON数据结构示例 - 这就是返回给上层Agent的数据】")
            print("="*80)
            
            # 选择第一个平台作为示例
            first_platform_data = service.platforms_data[0]
            
            print("\n完整的平台数据JSON结构：")
            print("-" * 40)
            import json
            print(json.dumps(first_platform_data, ensure_ascii=False, indent=2))
            print("-" * 40)
            
            print(f"\n数据字段说明：")
            print(f"- platform_icon: 平台图标/emoji")
            print(f"- platform_name: 平台名称")
            print(f"- description: 平台描述")
            print(f"- focus_categories: 主要经营类别")
            print(f"- tags: 平台特色标签")
            print(f"- user_data: 用户统计数据")
            print(f"- rating: 各应用商店评分")
            print(f"- transaction_model: 交易模式")
            
            print(f"\n上层Agent可以使用这些数据进行：")
            print(f"- 智能推荐分析")
            print(f"- 用户友好的展示")
            print(f"- 基于评分的排序")
            print(f"- 基于用户数据的可信度评估")


if __name__ == "__main__":
    # 简单的手动测试
    async def manual_test():
        """手动测试"""
        print("开始手动测试RAG服务...")
        
        try:
            service = PlatformRecommendationRAGService()
            print("✓ 服务初始化成功")
            
            # 测试搜索
            item_analysis = ItemAnalysisModel(
                category="电子产品",
                sub_category="智能手机",
                brand="苹果",
                condition="九成新",
                material="金属和玻璃",
                color="黑色",
                keywords=["iPhone", "智能手机", "苹果"],
                description="一台黑色的苹果iPhone手机，九成新。"
            )
            
            search_request = RAGSearchRequest(
                item_analysis=item_analysis,
                max_results=3,
                similarity_threshold=0.1
            )
            
            search_response = await service.search_platforms(search_request)
            print(f"✓ 搜索成功，返回 {len(search_response.results)} 个结果")
            
            for result in search_response.results:
                print(f"  - {result['platform_name']}: {result['similarity']:.3f}")
            
        except Exception as e:
            print(f"✗ 测试失败: {e}")
    
    # 运行手动测试
    asyncio.run(manual_test()) 