"""
创意改造步骤Agent测试

测试创意改造Agent的核心功能
"""

import asyncio

import pytest

from app.agents.creative_renovation.agent import CreativeRenovationAgent
from app.prompts.creative_renovation_prompts import CreativeRenovationPrompts


class TestCreativeRenovationAgent:
    """创意改造Agent测试类"""
    
    @pytest.fixture
    def agent(self):
        """创建Agent实例"""
        return CreativeRenovationAgent()
    
    @pytest.fixture
    def sample_analysis_result(self):
        """样例分析结果"""
        return {
            "category": "家具",
            "sub_category": "椅子",
            "condition": "八成新",
            "description": "一把旧木椅子，表面有轻微磨损",
            "material": "木质",
            "color": "棕色",
            "keywords": ["椅子", "木质", "家具"],
            "special_features": "有些许磨损"
        }
    
    def test_prompts_initialization(self):
        """测试提示词初始化"""
        print(f"\n==== 测试提示词初始化 ====")
        
        system_prompt = CreativeRenovationPrompts.get_system_prompt()
        print(f"系统提示词长度: {len(system_prompt)}")
        print(f"系统提示词前200字符: {system_prompt[:200]}...")
        
        assert isinstance(system_prompt, str)
        assert len(system_prompt) > 0
        assert "改造" in system_prompt or "JSON" in system_prompt
        
        # 测试用户提示词模板
        sample_analysis = {
            "category": "家具",
            "sub_category": "椅子",
            "condition": "八成新",
            "description": "一把旧木椅子",
            "material": "木质",
            "color": "棕色",
            "keywords": ["椅子", "木质", "家具"],
            "special_features": "有些许磨损"
        }
        user_prompt = CreativeRenovationPrompts.get_user_prompt(sample_analysis)
        print(f"用户提示词模板长度: {len(user_prompt)}")
        print(f"用户提示词包含物品信息: {'家具' in user_prompt}")
        
        # 测试类别配置
        categories = list(CreativeRenovationPrompts.CATEGORY_RENOVATION_PREFERENCES.keys())
        print(f"支持的物品类别: {categories}")
        
        # 测试状态影响
        conditions = list(CreativeRenovationPrompts.CONDITION_IMPACT.keys())
        print(f"支持的物品状态: {conditions}")
        
        print("提示词模块初始化测试通过！")
    
    def test_fallback_renovation_plan(self):
        """测试备用改造方案生成"""
        print(f"\n==== 测试备用改造方案生成 ====")
        print(f"测试类别: 家具, 状态: 八成新, 描述: 旧木桌")
        
        result = CreativeRenovationPrompts.get_fallback_renovation_plan(
            category="家具",
            condition="八成新",
            description="一张旧木桌，表面有划痕"
        )
        
        print(f"备用改造方案生成结果:")
        
        assert isinstance(result, dict)
        assert "project_title" in result
        assert "steps" in result
        assert "final_result" in result
        
        # 检查项目信息
        print(f"\n--- 改造项目信息 ---")
        print(f"项目标题: {result.get('project_title')}")
        print(f"项目描述: {result.get('project_description')}")
        print(f"难度等级: {result.get('difficulty_level')}")
        cost_range = result.get('estimated_cost_range', {})
        if isinstance(cost_range, dict):
            print(f"预计成本: {cost_range.get('min_cost')}-{cost_range.get('max_cost')}元")
        else:
            print(f"预计成本: {cost_range}")
        print(f"所需技能: {result.get('required_skills')}")
        
        # 检查安全警告
        safety_warnings = result.get("safety_warnings", [])
        print(f"\n--- 安全警告 ({len(safety_warnings)}条) ---")
        for i, warning in enumerate(safety_warnings):
            print(f"{i+1}. {warning}")
        
        # 检查改造步骤
        steps = result.get("steps", [])
        print(f"\n--- 改造步骤 ({len(steps)}步) ---")
        for step in steps:
            print(f"步骤 {step.get('step_number')}: {step.get('title')}")
            print(f"  描述: {step.get('description')}")
            print(f"  所需工具: {step.get('tools_needed')}")
            print(f"  所需材料: {step.get('materials_needed')}")
            # 适配新格式
            if 'estimated_time_minutes' in step:
                print(f"  预计耗时: {step.get('estimated_time_minutes')}分钟")
            else:
                print(f"  预计耗时: {step.get('estimated_time')}")
            print(f"  难度: {step.get('difficulty')}")
            print(f"  小贴士: {step.get('tips')}")
            print()
        
        # 检查最终结果
        final_result = result.get("final_result", {})
        print(f"--- 最终结果 ---")
        print(f"成品描述: {final_result.get('description')}")
        print(f"使用场景: {final_result.get('usage_scenarios')}")
        print(f"保养建议: {final_result.get('maintenance_tips')}")
        
        # 检查替代方案
        alternative_ideas = result.get("alternative_ideas", [])
        print(f"\n--- 替代方案 ({len(alternative_ideas)}个) ---")
        for idea in alternative_ideas:
            print(f"- {idea.get('title')}: {idea.get('description')}")
        
        assert len(steps) > 0
        assert isinstance(final_result, dict)
    
    def test_category_preferences(self):
        """测试类别偏好配置"""
        print(f"\n==== 测试类别偏好配置 ====")
        
        # 测试精确匹配
        furniture_prefs = CreativeRenovationPrompts.get_category_preferences("家具")
        print(f"家具类别配置: {furniture_prefs}")
        assert "优势" in furniture_prefs
        assert "常见改造" in furniture_prefs
        assert "难度系数" in furniture_prefs
        assert "成本系数" in furniture_prefs
        
        # 测试模糊匹配
        electronics_prefs = CreativeRenovationPrompts.get_category_preferences("笔记本电脑")
        print(f"电子产品匹配: {electronics_prefs}")
        
        # 测试默认配置
        unknown_prefs = CreativeRenovationPrompts.get_category_preferences("未知类别")
        print(f"未知类别默认配置: {unknown_prefs}")
        assert "优势" in unknown_prefs
        
        print("类别偏好配置测试通过！")
    
    def test_condition_impact(self):
        """测试物品状态影响"""
        print(f"\n==== 测试物品状态影响 ====")
        
        for condition in ["全新", "八成新", "有磨损", "损坏"]:
            impact = CreativeRenovationPrompts.get_condition_impact(condition)
            print(f"{condition}: {impact}")
            assert "改造建议" in impact
            assert "难度调整" in impact
            assert "成本调整" in impact
            assert "注意事项" in impact
        
        print("物品状态影响测试通过！")
    
    @pytest.mark.asyncio
    async def test_generate_from_analysis(self, agent, sample_analysis_result):
        """测试从分析结果生成改造步骤"""
        print(f"\n==== 测试从分析结果生成改造步骤 ====")
        print(f"输入分析结果: {sample_analysis_result}")
        
        try:
            result = await agent.generate_from_analysis(sample_analysis_result)
            
            print(f"测试结果成功: {result.get('success')}")
            print(f"数据来源: {result.get('source')}")
            print(f"生成来源: {result.get('generation_source')}")
            
            assert isinstance(result, dict)
            assert "success" in result
            assert "source" in result
            assert result["source"] == "analysis_result"
            
            if result["success"]:
                print(f"\n--- 分析结果信息 ---")
                analysis = result.get("analysis_result", {})
                print(f"类别: {analysis.get('category')}")
                print(f"子类别: {analysis.get('sub_category')}")
                print(f"材质: {analysis.get('material')}")
                print(f"状态: {analysis.get('condition')}")
                print(f"关键词: {analysis.get('keywords')}")
                
                assert "renovation_plan" in result
                assert "analysis_result" in result
                
                renovation_plan = result["renovation_plan"]
                assert "project_title" in renovation_plan
                assert "steps" in renovation_plan
                
                print(f"\n--- 改造方案详情 ---")
                print(f"项目标题: {renovation_plan.get('project_title')}")
                print(f"项目描述: {renovation_plan.get('project_description')}")
                print(f"难度等级: {renovation_plan.get('difficulty_level')}")
                print(f"所需技能: {renovation_plan.get('required_skills')}")
                
                steps = renovation_plan.get("steps", [])
                print(f"改造步骤数量: {len(steps)}")
                
                for i, step in enumerate(steps[:3]):  # 只显示前3步
                    print(f"步骤{i+1}: {step.get('title')}")
                    print(f"  描述: {step.get('description')[:50]}...")
                    print(f"  工具: {step.get('tools_needed')}")
                    print(f"  材料: {step.get('materials_needed')}")
                    
                # 测试摘要功能
                summary = agent.get_step_summary(renovation_plan)
                print(f"\n--- 改造摘要 ---")
                print(f"概览: {summary}")
                
            else:
                print(f"测试失败: {result.get('error')}")
                
        finally:
            await agent.close()
    
    def test_validation_logic(self, sample_analysis_result):
        """测试输入验证逻辑"""
        print(f"\n==== 测试输入验证逻辑 ====")
        
        agent = CreativeRenovationAgent()
        
        # 测试空输入
        print("测试空输入...")
        import asyncio
        
        async def test_empty_input():
            result = await agent.generate_from_analysis(None)
            assert not result["success"]
            assert "分析结果为空" in result["error"]
            
            result = await agent.generate_from_analysis({})
            # 空字典应该被接受但可能导致后续处理问题
            print(f"空字典输入结果: {result.get('success')}")
        
        asyncio.run(test_empty_input())
        
        # 测试正常输入
        print("测试正常输入格式...")
        assert isinstance(sample_analysis_result, dict)
        assert "category" in sample_analysis_result
        assert "condition" in sample_analysis_result
        print("输入验证逻辑测试通过！")
    
    def test_summary_features(self, sample_analysis_result):
        """测试摘要功能"""
        print(f"\n==== 测试摘要功能 ====")
        
        # 创建一个示例改造方案用于测试
        sample_plan = CreativeRenovationPrompts.get_fallback_renovation_plan(
            category=sample_analysis_result["category"],
            condition=sample_analysis_result["condition"],
            description=sample_analysis_result["description"]
        )
        
        agent = CreativeRenovationAgent()
        
        # 测试步骤摘要
        summary = agent.get_step_summary(sample_plan)
        print(f"步骤摘要: {summary}")
        assert isinstance(summary, dict)
        
        # 测试详细概览
        overview = agent.get_detailed_overview(sample_plan)
        print(f"详细概览: {overview}")
        assert isinstance(overview, dict)
        
        # 测试文本摘要生成
        text_summary = agent.generate_summary_text(sample_plan)
        print(f"文本摘要: {text_summary}")
        assert isinstance(text_summary, str)
        assert len(text_summary) > 0
        
        print("摘要功能测试通过！")


async def simple_test():
    """简单快速测试"""
    print("\n" + "="*50)
    print("创意改造Agent - 简单测试")
    print("="*50)
    
    # 创建样例分析结果
    analysis_result = {
        "category": "家具",
        "sub_category": "桌子",
        "condition": "八成新",
        "description": "一张木质书桌，表面有轻微划痕",
        "material": "木质",
        "color": "棕色",
        "keywords": ["桌子", "木质", "家具"]
    }
    
    async with CreativeRenovationAgent() as agent:
        result = await agent.generate_from_analysis(analysis_result)
        
        if result["success"]:
            plan = result["renovation_plan"]
            print(f"✅ 改造方案生成成功!")
            print(f"项目: {plan.get('project_title')}")
            print(f"难度: {plan.get('difficulty_level')}")
            print(f"步骤数: {len(plan.get('steps', []))}")
            
            # 测试摘要
            summary = agent.get_step_summary(plan)
            print(f"摘要: {summary}")
            
        else:
            print(f"❌ 改造方案生成失败: {result.get('error')}")


if __name__ == "__main__":
    # 运行简单测试
    asyncio.run(simple_test()) 