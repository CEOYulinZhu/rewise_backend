"""
平台推荐Agent测试

测试平台推荐Agent的核心功能
"""

import asyncio

import pytest

from app.agents.platform_recommendation.agent import PlatformRecommendationAgent
from app.models.platform_recommendation_agent_models import (
    PlatformRecommendationResponse,
    PlatformRecommendationResult,
    PlatformRecommendationItem
)
from app.prompts.platform_recommendation_prompts import PlatformRecommendationPrompts


class TestPlatformRecommendationAgent:
    """平台推荐Agent测试类"""
    
    @pytest.fixture
    def agent(self):
        """创建Agent实例"""
        return PlatformRecommendationAgent()
    
    @pytest.fixture
    def sample_analysis_result(self):
        """样例分析结果"""
        return {
            "category": "电子产品",
            "sub_category": "智能手机",
            "condition": "八成新",
            "description": "iPhone 13，使用一年多，外观良好，功能正常",
            "brand": "苹果",
            "material": "金属玻璃",
            "keywords": ["手机", "iPhone", "苹果", "智能手机"],
            "special_features": "Face ID正常，电池健康度85%"
        }
    
    def test_data_models(self):
        """测试数据模型"""
        print(f"\n==== 测试数据模型 ====")
        
        # 测试单个推荐项
        rec_item = PlatformRecommendationItem(
            platform_name="闲鱼",
            suitability_score=8.5,
            pros=["用户量大", "交易便捷", "支付宝保障"],
            cons=["竞争激烈", "价格透明度低"],
            recommendation_reason="适合个人卖家快速出售，用户基数大"
        )
        
        assert rec_item.platform_name == "闲鱼"
        assert rec_item.suitability_score == 8.5
        assert len(rec_item.pros) == 3
        assert len(rec_item.cons) == 2
        
        # 测试数据验证 - 分数范围
        try:
            invalid_rec = PlatformRecommendationItem(
                platform_name="测试",
                suitability_score=15,  # 超出范围
                pros=["测试"],
                cons=["测试"],
                recommendation_reason="测试"
            )
            assert False, "应该抛出验证错误"
        except ValueError as e:
            print(f"✅ 分数范围验证正常: {e}")
        
        # 测试推荐结果
        result = PlatformRecommendationResult(recommendations=[rec_item])
        platform_names = result.get_platform_names()
        assert platform_names == ["闲鱼"]
        
        print("数据模型测试通过！")
    
    def test_prompts_initialization(self):
        """测试提示词初始化"""
        print(f"\n==== 测试提示词初始化 ====")
        
        system_prompt = PlatformRecommendationPrompts.get_system_prompt()
        print(f"系统提示词长度: {len(system_prompt)}")
        print(f"\n【系统提示词完整内容】:")
        print("=" * 80)
        print(system_prompt)
        print("=" * 80)
        
        assert isinstance(system_prompt, str)
        assert len(system_prompt) > 0
        assert "平台推荐" in system_prompt or "二手交易" in system_prompt
        
        # 测试用户提示词模板
        sample_analysis = {
            "category": "电子产品",
            "sub_category": "智能手机",
            "condition": "八成新",
            "description": "iPhone 13，外观良好，功能正常",
            "brand": "苹果",
            "keywords": ["手机", "iPhone", "苹果"]
        }
        sample_rag_results = [
            {
                "raw_platform_data": {
                    "platform_name": "闲鱼",
                    "description": "阿里旗下'国民级'二手社区，用户超3亿，覆盖全品类",
                    "focus_categories": ["全品类", "电子产品"],
                    "tags": ["芝麻信用分参考", "支付宝担保交易"],
                    "transaction_model": "C2C",
                    "user_data": {"monthly_active_users": "2.09亿"},
                    "rating": {"app_store": 4.7}
                },
                "similarity": 0.85,
                "metadata": {
                    "platform_name": "闲鱼",
                    "description": "阿里旗下'国民级'二手社区"
                }
            },
            {
                "raw_platform_data": {
                    "platform_name": "转转",
                    "description": "58同城旗下平台，主打年轻用户群体",
                    "focus_categories": ["3C数码", "手机回收"],
                    "tags": ["官方验机", "AI验机"],
                    "transaction_model": "C2C、C2B2C",
                    "user_data": {"monthly_active_users": "0.36亿"},
                    "rating": {"yingyongbao": 4.4}
                },
                "similarity": 0.72,
                "metadata": {
                    "platform_name": "转转",
                    "description": "58同城旗下平台"
                }
            }
        ]
        
        user_prompt = PlatformRecommendationPrompts.get_user_prompt(sample_analysis, sample_rag_results)
        print(f"\n用户提示词长度: {len(user_prompt)}")
        print(f"\n【用户提示词完整内容】:")
        print("=" * 80)
        print(user_prompt)
        print("=" * 80)
        
        assert "电子产品" in user_prompt
        assert "闲鱼" in user_prompt
        assert "转转" in user_prompt
        assert "iPhone" in user_prompt
        
        print("提示词模块测试通过！")
    
    def test_fallback_recommendations(self):
        """测试备用推荐逻辑"""
        print(f"\n==== 测试备用推荐逻辑 ====")
        
        # 测试电子产品推荐
        result = PlatformRecommendationPrompts.get_fallback_recommendations("电子产品")
        print(f"电子产品备用推荐: {len(result['recommendations'])}个平台")
        
        assert isinstance(result, dict)
        assert "recommendations" in result
        recommendations = result["recommendations"]
        assert len(recommendations) >= 1
        
        for rec in recommendations:
            assert "platform_name" in rec
            assert "suitability_score" in rec
            assert "pros" in rec
            assert "cons" in rec
            assert "recommendation_reason" in rec
            assert 0 <= rec["suitability_score"] <= 10
        
        print(f"✅ 备用推荐结果验证通过")
        
        # 测试图书推荐
        book_result = PlatformRecommendationPrompts.get_fallback_recommendations("图书")
        print(f"图书备用推荐: {len(book_result['recommendations'])}个平台")
        assert len(book_result["recommendations"]) >= 1
        
        print("备用推荐逻辑测试通过！")
    
    @pytest.mark.asyncio
    async def test_recommend_platforms(self, agent, sample_analysis_result):
        """测试平台推荐核心功能"""
        print(f"\n==== 测试平台推荐核心功能 ====")
        print(f"【输入分析结果】:")
        import json
        print(json.dumps(sample_analysis_result, ensure_ascii=False, indent=2))
        
        try:
            response = await agent.recommend_platforms(sample_analysis_result)
            
            print(f"\n【响应基本信息】:")
            print(f"  推荐结果成功: {response.success}")
            print(f"  数据来源: {response.source}")
            
            # 打印完整响应对象的所有字段
            print(f"\n【Agent返回的完整响应数据结构】:")
            print("=" * 80)
            response_dict = response.dict()
            print(json.dumps(response_dict, ensure_ascii=False, indent=2, default=str))
            print("=" * 80)
            
            assert isinstance(response, PlatformRecommendationResponse)
            
            if response.success:
                print(f"\n【物品分析结果回显】:")
                analysis = response.analysis_result
                print(f"  类别: {analysis.get('category')}")
                print(f"  子类别: {analysis.get('sub_category')}")
                print(f"  品牌: {analysis.get('brand')}")
                print(f"  状态: {analysis.get('condition')}")
                print(f"  描述: {analysis.get('description')}")
                print(f"  关键词: {analysis.get('keywords')}")
                print(f"  特殊特性: {analysis.get('special_features')}")
                
                # 验证AI推荐结果
                ai_recs = response.ai_recommendations
                assert ai_recs is not None
                assert isinstance(ai_recs, PlatformRecommendationResult)
                
                print(f"\n【AI推荐结果详情】:")
                recommendations = ai_recs.recommendations
                print(f"  推荐平台数量: {len(recommendations)}")
                
                for i, rec in enumerate(recommendations, 1):
                    print(f"\n  {i}. 【{rec.platform_name}】")
                    print(f"     适合度评分: {rec.suitability_score}/10")
                    print(f"     优势: {rec.pros}")
                    print(f"     劣势: {rec.cons}")
                    print(f"     推荐理由: {rec.recommendation_reason}")
                    
                    # 验证数据格式
                    assert 0 <= rec.suitability_score <= 10
                    assert 1 <= len(rec.pros) <= 3
                    assert 1 <= len(rec.cons) <= 2
                    assert len(rec.recommendation_reason) > 0
                
                # 验证平台详细数据
                if response.platform_details:
                    print(f"\n【推荐平台的完整基础数据】:")
                    print(f"  获取到 {len(response.platform_details)} 个平台的详细数据")
                    for idx, platform in enumerate(response.platform_details, 1):
                        print(f"\n  {idx}. 平台: {platform.get('platform_name')}")
                        print(f"     平台图标: {platform.get('platform_icon', 'N/A')}")
                        print(f"     描述: {platform.get('description', 'N/A')}")
                        print(f"     主要品类: {platform.get('focus_categories', [])}")
                        print(f"     平台特色: {platform.get('tags', [])}")
                        print(f"     交易模式: {platform.get('transaction_model', 'N/A')}")
                        
                        user_data = platform.get('user_data', {})
                        if user_data:
                            print(f"     用户数据:")
                            for key, value in user_data.items():
                                if value:
                                    print(f"       {key}: {value}")
                        
                        rating = platform.get('rating', {})
                        if rating:
                            print(f"     用户评分:")
                            for store, score in rating.items():
                                if score:
                                    print(f"       {store}: {score}")
                else:
                    print(f"\n【警告】: 未获取到推荐平台的详细数据")
                
                # 测试便捷方法
                print(f"\n【便捷方法测试】:")
                top_rec = response.get_top_recommendation()
                if top_rec:
                    print(f"  get_top_recommendation(): {top_rec.platform_name} ({top_rec.suitability_score})")
                
                platform_names = response.ai_recommendations.get_platform_names()
                print(f"  get_platform_names(): {platform_names}")
                
                # 显示AI原始响应
                if hasattr(response, 'ai_raw_response') and response.ai_raw_response:
                    print(f"\n【AI模型原始响应】:")
                    print("=" * 80)
                    print(response.ai_raw_response)
                    print("=" * 80)
                else:
                    print(f"\n【注意】: 未获取到AI原始响应内容")
                
            else:
                print(f"\n【推荐失败信息】: {response.error}")
                
        finally:
            await agent.close()
    
    def test_validation_logic(self, sample_analysis_result):
        """测试输入验证逻辑"""
        print(f"\n==== 测试输入验证逻辑 ====")
        
        agent = PlatformRecommendationAgent()
        
        # 测试空输入
        async def test_empty_input():
            response = await agent.recommend_platforms(None)
            assert not response.success
            assert "分析结果为空" in response.error
            
            response = await agent.recommend_platforms({})
            # 空字典应该会在后续处理中出现问题，但不会在最初验证时失败
            print(f"空字典输入结果: {response.success}")
        
        asyncio.run(test_empty_input())
        
        # 测试正常输入
        print("测试正常输入格式...")
        assert isinstance(sample_analysis_result, dict)
        assert "category" in sample_analysis_result
        assert "condition" in sample_analysis_result
        print("输入验证逻辑测试通过！")


    @pytest.mark.asyncio
    async def test_detailed_workflow(self, agent):
        """测试详细工作流程，显示所有内部处理过程"""
        print(f"\n==== 测试详细工作流程 ====")
        
        # 创建详细的分析结果
        analysis_result = {
            "category": "电子产品",
            "sub_category": "笔记本电脑",
            "condition": "八成新",
            "description": "MacBook Pro 2021，M1芯片，16GB内存，512GB存储，轻微使用痕迹",
            "brand": "苹果",
            "material": "铝合金",
            "keywords": ["笔记本", "MacBook", "苹果", "M1"],
            "special_features": "M1芯片，Retina显示屏，Touch Bar"
        }
        
        print(f"【测试输入】:")
        import json
        print(json.dumps(analysis_result, ensure_ascii=False, indent=2))
        
        try:
            # 首先测试RAG服务单独调用
            from app.services.rag.platform_recommendation_service import PlatformRecommendationRAGService
            from app.models.platform_recommendation_models import ItemAnalysisModel, RAGSearchRequest
            
            print(f"\n【步骤1：RAG服务检索】:")
            rag_service = PlatformRecommendationRAGService()
            rag_request = RAGSearchRequest(
                item_analysis=ItemAnalysisModel(**analysis_result),
                similarity_threshold=0.3,
                max_results=5
            )
            
            rag_response = await rag_service.search_platforms(rag_request)
            print(f"  RAG检索结果数量: {len(rag_response.results)}")
            print(f"  RAG搜索元数据: {rag_response.search_metadata}")
            
            for i, result in enumerate(rag_response.results, 1):
                print(f"\n  RAG结果 {i}:")
                print(f"    平台名称: {result.get('platform_name', 'N/A')}")
                print(f"    相似度: {result.get('similarity', 0):.3f}")
                print(f"    文档摘要: {result.get('document', '')[:100]}...")
            
            # 构建提示词
            print(f"\n【步骤2：构建提示词】:")
            from app.prompts.platform_recommendation_prompts import PlatformRecommendationPrompts
            
            system_prompt = PlatformRecommendationPrompts.get_system_prompt()
            user_prompt = PlatformRecommendationPrompts.get_user_prompt(analysis_result, rag_response.results)
            
            print(f"  系统提示词长度: {len(system_prompt)}")
            print(f"  用户提示词长度: {len(user_prompt)}")
            
            print(f"\n【系统提示词】:")
            print("-" * 60)
            print(system_prompt)
            print("-" * 60)
            
            print(f"\n【用户提示词】:")
            print("-" * 60)
            print(user_prompt)
            print("-" * 60)
            
            # 调用完整Agent
            print(f"\n【步骤3：Agent完整调用】:")
            response = await agent.recommend_platforms(analysis_result)
            
            if response.success:
                print(f"  Agent调用成功!")
                
                # 显示完整响应结构
                print(f"\n【Agent响应完整结构】:")
                response_dict = response.dict()
                print(json.dumps(response_dict, ensure_ascii=False, indent=2, default=str))
                
                # 显示各个字段的详细信息
                print(f"\n【响应字段详细解析】:")
                print(f"  success: {response.success} (bool)")
                print(f"  source: {response.source} (str)")
                print(f"  analysis_result: {type(response.analysis_result)} - 回显的输入分析结果")
                print(f"  ai_recommendations: {type(response.ai_recommendations)} - AI推荐结果对象")
                print(f"  platform_details: {type(response.platform_details)} - 推荐平台的完整数据列表")
                print(f"  rag_metadata: {type(response.rag_metadata)} - RAG检索元数据")
                print(f"  error: {response.error} (None表示无错误)")
                
                if response.ai_recommendations:
                    recs = response.ai_recommendations.recommendations
                    print(f"\n【AI推荐结果结构解析】:")
                    print(f"  recommendations: List[PlatformRecommendationItem] (长度: {len(recs)})")
                    
                    for i, rec in enumerate(recs, 1):
                        print(f"\n  推荐项 {i}:")
                        print(f"    platform_name: {rec.platform_name} (str)")
                        print(f"    suitability_score: {rec.suitability_score} (float, 0-10)")
                        print(f"    pros: {rec.pros} (List[str], 长度: {len(rec.pros)})")
                        print(f"    cons: {rec.cons} (List[str], 长度: {len(rec.cons)})")
                        print(f"    recommendation_reason: {rec.recommendation_reason} (str)")
                
                if response.platform_details:
                    print(f"\n【平台详细数据结构解析】:")
                    print(f"  platform_details: List[Dict] (长度: {len(response.platform_details)})")
                    
                    for i, platform in enumerate(response.platform_details, 1):
                        print(f"\n  平台详细数据 {i}:")
                        print(f"    数据类型: {type(platform)}")
                        print(f"    字段数量: {len(platform)}")
                        print(f"    主要字段: {list(platform.keys())}")
                        print(f"    platform_name: {platform.get('platform_name')}")
                        print(f"    description: {platform.get('description', '')[:50]}...")
                
                # 测试便捷方法
                print(f"\n【便捷方法测试】:")
                top_rec = response.get_top_recommendation()
                if top_rec:
                    print(f"  get_top_recommendation(): {top_rec.platform_name} ({top_rec.suitability_score})")
                
                platform_names = response.ai_recommendations.get_platform_names()
                print(f"  get_platform_names(): {platform_names}")
                
                # 显示AI原始响应
                if hasattr(response, 'ai_raw_response') and response.ai_raw_response:
                    print(f"\n【AI模型原始响应内容】:")
                    print("=" * 80)
                    print(response.ai_raw_response)
                    print("=" * 80)
                    print(f"  原始响应长度: {len(response.ai_raw_response)} 字符")
                else:
                    print(f"\n【注意】: 未获取到AI原始响应内容")
                
            else:
                print(f"  Agent调用失败: {response.error}")
                
        except Exception as e:
            print(f"【错误】: {e}")
            import traceback
            traceback.print_exc()
            
        finally:
            await agent.close()


async def simple_test():
    """简单快速测试"""
    print("\n" + "="*50)
    print("平台推荐Agent - 简单测试")
    print("="*50)
    
    # 创建样例分析结果
    analysis_result = {
        "category": "电子产品",
        "sub_category": "智能手机",
        "condition": "八成新", 
        "description": "iPhone 14，使用半年，外观完好",
        "brand": "苹果",
        "material": "金属玻璃",
        "keywords": ["手机", "iPhone", "苹果"]
    }
    
    async with PlatformRecommendationAgent() as agent:
        response = await agent.recommend_platforms(analysis_result)
        
        if response.success:
            print(f"✅ 平台推荐成功!")
            
            ai_recs = response.ai_recommendations
            if ai_recs:
                print(f"\n📊 推荐平台排名:")
                recommendations = ai_recs.recommendations
                for i, rec in enumerate(recommendations, 1):
                    print(f"{i}. {rec.platform_name}: {rec.suitability_score}/10")
                
                top_rec = response.get_top_recommendation()
                if top_rec:
                    print(f"\n🎯 最佳推荐: {top_rec.platform_name} ({top_rec.suitability_score}/10)")
                    print(f"推荐理由: {top_rec.recommendation_reason}")
            
            if response.platform_details:
                print(f"\n📋 获取到 {len(response.platform_details)} 个平台的详细数据")
        
        else:
            print(f"❌ 平台推荐失败: {response.error}")


if __name__ == "__main__":
    # 运行简单测试
    asyncio.run(simple_test()) 