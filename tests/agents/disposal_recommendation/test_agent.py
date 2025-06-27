"""
三大处置路径推荐Agent测试

测试处置路径推荐Agent的核心功能
"""

import asyncio

import pytest

from app.agents.disposal_recommendation.agent import DisposalRecommendationAgent
from app.prompts.disposal_recommendation_prompts import DisposalRecommendationPrompts
from app.models.disposal_recommendation_models import (
    DisposalRecommendationResponse,
    DisposalRecommendations,
    DisposalPathRecommendation,
    OverallRecommendation
)


class TestDisposalRecommendationAgent:
    """处置路径推荐Agent测试类"""
    
    @pytest.fixture
    def agent(self):
        """创建Agent实例"""
        return DisposalRecommendationAgent()
    
    def test_data_models(self):
        """测试数据模型"""
        print(f"\n==== 测试数据模型 ====")
        
        # 测试单个路径推荐
        creative_rec = DisposalPathRecommendation(
            recommendation_score=75,
            reason_tags=["创意改造", "环保利用", "DIY"]
        )
        assert creative_rec.recommendation_score == 75
        assert len(creative_rec.reason_tags) == 3
        
        # 测试数据验证 - 分数范围
        try:
            invalid_rec = DisposalPathRecommendation(
                recommendation_score=150,  # 超出范围
                reason_tags=["测试"]
            )
            assert False, "应该抛出验证错误"
        except ValueError as e:
            print(f"✅ 分数范围验证正常: {e}")
        
        # 测试数据验证 - 标签长度
        try:
            invalid_rec = DisposalPathRecommendation(
                recommendation_score=50,
                reason_tags=["这是一个超过七个字符的标签"]  # 超出长度
            )
            assert False, "应该抛出验证错误"
        except ValueError as e:
            print(f"✅ 标签长度验证正常: {e}")
        
        # 测试完整推荐对象
        recycling_rec = DisposalPathRecommendation(50, ["环保", "回收"])
        trading_rec = DisposalPathRecommendation(80, ["保值", "需求大"])
        overall_rec = OverallRecommendation("二手交易", "最具性价比")
        
        recommendations = DisposalRecommendations(
            creative_renovation=creative_rec,
            recycling_donation=recycling_rec,
            secondhand_trading=trading_rec,
            overall_recommendation=overall_rec
        )
        
        # 测试便捷方法
        sorted_recs = recommendations.get_sorted_recommendations()
        highest_rec = recommendations.get_highest_recommendation()
        
        print(f"推荐排序: {[(name, rec.recommendation_score) for name, rec in sorted_recs]}")
        print(f"最高推荐: {highest_rec[0]} ({highest_rec[1].recommendation_score})")
        
        assert highest_rec[0] == "二手交易"
        assert highest_rec[1].recommendation_score == 80
        
        # 测试字典转换
        dict_result = recommendations.to_dict()
        assert "creative_renovation" in dict_result
        assert dict_result["creative_renovation"]["recommendation_score"] == 75
        
        print("数据模型测试通过！")
    
    @pytest.fixture
    def sample_analysis_result(self):
        """样例分析结果"""
        return {
            "category": "电子产品",
            "sub_category": "笔记本电脑",
            "condition": "八成新",
            "description": "一台用了两年的笔记本电脑，外观良好，配置中等",
            "brand": "联想",
            "material": "塑料金属",
            "keywords": ["笔记本", "电脑", "联想"],
            "special_features": "偶尔卡顿"
        }
    
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
        print(f"  推荐度: {creative.get('recommendation_score')}")
        print(f"  推荐标签: {creative.get('reason_tags')}")
        
        # 回收捐赠
        recycling = result["recycling_donation"]
        print(f"♻️ 回收捐赠:")
        print(f"  推荐度: {recycling.get('recommendation_score')}")
        print(f"  推荐标签: {recycling.get('reason_tags')}")
        
        # 二手交易
        trading = result["secondhand_trading"]
        print(f"💰 二手交易:")
        print(f"  推荐度: {trading.get('recommendation_score')}")
        print(f"  推荐标签: {trading.get('reason_tags')}")
        
        # 总体推荐
        overall = result["overall_recommendation"]
        print(f"\n🎯 总体推荐:")
        print(f"  首选方案: {overall.get('primary_choice')}")
        print(f"  推荐理由: {overall.get('reason')}")
        
        print(f"\n推荐度总和: {creative_score + recycling_score + trading_score}")
    
    @pytest.mark.asyncio
    async def test_recommend_from_analysis(self, agent, sample_analysis_result):
        """测试从分析结果推荐"""
        print(f"\n==== 测试从分析结果推荐 ====")
        print(f"输入分析结果: {sample_analysis_result}")
        
        try:
            response = await agent.recommend_from_analysis(sample_analysis_result)
            
            print(f"测试结果成功: {response.success}")
            print(f"数据来源: {response.source}")
            print(f"推荐来源: {response.recommendation_source}")
            
            assert isinstance(response, DisposalRecommendationResponse)
            assert response.source == "analysis_result"
            
            if response.success:
                print(f"\n--- 物品分析结果 ---")
                analysis = response.analysis_result
                print(f"类别: {analysis.get('category')}")
                print(f"子类别: {analysis.get('sub_category')}")
                print(f"品牌: {analysis.get('brand')}")
                print(f"状态: {analysis.get('condition')}")
                print(f"关键词: {analysis.get('keywords')}")
                
                assert response.recommendations is not None
                assert response.analysis_result is not None
                
                recommendations = response.recommendations
                assert isinstance(recommendations, DisposalRecommendations)
                
                print(f"\n--- 三大处置路径推荐 ---")
                
                # 创意改造
                creative = recommendations.creative_renovation
                print(f"🎨 创意改造:")
                print(f"  推荐度: {creative.recommendation_score}")
                print(f"  推荐标签: {creative.reason_tags}")
                
                # 回收捐赠
                recycling = recommendations.recycling_donation
                print(f"♻️ 回收捐赠:")
                print(f"  推荐度: {recycling.recommendation_score}")
                print(f"  推荐标签: {recycling.reason_tags}")
                
                # 二手交易
                trading = recommendations.secondhand_trading
                print(f"💰 二手交易:")
                print(f"  推荐度: {trading.recommendation_score}")
                print(f"  推荐标签: {trading.reason_tags}")
                
                # 总体推荐
                overall = recommendations.overall_recommendation
                if overall:
                    print(f"\n🎯 总体推荐:")
                    print(f"  首选方案: {overall.primary_choice}")
                    print(f"  推荐理由: {overall.reason}")
                
                # 测试便捷方法
                sorted_recs = recommendations.get_sorted_recommendations()
                highest_rec = recommendations.get_highest_recommendation()
                print(f"\n📊 推荐排序:")
                for i, (name, rec) in enumerate(sorted_recs):
                    print(f"  {i+1}. {name}: {rec.recommendation_score}")
                print(f"最高推荐: {highest_rec[0]} ({highest_rec[1].recommendation_score})")
                
                # 测试数据验证
                assert 0 <= creative.recommendation_score <= 100
                assert 0 <= recycling.recommendation_score <= 100
                assert 0 <= trading.recommendation_score <= 100
                assert len(creative.reason_tags) <= 5
                assert len(recycling.reason_tags) <= 5
                assert len(trading.reason_tags) <= 5
                
            else:
                print(f"测试失败: {response.error}")
                
        finally:
            await agent.close()
    
    def test_validation_logic(self, sample_analysis_result):
        """测试输入验证逻辑"""
        print(f"\n==== 测试输入验证逻辑 ====")
        
        agent = DisposalRecommendationAgent()
        
        # 测试空输入
        print("测试空输入...")
        import asyncio
        
        async def test_empty_input():
            response = await agent.recommend_from_analysis(None)
            assert not response.success
            assert "分析结果为空" in response.error
            
            response = await agent.recommend_from_analysis({})
            # 空字典应该被接受但可能导致后续处理问题
            print(f"空字典输入结果: {response.success}")
        
        asyncio.run(test_empty_input())
        
        # 测试正常输入
        print("测试正常输入格式...")
        assert isinstance(sample_analysis_result, dict)
        assert "category" in sample_analysis_result
        assert "condition" in sample_analysis_result
        print("输入验证逻辑测试通过！")


async def simple_test():
    """简单快速测试"""
    print("\n" + "="*50)
    print("处置路径推荐Agent - 简单测试")
    print("="*50)
    
    # 创建样例分析结果
    analysis_result = {
        "category": "电子产品",
        "sub_category": "智能手机",
        "condition": "八成新",
        "description": "一台iPhone，外观良好，电池稍有老化",
        "brand": "苹果",
        "material": "金属玻璃",
        "keywords": ["手机", "iPhone", "苹果"]
    }
    
    async with DisposalRecommendationAgent() as agent:
        response = await agent.recommend_from_analysis(analysis_result)
        
        if response.success:
            recommendations = response.recommendations
            print(f"✅ 处置路径推荐成功!")
            
            print(f"\n📊 推荐度排名:")
            scores = [
                ("创意改造", recommendations.creative_renovation.recommendation_score),
                ("回收捐赠", recommendations.recycling_donation.recommendation_score),
                ("二手交易", recommendations.secondhand_trading.recommendation_score)
            ]
            scores.sort(key=lambda x: x[1], reverse=True)
            
            for i, (name, score) in enumerate(scores):
                print(f"{i+1}. {name}: {score}")
            
            # 使用便捷方法
            highest_rec = recommendations.get_highest_recommendation()
            print(f"\n🎯 最高推荐: {highest_rec[0]} ({highest_rec[1].recommendation_score})")
            
            overall = recommendations.overall_recommendation
            if overall:
                print(f"首选方案: {overall.primary_choice}")
                print(f"推荐理由: {overall.reason}")
            
        else:
            print(f"❌ 处置路径推荐失败: {response.error}")


if __name__ == "__main__":
    # 运行简单测试
    asyncio.run(simple_test()) 