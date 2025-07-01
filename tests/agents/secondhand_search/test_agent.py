"""
二手平台搜索Agent真实测试

测试 SecondhandSearchAgent 的实际搜索功能，包括真实的API调用和平台搜索
"""

import pytest
import asyncio
from app.agents.secondhand_search.agent import SecondhandSearchAgent


class TestSecondhandSearchAgentReal:
    """二手平台搜索Agent测试类"""
    
    @pytest.fixture
    def agent(self):
        """创建测试用的Agent实例"""
        return SecondhandSearchAgent()
    
    @pytest.fixture
    def sample_analysis_results(self):
        """多个示例分析结果用于测试"""
        return [
            {
                "name": "苹果手机测试",
                "analysis_result": {
                    "category": "电子产品",
                    "sub_category": "手机",
                    "brand": "苹果",
                    "model": "iPhone 12",
                    "condition": "95新",
                    "description": "苹果iPhone 12手机，黑色，128GB，功能正常，外观良好",
                    "color": "黑色",
                    "storage": "128GB"
                }
            },
            {
                "name": "小米手机测试",
                "analysis_result": {
                    "category": "电子产品",
                    "sub_category": "手机",
                    "brand": "小米",
                    "model": "小米11",
                    "condition": "9成新",
                    "description": "小米11手机，白色，256GB，使用正常，有轻微磨损",
                    "color": "白色",
                    "storage": "256GB"
                }
            },
            {
                "name": "华为手机测试",
                "analysis_result": {
                    "category": "电子产品",
                    "sub_category": "手机",
                    "brand": "华为",
                    "model": "P40",
                    "condition": "8成新",
                    "description": "华为P40手机，功能正常，外观有使用痕迹",
                    "color": "金色"
                }
            }
        ]

    @pytest.mark.asyncio
    async def test_real_keyword_extraction(self, agent, sample_analysis_results):
        """测试真实的关键词提取功能"""
        print(f"\n🔍 测试真实关键词提取功能")
        print("="*60)
        
        for test_case in sample_analysis_results:
            print(f"\n📱 测试案例: {test_case['name']}")
            print("-" * 40)
            
            analysis_result = test_case["analysis_result"]
            print(f"品牌型号: {analysis_result.get('brand', '')} {analysis_result.get('model', '')}")
            print(f"成色状态: {analysis_result.get('condition', '')}")
            print(f"商品描述: {analysis_result.get('description', '')}")
            
            try:
                # 测试Function Calling关键词提取
                print(f"\n🤖 测试Function Calling关键词提取...")
                fc_result = await agent._extract_keywords_with_function_calling(analysis_result)
                
                if fc_result.get("success"):
                    print(f"✅ Function Calling成功!")
                    print(f"🔗 关键词: {fc_result['keywords']}")
                    print(f"💭 搜索意图: {fc_result['search_intent']}")
                    print(f"📱 闲鱼建议: {fc_result['platform_suggestions'].get('xianyu', [])}")
                    print(f"♻️ 爱回收建议: {fc_result['platform_suggestions'].get('aihuishou', [])}")
                else:
                    print(f"❌ Function Calling失败: {fc_result.get('error')}")
                    
            except Exception as e:
                print(f"❌ Function Calling异常: {e}")
            
            # 测试备用关键词提取
            print(f"\n🛡️ 测试备用关键词提取...")
            try:
                fallback_result = agent._extract_keywords_fallback(analysis_result)
                
                if fallback_result.get("success"):
                    print(f"✅ 备用机制成功!")
                    print(f"🔗 关键词: {fallback_result['keywords']}")
                    print(f"💭 搜索意图: {fallback_result['search_intent']}")
                    print(f"📱 闲鱼建议: {fallback_result['platform_suggestions'].get('xianyu', [])}")
                    print(f"♻️ 爱回收建议: {fallback_result['platform_suggestions'].get('aihuishou', [])}")
                else:
                    print(f"❌ 备用机制失败: {fallback_result.get('error')}")
            except Exception as e:
                print(f"❌ 备用机制异常: {e}")
            
            print("-" * 40)

    @pytest.mark.asyncio
    async def test_real_platform_search(self, agent):
        """测试真实的平台搜索功能"""
        print(f"\n🛒 测试真实平台搜索功能")
        print("="*60)
        
        # 使用多个不同的关键词组合进行测试
        test_keywords_list = [
            ["iPhone", "手机", "二手"],
            ["小米", "手机", "闲置"],
            ["华为", "P40", "回收"]
        ]
        
        for i, test_keywords in enumerate(test_keywords_list, 1):
            print(f"\n🔍 测试组 {i}: {test_keywords}")
            print("-" * 30)
            
            # 测试闲鱼搜索
            print(f"\n🐟 测试闲鱼平台搜索...")
            try:
                xianyu_result = await agent._search_xianyu_platform(test_keywords, 20)
                
                if xianyu_result.get("success"):
                    print(f"✅ 闲鱼搜索成功!")
                    print(f"📊 找到商品: {xianyu_result.get('total_products', 0)} 个")
                    
                    products = xianyu_result.get("products", [])
                    for j, product in enumerate(products[:3], 1):
                        print(f"  {j}. {product.get('title', '无标题')}")
                        print(f"     💰 价格: ¥{product.get('price', 0)}")
                        print(f"     👤 卖家: {product.get('user_nick', '未知')}")
                        print(f"     📍 地区: {product.get('area', '未知')}")
                        if product.get('pic_url'):
                            print(f"     🖼️ 图片: {product['pic_url']}")
                        print()
                        
                    price_stats = xianyu_result.get("price_stats", {})
                    if price_stats:
                        print(f"💰 价格统计: {price_stats.get('price_range', '无数据')}")
                        print(f"📈 平均价格: ¥{price_stats.get('average_price', 0)}")
                else:
                    print(f"❌ 闲鱼搜索失败: {xianyu_result.get('error', '未知错误')}")
                    
            except Exception as e:
                print(f"❌ 闲鱼搜索异常: {e}")
            
            # 测试爱回收搜索
            print(f"\n♻️ 测试爱回收平台搜索...")
            try:
                aihuishou_result = await agent._search_aihuishou_platform(test_keywords, 20)
                
                if aihuishou_result.get("success"):
                    print(f"✅ 爱回收搜索成功!")
                    print(f"📊 找到商品: {aihuishou_result.get('total_products', 0)} 个")
                    
                    products = aihuishou_result.get("products", [])
                    for j, product in enumerate(products[:3], 1):
                        print(f"  {j}. {product.get('name', '无标题')}")
                        print(f"     💰 回收价: ¥{product.get('max_price', 0)}")
                        if product.get('image_url'):
                            print(f"     🖼️ 图片: {product['image_url']}")
                        print()
                        
                    price_stats = aihuishou_result.get("price_stats", {})
                    if price_stats:
                        print(f"💰 价格统计: {price_stats.get('price_range', '无数据')}")
                        print(f"📈 平均回收价: ¥{price_stats.get('average_price', 0)}")
                else:
                    print(f"❌ 爱回收搜索失败: {aihuishou_result.get('error', '未知错误')}")
                    
            except Exception as e:
                print(f"❌ 爱回收搜索异常: {e}")
            
            print("-" * 30)

    @pytest.mark.asyncio
    async def test_real_complete_search_flow(self, agent, sample_analysis_results):
        """测试真实的完整搜索流程"""
        print(f"\n🚀 测试真实完整搜索流程")
        print("="*60)
        
        for test_case in sample_analysis_results:
            print(f"\n📱 测试案例: {test_case['name']}")
            print("-" * 40)
            
            analysis_result = test_case["analysis_result"]
            print(f"品牌型号: {analysis_result.get('brand', '')} {analysis_result.get('model', '')}")
            print(f"成色状态: {analysis_result.get('condition', '')}")
            print(f"商品描述: {analysis_result.get('description', '')}")
            
            try:
                # 执行完整搜索流程
                result = await agent.search_from_analysis(
                    analysis_result=analysis_result,
                    max_results_per_platform=20
                )
                
                if result.get("success"):
                    await self._display_search_results(result, test_case['name'])
                else:
                    print(f"❌ 搜索失败: {result.get('error', '未知错误')}")
                    
            except Exception as e:
                print(f"❌ 搜索异常: {e}")
                import traceback
                traceback.print_exc()
                
            print("-" * 40)

    async def _display_search_results(self, result, test_name):
        """显示详细的搜索结果"""
        search_result = result["result"]
        
        print(f"\n✅ {test_name} 搜索成功!")
        print(f"📊 总商品数量: {search_result['total_products']}")
        
        # 显示关键词信息
        keywords_info = search_result.get('keywords', {})
        print(f"🔍 提取关键词: {keywords_info.get('keywords', [])}")
        print(f"💭 搜索意图: {keywords_info.get('search_intent', '')}")
        
        # 显示Function Call结果
        fc_result = result.get('function_call_result', {})
        fc_source = fc_result.get('source', '未知')
        if fc_result.get('success'):
            print(f"🤖 关键词来源: {fc_source} ✅")
        else:
            print(f"🤖 关键词来源: {fc_source} (备用机制)")
        
        # 闲鱼平台结果
        print(f"\n🐟 闲鱼平台结果:")
        xianyu_stats = search_result['platform_stats']['xianyu']
        if xianyu_stats['success']:
            print(f"  ✅ 找到 {xianyu_stats['product_count']} 个商品")
            
            if xianyu_stats.get('price_stats'):
                price_stats = xianyu_stats['price_stats']
                print(f"  💰 价格区间: {price_stats.get('price_range', '无数据')}")
                print(f"  📈 平均价格: ¥{price_stats.get('average_price', 0)}")
                print(f"  📊 最低价格: ¥{price_stats.get('min_price', 0)}")
                print(f"  📊 最高价格: ¥{price_stats.get('max_price', 0)}")
            
            # 显示商品详情
            xianyu_products = [p for p in search_result['products'] if p.get('platform') == '闲鱼']
            if xianyu_products:
                print(f"  📦 商品详情:")
                for i, product in enumerate(xianyu_products[:3], 1):
                    print(f"    {i}. {product.get('title', '无标题')}")
                    print(f"       💰 价格: ¥{product.get('price', 0)}")
                    print(f"       👤 卖家: {product.get('seller', '未知')}")
                    print(f"       📍 地区: {product.get('location', '未知')}")
                    if product.get('image_url'):
                        print(f"       🖼️ 图片: {product['image_url']}")
                    print()
        else:
            print(f"  ❌ 搜索失败: {xianyu_stats.get('error', '未知错误')}")
        
        # 爱回收平台结果 
        print(f"♻️ 爱回收平台结果:")
        aihuishou_stats = search_result['platform_stats']['aihuishou']
        if aihuishou_stats['success']:
            print(f"  ✅ 找到 {aihuishou_stats['product_count']} 个商品")
            
            if aihuishou_stats.get('price_stats'):
                price_stats = aihuishou_stats['price_stats']
                print(f"  💰 回收价区间: {price_stats.get('price_range', '无数据')}")
                print(f"  📈 平均回收价: ¥{price_stats.get('average_price', 0)}")
                print(f"  📊 最低回收价: ¥{price_stats.get('min_price', 0)}")
                print(f"  📊 最高回收价: ¥{price_stats.get('max_price', 0)}")
            
            # 显示商品详情
            aihuishou_products = [p for p in search_result['products'] if p.get('platform') == '爱回收']
            if aihuishou_products:
                print(f"  📦 回收商品详情:")
                for i, product in enumerate(aihuishou_products[:3], 1):
                    print(f"    {i}. {product.get('title', '无标题')}")
                    print(f"       💰 回收价: ¥{product.get('price', 0)}")
                    print(f"       🏢 平台: {product.get('seller', '爱回收')}")
                    if product.get('image_url'):
                        print(f"       🖼️ 图片: {product['image_url']}")
                    print()
        else:
            print(f"  ❌ 搜索失败: {aihuishou_stats.get('error', '未知错误')}")

    @pytest.mark.asyncio
    async def test_agent_context_manager(self):
        """测试Agent的上下文管理器"""
        print(f"\n🔧 测试Agent上下文管理器")
        print("="*60)
        
        async with SecondhandSearchAgent() as agent:
            assert agent is not None
            assert hasattr(agent, 'client')
            print("✅ Agent上下文管理器工作正常")
            
            # 简单的备用关键词测试
            test_analysis = {
                "category": "电子产品",
                "sub_category": "手机", 
                "brand": "测试品牌"
            }
            
            fallback_result = agent._extract_keywords_fallback(test_analysis)
            assert fallback_result["success"] is True
            print("✅ 备用关键词提取功能正常")

    def test_parse_function_call_response(self):
        """测试Function Call响应解析功能"""
        print(f"\n🔧 测试Function Call响应解析")
        print("="*60)
        
        agent = SecondhandSearchAgent()
        
        # 测试成功情况
        success_content = '<APIs>[{"name": "extract_secondhand_keywords", "parameters": {"keywords": ["test"], "search_intent": "test intent", "platform_suggestions": {"xianyu": ["xianyu_test"], "aihuishou": ["aihuishou_test"]}}}]</APIs>'
        
        result = agent._parse_function_call_response(success_content)
        
        assert result is not None
        assert result["name"] == "extract_secondhand_keywords"
        assert "parameters" in result
        assert result["parameters"]["keywords"] == ["test"]
        print("✅ Function Call成功响应解析正常")
        
        # 测试失败情况
        failure_cases = [
            '<APIs>[invalid json]</APIs>',  # 无效JSON
            'no api tags here',  # 无API标签
            '<APIs>[]</APIs>'  # 空数组
        ]
        
        for failure_content in failure_cases:
            result = agent._parse_function_call_response(failure_content)
            assert result is None
        
        print("✅ Function Call失败响应处理正常")

    @pytest.mark.asyncio
    async def test_error_handling(self, agent):
        """测试错误处理机制"""
        print(f"\n🔧 测试错误处理机制")
        print("="*60)
        
        # 测试无效分析结果
        print("测试无效分析结果...")
        result = await agent.search_from_analysis(analysis_result={})
        assert result["success"] is False
        assert "error" in result
        print("✅ 空分析结果错误处理正常")
        
        result = await agent.search_from_analysis(analysis_result=None)
        assert result["success"] is False
        assert "error" in result
        print("✅ None分析结果错误处理正常")


if __name__ == "__main__":
    # 可以直接运行这个文件进行测试
    import asyncio
    
    async def run_single_test():
        """运行单个测试进行快速验证"""
        print("🌟 二手平台搜索Agent - 快速真实测试")
        print("="*60)
        
        test_analysis = {
            "category": "电子产品",
            "sub_category": "手机",
            "brand": "苹果",
            "model": "iPhone 13",
            "condition": "95新",
            "description": "苹果iPhone 13手机，黑色，128GB，功能正常，外观良好"
        }
        
        async with SecondhandSearchAgent() as agent:
            try:
                result = await agent.search_from_analysis(
                    analysis_result=test_analysis,
                    max_results_per_platform=3
                )
                
                if result["success"]:
                    search_result = result["result"]
                    print(f"✅ 搜索成功! 找到 {search_result['total_products']} 个商品")
                    
                    # 显示平台统计
                    platform_stats = search_result['platform_stats']
                    for platform, stats in platform_stats.items():
                        if stats['success']:
                            print(f"{platform}: {stats['product_count']} 个商品")
                        else:
                            print(f"{platform}: 搜索失败 - {stats.get('error', '未知错误')}")
                else:
                    print(f"❌ 搜索失败: {result.get('error')}")
                    
            except Exception as e:
                print(f"❌ 测试异常: {e}")
    
    print("选择运行方式:")
    print("1. 运行pytest测试")
    print("2. 运行快速单个测试")
    
    choice = input("请选择 (1/2): ").strip()
    
    if choice == "2":
        asyncio.run(run_single_test())
    else:
        pytest.main([__file__, "-v", "-s"]) 