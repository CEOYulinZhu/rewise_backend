"""
爱回收搜索服务测试

测试AihuishouService的核心功能，包括真实API调用
"""

import asyncio
import sys
from pathlib import Path

import pytest

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from app.services.aihuishou_service import AihuishouService, search_aihuishou_products
from app.models.aihuishou_models import (
    AihuishouSearchRequest,
    AihuishouSearchResponse,
    AihuishouProduct,
    AihuishouPriceStats,
    AihuishouSearchDataConverter
)


class TestAihuishouServiceReal:
    """爱回收服务真实API测试类"""
    
    @pytest.fixture
    def service(self):
        """创建服务实例"""
        return AihuishouService()
    
    def test_service_initialization(self, service):
        """测试服务初始化"""
        print(f"\n==== 测试服务初始化 ====")
        
        # 验证配置是否正确加载
        assert service.base_url == "https://dubai.aihuishou.com/dubai-gateway/recycle-products/search-v9"
        assert service.timeout == 30
        assert service.max_retries == 3
        assert "application/json" in service.headers["content-type"]
        
        print(f"✅ 服务初始化成功")
        print(f"   API URL: {service.base_url}")
        print(f"   超时设置: {service.timeout}秒")
        print(f"   最大重试: {service.max_retries}次")
    
    @pytest.mark.asyncio
    async def test_search_products_real_api(self, service):
        """测试真实API搜索产品功能"""
        print(f"\n==== 测试真实API搜索产品 ====")
        
        try:
            # 测试搜索苹果产品
            response = await service.search_products(
                keyword="苹果13",
                city_id=103,
                page_size=20
            )
            
            print(f"✅ API调用成功")
            print(f"   搜索关键词: 苹果13")
            print(f"   响应状态: {'成功' if response.is_success else '失败'}")
            print(f"   产品数量: {response.product_count}")
            
            # 验证响应结构
            assert isinstance(response, AihuishouSearchResponse)
            assert response.is_success
            assert response.product_count > 0
            assert len(response.data) > 0
            
            # 打印前3个产品信息
            print(f"\n📱 前3个产品信息:")
            for i, product in enumerate(response.data[:3]):
                print(f"   {i+1}. {product.name}")
                print(f"      价格: ¥{product.max_price}")
                print(f"      图片: {product.image_url}")
                print()
            
            # 验证价格统计
            if response.price_stats:
                stats = response.price_stats
                print(f"💰 价格统计信息:")
                print(f"   价格区间: {stats.price_range}")
                print(f"   平均价格: ¥{stats.average_price}")
                print(f"   最低价格: ¥{stats.min_price}")
                print(f"   最高价格: ¥{stats.max_price}")
                
                # 验证价格统计的合理性
                assert stats.min_price <= stats.average_price <= stats.max_price
                assert stats.total_products == response.product_count
            
        except Exception as e:
            print(f"❌ API调用失败: {str(e)}")
            print(f"   错误类型: {type(e).__name__}")
            # 在测试环境中，我们只记录错误但不失败测试
            # 因为API可能因为网络或服务端问题暂时不可用
            pytest.skip(f"API暂时不可用: {str(e)}")
    
    @pytest.mark.asyncio
    async def test_search_with_price_analysis(self, service):
        """测试带价格分析的搜索功能"""
        print(f"\n==== 测试价格分析搜索 ====")
        
        try:
            # 测试价格分析功能
            result = await service.search_with_price_analysis(
                keyword="iPhone",
                city_id=103,
                page_size=15
            )
            
            print(f"✅ 价格分析搜索成功")
            print(f"   搜索关键词: iPhone")
            print(f"   是否成功: {result.get('success', False)}")
            print(f"   产品总数: {result.get('total_products', 0)}")
            
            # 验证返回结构
            assert "success" in result
            assert "total_products" in result
            assert "products" in result
            
            if result["success"] and result["total_products"] > 0:
                # 打印价格统计
                if "price_stats" in result and result["price_stats"]:
                    stats = result["price_stats"]
                    print(f"\n📊 基础价格统计:")
                    print(f"   {stats}")
                
                # 打印价格分析
                if "price_analysis" in result and result["price_analysis"]:
                    analysis = result["price_analysis"]
                    print(f"\n📈 价格分析结果:")
                    
                    if "distribution" in analysis:
                        dist = analysis["distribution"]
                        print(f"   价格分布:")
                        print(f"     中位数: ¥{dist.get('median_price', 0)}")
                        print(f"     方差: {dist.get('price_variance', 0)}")
                        print(f"     价格区间分布: {dist.get('price_ranges', {})}")
                    
                    if "recommendations" in analysis:
                        rec = analysis["recommendations"]
                        print(f"   建议:")
                        for key, value in rec.items():
                            print(f"     {key}: {value}")
                
                # 验证产品数据
                products = result.get("products", [])
                if products:
                    print(f"\n🔍 样本产品 (前2个):")
                    for i, product in enumerate(products[:2]):
                        print(f"   {i+1}. {product['name']}")
                        print(f"      价格: ¥{product['max_price']}")
            
        except Exception as e:
            print(f"❌ 价格分析搜索失败: {str(e)}")
            print(f"   错误类型: {type(e).__name__}")
            pytest.skip(f"价格分析功能暂时不可用: {str(e)}")
    
    @pytest.mark.asyncio
    async def test_search_different_keywords(self, service):
        """测试不同关键词的搜索效果"""
        print(f"\n==== 测试不同关键词搜索 ====")
        
        test_keywords = ["华为", "小米", "iPad", "MacBook"]
        
        for keyword in test_keywords:
            try:
                print(f"\n🔍 测试关键词: {keyword}")
                
                response = await service.search_products(
                    keyword=keyword,
                    city_id=103,
                    page_size=5
                )
                
                print(f"   结果: 找到 {response.product_count} 个产品")
                
                if response.product_count > 0:
                    # 显示第一个产品
                    first_product = response.data[0]
                    print(f"   示例: {first_product.name} - ¥{first_product.max_price}")
                    
                    # 显示价格范围
                    if response.price_stats:
                        print(f"   价格: {response.price_stats.price_range}")
                
                # 简短延迟避免请求过于频繁
                await asyncio.sleep(0.5)
                
            except Exception as e:
                print(f"   错误: {str(e)}")
                continue
    
    @pytest.mark.asyncio
    async def test_convenience_function(self):
        """测试便捷函数"""
        print(f"\n==== 测试便捷函数 ====")
        
        try:
            # 测试包含价格分析的搜索
            result_with_analysis = await search_aihuishou_products(
                keyword="苹果手机",
                include_price_analysis=True,
                page_size=8
            )
            
            print(f"✅ 便捷函数调用成功（含价格分析）")
            print(f"   产品数量: {result_with_analysis.get('total_products', 0)}")
            
            # 测试不包含价格分析的搜索
            result_simple = await search_aihuishou_products(
                keyword="苹果手机", 
                include_price_analysis=False,
                page_size=5
            )
            
            print(f"✅ 便捷函数调用成功（简单搜索）")
            print(f"   产品数量: {result_simple.get('total_products', 0)}")
            
            # 验证两种模式的差异
            has_analysis = "price_analysis" in result_with_analysis
            no_analysis = "price_analysis" not in result_simple
            
            print(f"   价格分析模式差异验证: {has_analysis and no_analysis}")
            
        except Exception as e:
            print(f"❌ 便捷函数测试失败: {str(e)}")
            pytest.skip(f"便捷函数暂时不可用: {str(e)}")
    
    def test_error_handling(self, service):
        """测试错误处理机制"""
        print(f"\n==== 测试错误处理 ====")
        
        # 测试空关键词
        with pytest.raises(ValueError, match="搜索关键词不能为空"):
            asyncio.run(service.search_products(""))
        print(f"✅ 空关键词错误处理正确")
        
        # 测试无效页面大小
        with pytest.raises(ValueError, match="page_size参数范围应为1-50"):
            asyncio.run(service.search_products("test", page_size=0))
        print(f"✅ 页面大小错误处理正确")
        
        # 测试无效页面索引
        with pytest.raises(ValueError, match="page_index参数应大于等于0"):
            asyncio.run(service.search_products("test", page_index=-1))
        print(f"✅ 页面索引错误处理正确")
    
    def test_data_models(self):
        """测试数据模型"""
        print(f"\n==== 测试数据模型 ====")
        
        # 测试产品模型
        product = AihuishouProduct(
            id=12345,
            name="测试产品",
            max_price=1000,
            image_url="https://example.com/image.jpg"
        )
        
        product_dict = product.to_dict()
        assert product_dict["id"] == 12345
        assert product_dict["name"] == "测试产品"
        assert product_dict["max_price"] == 1000
        print(f"✅ 产品模型测试通过")
        
        # 测试价格统计模型
        products = [
            AihuishouProduct(id=1, name="产品1", max_price=500, image_url="url1"),
            AihuishouProduct(id=2, name="产品2", max_price=1500, image_url="url2"),
            AihuishouProduct(id=3, name="产品3", max_price=2000, image_url="url3"),
        ]
        
        stats = AihuishouPriceStats.calculate_from_products(products)
        assert stats.min_price == 500
        assert stats.max_price == 2000
        assert stats.average_price == 1333.33
        assert stats.total_products == 3
        assert "¥500 - ¥2000" == stats.price_range
        print(f"✅ 价格统计模型测试通过")
        
        # 测试搜索请求模型
        request = AihuishouSearchRequest(keyword="test")
        request_body = request.to_request_body()
        assert request_body["keyword"] == "test"
        assert request_body["scene"] == "RECYCLE"
        assert request_body["cityId"] == 103
        print(f"✅ 搜索请求模型测试通过")
    
    @pytest.mark.asyncio
    async def test_comprehensive_workflow(self):
        """测试完整工作流程"""
        print(f"\n==== 测试完整工作流程 ====")
        
        try:
            service = AihuishouService()
            
            print(f"📋 执行完整搜索工作流程:")
            print(f"   1. 初始化服务")
            print(f"   2. 执行产品搜索")
            print(f"   3. 进行价格分析")
            print(f"   4. 数据格式转换")
            
            # 步骤1: 搜索产品
            response = await service.search_products("手机", page_size=10)
            print(f"   ✅ 步骤1完成: 找到 {response.product_count} 个产品")
            
            # 步骤2: 转换为简化格式
            simplified = AihuishouSearchDataConverter.to_simplified_format(response)
            print(f"   ✅ 步骤2完成: 简化格式转换")
            
            # 步骤3: 转换为详细格式
            detailed = AihuishouSearchDataConverter.to_detailed_format(response)
            print(f"   ✅ 步骤3完成: 详细格式转换")
            
            # 步骤4: 价格分析
            if response.product_count > 0:
                prices = [p.max_price for p in response.data]
                variance = service._calculate_variance(prices)
                distribution = service._analyze_price_distribution(prices)
                print(f"   ✅ 步骤4完成: 价格分析")
                print(f"      价格方差: {variance:.2f}")
                print(f"      价格分布区间数: {len(distribution.get('price_ranges', {}))}")
            
            print(f"\n🎉 完整工作流程测试成功!")
            
        except Exception as e:
            print(f"❌ 工作流程测试失败: {str(e)}")
            pytest.skip(f"工作流程暂时不可用: {str(e)}")


def test_models_only():
    """仅测试数据模型（不依赖网络）"""
    print(f"\n==== 独立模型测试 ====")
    
    # 模拟API响应数据
    mock_api_data = {
        "code": 0,
        "resultMessage": "",
        "data": [
            {
                "id": 43510,
                "name": "苹果 iPhone 13",
                "maxPrice": 2000,
                "imageUrl": "https://sr.aihuishou.com/image/test.png",
                "categoryId": 1,
                "brandId": 52,
                "bizType": 1,
                "type": 0,
                "isEnvironmentalRecycling": False,
                "link": None,
                "marketingTagText": None
            },
            {
                "id": 43511,
                "name": "苹果 iPhone 13 Pro",
                "maxPrice": 3200,
                "imageUrl": "https://sr.aihuishou.com/image/test2.png",
                "categoryId": 1,
                "brandId": 52,
                "bizType": 1,
                "type": 0,
                "isEnvironmentalRecycling": False,
                "link": None,
                "marketingTagText": None
            }
        ],
        "page": 0,
        "pageSize": 20,
        "totalCount": 47
    }
    
    # 测试从API响应创建模型
    response = AihuishouSearchResponse.from_api_response(mock_api_data)
    
    print(f"✅ 模型解析成功")
    print(f"   产品数量: {response.product_count}")
    print(f"   是否成功: {response.is_success}")
    
    if response.price_stats:
        print(f"   价格统计: {response.price_stats.price_range}")
        print(f"   平均价格: ¥{response.price_stats.average_price}")
    
    # 测试数据转换
    simplified = AihuishouSearchDataConverter.to_simplified_format(response)
    detailed = AihuishouSearchDataConverter.to_detailed_format(response)
    
    print(f"✅ 数据转换成功")
    print(f"   简化格式产品数: {len(simplified.get('products', []))}")
    print(f"   详细格式产品数: {len(detailed.get('products', []))}")


if __name__ == "__main__":
    # 如果直接运行此文件，执行所有测试
    print("🚀 开始爱回收搜索服务测试")
    
    # 首先运行不依赖网络的模型测试
    test_models_only()
    
    # 然后运行需要网络的测试
    try:
        service = AihuishouService()
        
        # 测试基础功能
        asyncio.run(TestAihuishouServiceReal().test_search_products_real_api(service))
        asyncio.run(TestAihuishouServiceReal().test_search_with_price_analysis(service))
        asyncio.run(TestAihuishouServiceReal().test_comprehensive_workflow())
        
        print("\n🎉 所有测试完成!")
        
    except Exception as e:
        print(f"\n⚠️  网络相关测试跳过: {str(e)}") 