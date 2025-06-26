"""
创意改造步骤Agent测试

测试创意改造Agent的核心功能
"""

import pytest
import asyncio
from pathlib import Path

from app.agents.creative_renovation.agent import CreativeRenovationAgent
from app.prompts.creative_renovation_prompts import CreativeRenovationPrompts


class TestCreativeRenovationAgent:
    """创意改造Agent测试类"""
    
    @pytest.fixture
    def agent(self):
        """创建Agent实例"""
        return CreativeRenovationAgent()
    
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
    async def test_generate_from_text(self, agent):
        """测试从文字描述生成改造步骤"""
        text_description = "一张旧书桌，木质材料，表面有划痕但结构完好，想要翻新一下"
        
        print(f"\n==== 测试从文字描述生成改造步骤 ====")
        print(f"输入文字描述: {text_description}")
        
        try:
            result = await agent.generate_from_text(text_description)
            
            print(f"测试结果成功: {result.get('success')}")
            print(f"数据来源: {result.get('source')}")
            print(f"生成来源: {result.get('generation_source')}")
            
            assert isinstance(result, dict)
            assert "success" in result
            assert "source" in result
            assert result["source"] == "text"
            
            if result["success"]:
                print(f"\n--- 物品分析结果 ---")
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
                
                print(f"\n--- 创意改造方案 ---")
                print(f"项目标题: {renovation_plan.get('project_title')}")
                print(f"项目描述: {renovation_plan.get('project_description')}")
                print(f"难度等级: {renovation_plan.get('difficulty_level')}")
                
                # 适配新的成本格式
                cost_range = renovation_plan.get('estimated_cost_range', {})
                if isinstance(cost_range, dict):
                    print(f"预计成本: {cost_range.get('min_cost')}-{cost_range.get('max_cost')}元")
                
                print(f"所需技能: {renovation_plan.get('required_skills')}")
                
                # 安全警告
                safety_warnings = renovation_plan.get("safety_warnings", [])
                print(f"\n--- 安全警告 ({len(safety_warnings)}条) ---")
                for i, warning in enumerate(safety_warnings):
                    print(f"{i+1}. {warning}")
                
                # 详细步骤
                steps = renovation_plan.get("steps", [])
                print(f"\n--- 详细改造步骤 ({len(steps)}步) ---")
                for step in steps:
                    print(f"\n步骤 {step.get('step_number')}: {step.get('title')}")
                    print(f"  描述: {step.get('description')}")
                    print(f"  所需工具: {', '.join(step.get('tools_needed', []))}")
                    print(f"  所需材料: {', '.join(step.get('materials_needed', []))}")
                    
                    # 适配新的时间格式
                    if 'estimated_time_minutes' in step:
                        print(f"  预计耗时: {step.get('estimated_time_minutes')}分钟")
                    else:
                        print(f"  预计耗时: {step.get('estimated_time')}")
                    
                    print(f"  难度: {step.get('difficulty')}")
                    
                    tips = step.get('tips', [])
                    if tips:
                        print(f"  小贴士: {', '.join(tips)}")
                    
                    if step.get('image_description'):
                        print(f"  配图说明: {step.get('image_description')}")
                
                # 最终结果
                final_result = renovation_plan.get("final_result", {})
                print(f"\n--- 最终结果 ---")
                print(f"成品描述: {final_result.get('description')}")
                print(f"使用场景: {final_result.get('usage_scenarios')}")
                print(f"保养建议: {final_result.get('maintenance_tips')}")
                
                # 替代方案
                alternative_ideas = renovation_plan.get("alternative_ideas", [])
                if alternative_ideas:
                    print(f"\n--- 替代方案 ({len(alternative_ideas)}个) ---")
                    for idea in alternative_ideas:
                        print(f"- {idea.get('title')}: {idea.get('description')}")
                
                # 测试新的摘要功能
                summary = agent.get_step_summary(renovation_plan)
                print(f"\n--- 改造方案摘要 ---")
                print(f"总步骤数: {summary.get('total_steps')}")
                print(f"总耗时: {summary.get('total_hours')}小时 ({summary.get('total_minutes')}分钟)")
                print(f"时间范围: {summary.get('time_range')}")
                print(f"所需工具: {len(summary.get('required_tools', []))}种")
                print(f"所需材料: {len(summary.get('required_materials', []))}种")
                print(f"安全警告数: {summary.get('safety_warnings_count')}")
                print(f"有替代方案: {summary.get('has_alternative_ideas')}")
                print(f"新手友好: {summary.get('beginner_friendly')}")
                print(f"复杂度评分: {summary.get('complexity_score')}")
                
                # 测试新的详细概览功能
                detailed_overview = agent.get_detailed_overview(renovation_plan)
                print(f"\n--- 详细概览信息 ---")
                print(f"成本等级: {detailed_overview.get('cost_summary', {}).get('cost_level')}")
                print(f"时间等级: {detailed_overview.get('time_summary', {}).get('time_level')}")
                print(f"资源复杂度: {detailed_overview.get('resources_summary', {}).get('resource_complexity')}")
                
                # 测试文本摘要生成
                summary_text = agent.generate_summary_text(renovation_plan)
                print(f"\n--- 文本摘要 ---")
                print(summary_text)
                
            else:
                print(f"测试失败: {result.get('error')}")
                
        finally:
            await agent.close()
    
    @pytest.mark.asyncio  
    async def test_generate_from_analysis(self, agent):
        """测试从分析结果生成改造步骤"""
        analysis_result = {
            "category": "家具",
            "sub_category": "椅子",
            "condition": "八成新",
            "brand": "宜家",
            "material": "木质",
            "color": "白色",
            "keywords": ["椅子", "木质", "白色"],
            "description": "一把白色木质椅子，有轻微磨损",
            "special_features": "可拆卸靠背"
        }
        
        print(f"\n==== 测试从分析结果生成改造步骤 ====")
        print(f"输入分析结果: {analysis_result}")
        
        try:
            result = await agent.generate_from_analysis(analysis_result)
            
            print(f"测试结果成功: {result.get('success')}")
            print(f"数据来源: {result.get('source')}")
            print(f"生成来源: {result.get('generation_source')}")
            
            assert isinstance(result, dict)
            assert "success" in result
            assert "source" in result
            assert result["source"] == "analysis_result"
            
            if result["success"]:
                assert "renovation_plan" in result
                renovation_plan = result["renovation_plan"]
                assert "project_title" in renovation_plan
                assert "steps" in renovation_plan
                
                print(f"\n--- 创意改造方案 ---")
                print(f"项目标题: {renovation_plan.get('project_title')}")
                print(f"难度等级: {renovation_plan.get('difficulty_level')}")
                
                # 适配新的成本格式
                cost_range = renovation_plan.get('estimated_cost_range', {})
                if isinstance(cost_range, dict):
                    print(f"预计成本: {cost_range.get('min_cost')}-{cost_range.get('max_cost')}元")
                
                # 改造步骤
                steps = renovation_plan.get("steps", [])
                print(f"\n--- 改造步骤概览 ({len(steps)}步) ---")
                for step in steps:
                    time_info = f"{step.get('estimated_time_minutes', '未知')}分钟" if 'estimated_time_minutes' in step else step.get('estimated_time', '未知')
                    print(f"步骤 {step.get('step_number')}: {step.get('title')} ({step.get('difficulty')}, {time_info})")
                
                # 测试验证功能
                is_valid = agent._validate_renovation_plan(renovation_plan)
                print(f"\n改造方案格式验证: {'通过' if is_valid else '失败'}")
                assert is_valid == True
                
                # 测试新的概览功能
                detailed_overview = agent.get_detailed_overview(renovation_plan)
                print(f"\n--- 详细概览统计 ---")
                print(f"总耗时: {detailed_overview.get('time_summary', {}).get('total_minutes')}分钟")
                print(f"工具分类: {detailed_overview.get('resources_summary', {}).get('tool_categories', {})}")
                
            else:
                print(f"测试失败: {result.get('error')}")
                
        finally:
            await agent.close()
    
    def test_validation_logic(self):
        """测试改造方案验证逻辑"""
        print(f"\n==== 测试改造方案验证逻辑 ====")
        
        agent = CreativeRenovationAgent()
        
        # 有效的改造方案 - 新格式
        valid_plan = {
            "project_title": "旧椅子翻新改造",
            "project_description": "将旧椅子进行翻新改造",
            "difficulty_level": "中等",
            "estimated_cost_range": {
                "min_cost": 80,
                "max_cost": 120,
                "cost_description": "翻新材料成本"
            },
            "required_skills": ["木工基础", "涂装"],
            "safety_warnings": ["佩戴防护眼镜", "保持通风"],
            "steps": [
                {
                    "step_number": 1,
                    "title": "清洁准备",
                    "description": "清洁椅子表面",
                    "tools_needed": ["抹布", "清洁剂"],
                    "materials_needed": ["清洁用品"],
                    "estimated_time_minutes": 30,
                    "difficulty": "简单",
                    "tips": ["彻底清洁"]
                }
            ],
            "final_result": {
                "description": "焕然一新的椅子",
                "usage_scenarios": ["客厅使用"],
                "maintenance_tips": ["定期清洁"]
            }
        }
        
        validation_result = agent._validate_renovation_plan(valid_plan)
        print(f"有效方案验证: {validation_result}")
        assert validation_result == True
        
        # 无效的改造方案 - 缺少必要字段
        invalid_plan = {
            "project_title": "改造项目",
            "steps": [
                {
                    "step_number": 1,
                    "title": "步骤1"
                    # 缺少必要字段
                }
            ]
            # 缺少其他必要字段
        }
        
        validation_result_invalid = agent._validate_renovation_plan(invalid_plan)
        print(f"无效方案验证: {validation_result_invalid}")
        assert validation_result_invalid == False
        
        print("改造方案验证逻辑测试通过！")
    
    def test_new_summary_features(self):
        """测试新的概览功能"""
        print(f"\n==== 测试新的概览功能 ====")
        
        agent = CreativeRenovationAgent()
        
        # 构造测试改造方案
        test_plan = {
            "project_title": "测试改造项目",
            "project_description": "测试用改造方案",
            "difficulty_level": "中等",
            "estimated_cost_range": {
                "min_cost": 60,
                "max_cost": 100,
                "cost_description": "测试成本"
            },
            "required_skills": ["基础技能"],
            "safety_warnings": ["注意安全"],
            "steps": [
                {
                    "step_number": 1,
                    "title": "准备工作",
                    "description": "准备所需工具和材料",
                    "tools_needed": ["锤子", "螺丝刀"],
                    "materials_needed": ["钉子", "木板"],
                    "estimated_time_minutes": 45,
                    "difficulty": "简单"
                },
                {
                    "step_number": 2,
                    "title": "主要工作",
                    "description": "进行主要改造工作",
                    "tools_needed": ["电钻", "砂纸"],
                    "materials_needed": ["油漆", "刷子"],
                    "estimated_time_minutes": 90,
                    "difficulty": "中等"
                }
            ],
            "final_result": {
                "description": "改造完成的物品",
                "usage_scenarios": ["日常使用"],
                "maintenance_tips": ["定期维护"]
            },
            "alternative_ideas": [
                {
                    "title": "简化方案",
                    "description": "更简单的改造方法"
                }
            ]
        }
        
        # 测试详细概览
        detailed_overview = agent.get_detailed_overview(test_plan)
        print(f"--- 详细概览测试 ---")
        print(f"项目标题: {detailed_overview.get('project_title')}")
        print(f"总耗时: {detailed_overview.get('time_summary', {}).get('total_minutes')}分钟")
        print(f"成本范围: {detailed_overview.get('cost_summary', {}).get('min_cost')}-{detailed_overview.get('cost_summary', {}).get('max_cost')}元")
        print(f"复杂度评分: {detailed_overview.get('difficulty_analysis', {}).get('complexity_score')}")
        print(f"新手友好: {detailed_overview.get('difficulty_analysis', {}).get('beginner_friendly')}")
        
        # 测试文本摘要
        summary_text = agent.generate_summary_text(test_plan)
        print(f"\n--- 文本摘要测试 ---")
        print(summary_text)
        
        # 验证概览结果
        assert detailed_overview["project_title"] == "测试改造项目"
        assert detailed_overview["time_summary"]["total_minutes"] == 135  # 45+90
        assert detailed_overview["cost_summary"]["min_cost"] == 60
        assert detailed_overview["cost_summary"]["max_cost"] == 100
        assert detailed_overview["steps_summary"]["total_steps"] == 2
        assert detailed_overview["resources_summary"]["total_tools"] == 4  # 去重后的工具数
        assert detailed_overview["resources_summary"]["total_materials"] == 4  # 去重后的材料数
        
        print("新的概览功能测试通过！")


if __name__ == "__main__":
    # 运行简单测试
    async def simple_test():
        print("=" * 60)
        print("创意改造Agent - 简单功能测试")
        print("=" * 60)
        
        agent = CreativeRenovationAgent()
        
        try:
            # 测试文字描述改造步骤生成
            text_description = "一张旧的实木餐桌，表面有一些划痕和磨损，但整体结构完好"
            print(f"\n📝 测试输入: {text_description}")
            print("正在调用AI模型生成改造步骤...")
            
            result = await agent.generate_from_text(text_description)
            
            print(f"\n✅ 测试结果: {'成功' if result.get('success') else '失败'}")
            print(f"🔄 生成来源: {result.get('generation_source', '未知')}")
            
            if result.get('success'):
                # 显示分析结果
                analysis = result.get('analysis_result', {})
                print(f"\n📊 物品分析:")
                print(f"   类别: {analysis.get('category')}")
                print(f"   状态: {analysis.get('condition')}")
                print(f"   材质: {analysis.get('material')}")
                
                # 显示改造方案
                renovation = result.get('renovation_plan', {})
                print(f"\n🎨 改造方案:")
                print(f"   项目: {renovation.get('project_title')}")
                print(f"   难度: {renovation.get('difficulty_level')}")
                
                # 显示成本信息
                cost_range = renovation.get('estimated_cost_range', {})
                if isinstance(cost_range, dict):
                    print(f"   成本: {cost_range.get('min_cost')}-{cost_range.get('max_cost')}元")
                
                # 显示步骤概览
                steps = renovation.get('steps', [])
                print(f"\n🔨 改造步骤 ({len(steps)}步):")
                for step in steps:
                    time_info = f"{step.get('estimated_time_minutes')}分钟" if 'estimated_time_minutes' in step else step.get('estimated_time', '未知')
                    print(f"   {step.get('step_number')}. {step.get('title')} ({time_info})")
                
                # 显示新的摘要功能
                summary = agent.get_step_summary(renovation)
                print(f"\n📋 方案摘要:")
                print(f"   总耗时: {summary.get('total_hours')}小时")
                print(f"   所需工具: {len(summary.get('required_tools', []))}种")
                print(f"   所需材料: {len(summary.get('required_materials', []))}种")
                print(f"   新手友好: {'是' if summary.get('beginner_friendly') else '否'}")
                
                # 显示文本摘要
                summary_text = agent.generate_summary_text(renovation)
                print(f"\n📝 简洁摘要:")
                print(summary_text)
                
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