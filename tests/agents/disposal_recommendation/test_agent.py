"""
三大处置路径推荐Agent测试

测试处置路径推荐Agent的核心功能
"""

import pytest
import asyncio
from pathlib import Path

from app.agents.disposal_recommendation.agent import DisposalRecommendationAgent
from app.prompts.disposal_recommendation_prompts import DisposalRecommendationPrompts


class TestDisposalRecommendationAgent:
    """处置路径推荐Agent测试类"""
    
    @pytest.fixture
    def agent(self):
        """创建Agent实例"""
        return DisposalRecommendationAgent()
    
    def test_prompts_initialization(self):
        """测试提示词初始化"""
        print(f"\n==== 测试提示词初始化 ====")
        
        system_prompt = DisposalRecommendationPrompts.get_system_prompt()
        print(f"系统提示词长度: {len(system_prompt)}")
        print(f"系统提示词前200字符: {system_prompt[:200]}...")
        
        assert isinstance(system_prompt, str)
        assert len(system_prompt) > 0
        assert "处置路径" in system_prompt or "处置方案" in system_prompt
        
        # 测试用户提示词模板
        sample_analysis = {
            "category": "测试类别",
            "condition": "测试状态",
            "description": "测试描述"
        }
        user_prompt = DisposalRecommendationPrompts.get_user_prompt(sample_analysis)
        print(f"用户提示词模板长度: {len(user_prompt)}")
        print(f"用户提示词包含分析结果: {'category: 测试类别' in user_prompt}")
        
        # 测试类别配置
        categories = list(DisposalRecommendationPrompts.CATEGORY_DISPOSAL_PREFERENCES.keys())
        print(f"支持的物品类别: {categories}")
        
        # 测试状态修正系数
        conditions = list(DisposalRecommendationPrompts.CONDITION_MODIFIERS.keys())
        print(f"支持的物品状态: {conditions}")
        
        print("提示词模块初始化测试通过！")
    
    def test_fallback_recommendations(self):
        """测试备用推荐逻辑"""
        print(f"\n==== 测试备用推荐逻辑 ====")
        print(f"测试类别: 电子产品, 状态: 八成新")
        
        result = DisposalRecommendationPrompts.get_fallback_recommendations(
            category="电子产品",
            condition="八成新"
        )
        
        print(f"备用推荐算法结果:")
        
        assert isinstance(result, dict)
        assert "creative_renovation" in result
        assert "recycling_donation" in result  
        assert "secondhand_trading" in result
        assert "overall_recommendation" in result
        
        # 检查推荐度
        creative_score = result["creative_renovation"]["recommendation_score"]
        recycling_score = result["recycling_donation"]["recommendation_score"]
        trading_score = result["secondhand_trading"]["recommendation_score"]
        
        assert 0 <= creative_score <= 100
        assert 0 <= recycling_score <= 100
        assert 0 <= trading_score <= 100
        
        # 检查标签
        assert isinstance(result["creative_renovation"]["reason_tags"], list)
        assert isinstance(result["recycling_donation"]["reason_tags"], list)
        assert isinstance(result["secondhand_trading"]["reason_tags"], list)
        
        print(f"\n--- 备用推荐结果 ---")
        
        # 创意改造
        creative = result["creative_renovation"]
        print(f"🎨 创意改造:")
        print(f"  推荐度: {creative.get('recommendation_score')}%")
        print(f"  推荐标签: {creative.get('reason_tags')}")
        print(f"  难度等级: {creative.get('difficulty_level')}")
        print(f"  预估耗时: {creative.get('estimated_time')}")
        print(f"  预估成本: {creative.get('estimated_cost')}")
        
        # 回收捐赠
        recycling = result["recycling_donation"]
        print(f"♻️ 回收捐赠:")
        print(f"  推荐度: {recycling.get('recommendation_score')}%")
        print(f"  推荐标签: {recycling.get('reason_tags')}")
        print(f"  环保影响: {recycling.get('environmental_impact')}")
        print(f"  社会价值: {recycling.get('social_value')}")
        
        # 二手交易
        trading = result["secondhand_trading"]
        print(f"💰 二手交易:")
        print(f"  推荐度: {trading.get('recommendation_score')}%")
        print(f"  推荐标签: {trading.get('reason_tags')}")
        print(f"  预估价格: {trading.get('estimated_price_range')}")
        print(f"  市场需求: {trading.get('market_demand')}")
        print(f"  销售难度: {trading.get('selling_difficulty')}")
        
        # 总体推荐
        overall = result["overall_recommendation"]
        print(f"\n🎯 总体推荐:")
        print(f"  首选方案: {overall.get('primary_choice')}")
        print(f"  推荐理由: {overall.get('reason')}")
        
        print(f"\n推荐度总和: {creative_score + recycling_score + trading_score}%")
    
    @pytest.mark.asyncio
    async def test_recommend_from_text(self, agent):
        """测试从文字描述推荐"""
        text_description = "一台用了两年的笔记本电脑，外观良好，配置中等，偶尔卡顿"
        
        print(f"\n==== 测试从文字描述推荐 ====")
        print(f"输入文字描述: {text_description}")
        
        try:
            result = await agent.recommend_from_text(text_description)
            
            print(f"测试结果成功: {result.get('success')}")
            print(f"数据来源: {result.get('source')}")
            print(f"推荐来源: {result.get('recommendation_source')}")
            
            assert isinstance(result, dict)
            assert "success" in result
            assert "source" in result
            assert result["source"] == "text"
            
            if result["success"]:
                print(f"\n--- 物品分析结果 ---")
                analysis = result.get("analysis_result", {})
                print(f"类别: {analysis.get('category')}")
                print(f"子类别: {analysis.get('sub_category')}")
                print(f"品牌: {analysis.get('brand')}")
                print(f"状态: {analysis.get('condition')}")
                print(f"关键词: {analysis.get('keywords')}")
                
                assert "recommendations" in result
                assert "analysis_result" in result
                
                recommendations = result["recommendations"]
                assert "creative_renovation" in recommendations
                assert "recycling_donation" in recommendations
                assert "secondhand_trading" in recommendations
                
                print(f"\n--- 三大处置路径推荐 ---")
                
                # 创意改造
                creative = recommendations["creative_renovation"]
                print(f"🎨 创意改造:")
                print(f"  推荐度: {creative.get('recommendation_score')}%")
                print(f"  推荐标签: {creative.get('reason_tags')}")
                print(f"  难度等级: {creative.get('difficulty_level')}")
                print(f"  预估耗时: {creative.get('estimated_time')}")
                print(f"  预估成本: {creative.get('estimated_cost')}")
                
                # 回收捐赠
                recycling = recommendations["recycling_donation"]
                print(f"♻️ 回收捐赠:")
                print(f"  推荐度: {recycling.get('recommendation_score')}%")
                print(f"  推荐标签: {recycling.get('reason_tags')}")
                print(f"  环保影响: {recycling.get('environmental_impact')}")
                print(f"  社会价值: {recycling.get('social_value')}")
                
                # 二手交易
                trading = recommendations["secondhand_trading"]
                print(f"💰 二手交易:")
                print(f"  推荐度: {trading.get('recommendation_score')}%")
                print(f"  推荐标签: {trading.get('reason_tags')}")
                print(f"  预估价格: {trading.get('estimated_price_range')}")
                print(f"  市场需求: {trading.get('market_demand')}")
                print(f"  销售难度: {trading.get('selling_difficulty')}")
                
                # 总体推荐
                overall = recommendations.get("overall_recommendation", {})
                print(f"\n🎯 总体推荐:")
                print(f"  首选方案: {overall.get('primary_choice')}")
                print(f"  推荐理由: {overall.get('reason')}")
                
            else:
                print(f"测试失败: {result.get('error')}")
                
        finally:
            await agent.close()
    
    @pytest.mark.asyncio  
    async def test_recommend_from_analysis(self, agent):
        """测试从分析结果推荐"""
        analysis_result = {
            "category": "电子产品",
            "sub_category": "笔记本电脑",
            "condition": "八成新",
            "brand": "联想",
            "keywords": ["电脑", "笔记本", "办公"],
            "description": "二手笔记本电脑，功能正常"
        }
        
        print(f"\n==== 测试从分析结果推荐 ====")
        print(f"输入分析结果: {analysis_result}")
        
        try:
            result = await agent.recommend_from_analysis(analysis_result)
            
            print(f"测试结果成功: {result.get('success')}")
            print(f"数据来源: {result.get('source')}")
            print(f"推荐来源: {result.get('recommendation_source')}")
            
            assert isinstance(result, dict)
            assert "success" in result
            assert "source" in result
            assert result["source"] == "analysis_result"
            
            if result["success"]:
                assert "recommendations" in result
                recommendations = result["recommendations"]
                assert "creative_renovation" in recommendations
                assert "recycling_donation" in recommendations
                assert "secondhand_trading" in recommendations
                
                print(f"\n--- 三大处置路径推荐 ---")
                
                # 创意改造
                creative = recommendations["creative_renovation"]
                print(f"🎨 创意改造:")
                print(f"  推荐度: {creative.get('recommendation_score')}%")
                print(f"  推荐标签: {creative.get('reason_tags')}")
                if 'difficulty_level' in creative:
                    print(f"  难度等级: {creative.get('difficulty_level')}")
                if 'estimated_time' in creative:
                    print(f"  预估耗时: {creative.get('estimated_time')}")
                if 'estimated_cost' in creative:
                    print(f"  预估成本: {creative.get('estimated_cost')}")
                
                # 回收捐赠
                recycling = recommendations["recycling_donation"]
                print(f"♻️ 回收捐赠:")
                print(f"  推荐度: {recycling.get('recommendation_score')}%")
                print(f"  推荐标签: {recycling.get('reason_tags')}")
                if 'environmental_impact' in recycling:
                    print(f"  环保影响: {recycling.get('environmental_impact')}")
                if 'social_value' in recycling:
                    print(f"  社会价值: {recycling.get('social_value')}")
                
                # 二手交易
                trading = recommendations["secondhand_trading"]
                print(f"💰 二手交易:")
                print(f"  推荐度: {trading.get('recommendation_score')}%")
                print(f"  推荐标签: {trading.get('reason_tags')}")
                if 'estimated_price_range' in trading:
                    print(f"  预估价格: {trading.get('estimated_price_range')}")
                if 'market_demand' in trading:
                    print(f"  市场需求: {trading.get('market_demand')}")
                if 'selling_difficulty' in trading:
                    print(f"  销售难度: {trading.get('selling_difficulty')}")
                
                # 总体推荐
                overall = recommendations.get("overall_recommendation", {})
                if overall:
                    print(f"\n🎯 总体推荐:")
                    print(f"  首选方案: {overall.get('primary_choice')}")
                    print(f"  推荐理由: {overall.get('reason')}")
                
            else:
                print(f"测试失败: {result.get('error')}")
                
        finally:
            await agent.close()
    
    def test_validation_logic(self):
        """测试推荐结果验证逻辑"""
        print(f"\n==== 测试推荐结果验证逻辑 ====")
        
        agent = DisposalRecommendationAgent()
        
        # 有效的推荐结果
        valid_result = {
            "creative_renovation": {
                "recommendation_score": 30,
                "reason_tags": ["改造潜力", "创意价值"]
            },
            "recycling_donation": {
                "recommendation_score": 40,
                "reason_tags": ["环保回收", "公益价值"]
            },
            "secondhand_trading": {
                "recommendation_score": 80,
                "reason_tags": ["保值性好", "需求量大"]
            }
        }
        
        validation_result = agent._validate_recommendation_result(valid_result)
        print(f"有效结果验证: {validation_result}")
        print(f"有效结果示例: {valid_result}")
        assert validation_result == True
        
        # 无效的推荐结果 - 缺少必要字段
        invalid_result = {
            "creative_renovation": {
                "recommendation_score": 30
                # 缺少 reason_tags
            },
            "recycling_donation": {
                "recommendation_score": 40,
                "reason_tags": ["环保回收"]
            }
            # 缺少 secondhand_trading
        }
        
        validation_result_invalid = agent._validate_recommendation_result(invalid_result)
        print(f"无效结果验证: {validation_result_invalid}")
        print(f"无效结果示例: {invalid_result}")
        assert validation_result_invalid == False
        
        # 测试分数范围验证
        invalid_score_result = {
            "creative_renovation": {
                "recommendation_score": 150,  # 超过100
                "reason_tags": ["改造潜力"]
            },
            "recycling_donation": {
                "recommendation_score": -10,  # 小于0
                "reason_tags": ["环保回收"]
            },
            "secondhand_trading": {
                "recommendation_score": 50,
                "reason_tags": ["保值性好"]
            }
        }
        
        validation_result_score = agent._validate_recommendation_result(invalid_score_result)
        print(f"无效分数验证: {validation_result_score}")
        assert validation_result_score == False
        
        print("推荐结果验证逻辑测试通过！")


if __name__ == "__main__":
    # 运行简单测试
    async def simple_test():
        print("=" * 60)
        print("三大处置路径推荐Agent - 简单功能测试")
        print("=" * 60)
        
        agent = DisposalRecommendationAgent()
        
        try:
            # 测试文字描述推荐
            text_description = "一张旧桌子，木质材料，有些划痕但还能用"
            print(f"\n📝 测试输入: {text_description}")
            print("正在调用AI模型分析...")
            
            result = await agent.recommend_from_text(text_description)
            
            print(f"\n✅ 测试结果: {'成功' if result.get('success') else '失败'}")
            print(f"🔄 推荐来源: {result.get('recommendation_source', '未知')}")
            
            if result.get('success'):
                # 显示分析结果
                analysis = result.get('analysis_result', {})
                print(f"\n📊 物品分析:")
                print(f"   类别: {analysis.get('category')}")
                print(f"   状态: {analysis.get('condition')}")
                print(f"   材质: {analysis.get('material')}")
                
                # 显示推荐结果
                recommendations = result.get('recommendations', {})
                print(f"\n🎯 处置路径推荐:")
                
                creative = recommendations.get('creative_renovation', {})
                print(f"   🎨 创意改造: {creative.get('recommendation_score', 0)}%")
                print(f"      标签: {creative.get('reason_tags', [])}")
                
                recycling = recommendations.get('recycling_donation', {})
                print(f"   ♻️ 回收捐赠: {recycling.get('recommendation_score', 0)}%")
                print(f"      标签: {recycling.get('reason_tags', [])}")
                
                trading = recommendations.get('secondhand_trading', {})
                print(f"   💰 二手交易: {trading.get('recommendation_score', 0)}%")
                print(f"      标签: {trading.get('reason_tags', [])}")
                
                # 显示总体推荐
                overall = recommendations.get('overall_recommendation', {})
                if overall:
                    print(f"\n🏆 最佳推荐: {overall.get('primary_choice')}")
                    print(f"   理由: {overall.get('reason')}")
                
            else:
                print(f"❌ 错误信息: {result.get('error')}")
            
        except Exception as e:
            print(f"❌ 测试异常: {e}")
            import traceback
            traceback.print_exc()
        finally:
            await agent.close()
            print(f"\n🔚 测试完成")
    
    # 运行测试
    print("启动异步测试...")
    asyncio.run(simple_test()) 