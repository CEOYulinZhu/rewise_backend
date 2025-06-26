"""
改造方案概览提取服务测试

测试RenovationSummaryService的核心功能
"""

import pytest
from app.services.renovation_summary_service import RenovationSummaryService


class TestRenovationSummaryService:
    """改造方案概览提取服务测试类"""
    
    def test_extract_overview_basic(self):
        """测试基本概览提取功能"""
        print(f"\n==== 测试基本概览提取功能 ====")
        
        # 构造测试数据
        sample_renovation_plan = {
            "project_title": "旧书桌翻新改造",
            "project_description": "将旧书桌进行翻新改造",
            "difficulty_level": "中等",
            "estimated_cost_range": {
                "min_cost": 80,
                "max_cost": 150,
                "cost_description": "基础翻新材料"
            },
            "required_skills": ["木工基础", "涂装"],
            "safety_warnings": ["佩戴防护眼镜", "保持通风", "避免吸入粉尘"],
            "steps": [
                {
                    "step_number": 1,
                    "title": "清洁准备",
                    "description": "彻底清洁桌面",
                    "tools_needed": ["抹布", "清洁剂"],
                    "materials_needed": ["清洁用品"],
                    "estimated_time_minutes": 30,
                    "difficulty": "简单"
                },
                {
                    "step_number": 2,
                    "title": "打磨处理",
                    "description": "打磨桌面划痕",
                    "tools_needed": ["砂纸", "电动砂光机"],
                    "materials_needed": ["不同粗细砂纸"],
                    "estimated_time_minutes": 90,
                    "difficulty": "中等"
                },
                {
                    "step_number": 3,
                    "title": "重新涂装",
                    "description": "涂刷新的漆面",
                    "tools_needed": ["刷子", "滚筒"],
                    "materials_needed": ["底漆", "面漆"],
                    "estimated_time_minutes": 120,
                    "difficulty": "中等"
                }
            ],
            "final_result": {
                "description": "焕然一新的书桌",
                "usage_scenarios": ["办公学习", "装饰展示"],
                "maintenance_tips": ["定期清洁", "避免重压"]
            },
            "alternative_ideas": [
                {
                    "title": "简化版翻新",
                    "description": "仅清洁和保养"
                }
            ]
        }
        
        # 提取概览
        overview = RenovationSummaryService.extract_overview(sample_renovation_plan)
        
        print(f"概览提取结果:")
        print(f"项目标题: {overview.get('project_title')}")
        print(f"整体难度: {overview.get('overall_difficulty')}")
        
        # 验证基本信息
        assert overview["project_title"] == "旧书桌翻新改造"
        assert overview["overall_difficulty"] == "中等"
        assert overview["has_safety_warnings"] == True
        assert overview["safety_warnings_count"] == 3
        assert overview["has_alternative_ideas"] == True
        
        # 验证成本信息
        cost_summary = overview["cost_summary"]
        print(f"\n--- 成本信息 ---")
        print(f"最低成本: {cost_summary['min_cost']}元")
        print(f"最高成本: {cost_summary['max_cost']}元")
        print(f"平均成本: {cost_summary['average_cost']}元")
        print(f"成本等级: {cost_summary['cost_level']}")
        
        assert cost_summary["min_cost"] == 80
        assert cost_summary["max_cost"] == 150
        assert cost_summary["average_cost"] == 115.0
        assert cost_summary["cost_level"] == "中等成本"
        
        # 验证时间信息
        time_summary = overview["time_summary"]
        print(f"\n--- 时间信息 ---")
        print(f"总分钟数: {time_summary['total_minutes']}")
        print(f"总小时数: {time_summary['total_hours']}")
        print(f"时间范围: {time_summary['time_range']}")
        print(f"时间等级: {time_summary['time_level']}")
        
        assert time_summary["total_minutes"] == 240  # 30+90+120
        assert time_summary["total_hours"] == 4.0
        assert time_summary["time_level"] == "较长耗时"
        
        # 验证步骤信息
        steps_summary = overview["steps_summary"]
        print(f"\n--- 步骤信息 ---")
        print(f"总步骤数: {steps_summary['total_steps']}")
        print(f"难度分布: {steps_summary['difficulty_distribution']}")
        print(f"复杂度评分: {steps_summary['complexity_score']}")
        
        assert steps_summary["total_steps"] == 3
        assert steps_summary["difficulty_distribution"]["简单"] == 1
        assert steps_summary["difficulty_distribution"]["中等"] == 2
        
        # 验证资源信息
        resources_summary = overview["resources_summary"]
        print(f"\n--- 资源信息 ---")
        print(f"工具总数: {resources_summary['total_tools']}")
        print(f"材料总数: {resources_summary['total_materials']}")
        print(f"工具列表: {resources_summary['tools_list']}")
        print(f"材料列表: {resources_summary['materials_list']}")
        print(f"资源复杂度: {resources_summary['resource_complexity']}")
        
        assert resources_summary["total_tools"] >= 4  # 去重后的工具数
        assert resources_summary["total_materials"] >= 4  # 去重后的材料数
        assert "抹布" in resources_summary["tools_list"]
        assert "底漆" in resources_summary["materials_list"]
        
        # 验证难度分析
        difficulty_analysis = overview["difficulty_analysis"]
        print(f"\n--- 难度分析 ---")
        print(f"复杂度评分: {difficulty_analysis['complexity_score']}")
        print(f"新手友好: {difficulty_analysis['beginner_friendly']}")
        print(f"技能要求: {difficulty_analysis['skill_requirements']}")
        
        assert "beginner_friendly" in difficulty_analysis
        assert difficulty_analysis["skill_count"] == 2
        
        print("基本概览提取测试通过！")
    
    def test_time_parsing(self):
        """测试时间解析功能"""
        print(f"\n==== 测试时间解析功能 ====")
        
        # 测试不同时间格式的解析
        test_cases = [
            ("30分钟", 30),
            ("1小时", 60),
            ("1.5小时", 90),
            ("1-2小时", 90),
            ("45-60分钟", 52.5),
            ("", 0),
            ("2小时30分钟", 150)
        ]
        
        for time_str, expected_minutes in test_cases:
            result = RenovationSummaryService._parse_time_string(time_str)
            print(f"'{time_str}' -> {result}分钟 (期望: {expected_minutes})")
            assert abs(result - expected_minutes) <= 1  # 允许1分钟误差
        
        print("时间解析功能测试通过！")
    
    def test_cost_classification(self):
        """测试成本分类功能"""
        print(f"\n==== 测试成本分类功能 ====")
        
        test_cases = [
            (30, "低成本"),
            (100, "中等成本"),
            (200, "高成本"),
            (500, "昂贵")
        ]
        
        for cost, expected_level in test_cases:
            result = RenovationSummaryService._classify_cost_level(cost)
            print(f"{cost}元 -> {result} (期望: {expected_level})")
            assert result == expected_level
        
        print("成本分类功能测试通过！")
    
    def test_time_classification(self):
        """测试时间分类功能"""
        print(f"\n==== 测试时间分类功能 ====")
        
        test_cases = [
            (0.5, "快速"),
            (2, "中等耗时"),
            (5, "较长耗时"),
            (8, "长时间项目")
        ]
        
        for hours, expected_level in test_cases:
            result = RenovationSummaryService._classify_time_level(hours)
            print(f"{hours}小时 -> {result} (期望: {expected_level})")
            assert result == expected_level
        
        print("时间分类功能测试通过！")
    
    def test_tool_categorization(self):
        """测试工具分类功能"""
        print(f"\n==== 测试工具分类功能 ====")
        
        test_tools = ["螺丝刀", "电动砂光机", "尺子", "抹布", "特殊工具"]
        categories = RenovationSummaryService._categorize_tools(test_tools)
        
        print(f"工具分类结果: {categories}")
        
        assert "基础工具" in categories
        assert "电动工具" in categories
        assert "测量工具" in categories
        assert "清洁工具" in categories
        assert "其他工具" in categories
        
        assert "螺丝刀" in categories["基础工具"]
        assert "电动砂光机" in categories["电动工具"]
        assert "尺子" in categories["测量工具"]
        assert "抹布" in categories["清洁工具"]
        assert "特殊工具" in categories["其他工具"]
        
        print("工具分类功能测试通过！")
    
    def test_resource_complexity_assessment(self):
        """测试资源复杂度评估"""
        print(f"\n==== 测试资源复杂度评估 ====")
        
        test_cases = [
            ({"锤子", "螺丝刀"}, {"钉子"}, "简单"),        # 3个资源
            ({"锤子", "螺丝刀", "尺子", "刷子"}, {"钉子", "油漆", "砂纸"}, "中等"),  # 7个资源
            (set(f"工具{i}" for i in range(8)), set(f"材料{i}" for i in range(5)), "复杂"),  # 13个资源
            (set(f"工具{i}" for i in range(10)), set(f"材料{i}" for i in range(8)), "非常复杂")  # 18个资源
        ]
        
        for tools, materials, expected_level in test_cases:
            result = RenovationSummaryService._assess_resource_complexity(tools, materials)
            print(f"{len(tools)}工具+{len(materials)}材料 -> {result} (期望: {expected_level})")
            assert result == expected_level
        
        print("资源复杂度评估测试通过！")
    
    def test_summary_text_generation(self):
        """测试摘要文本生成"""
        print(f"\n==== 测试摘要文本生成 ====")
        
        # 使用简化的概览数据
        overview = {
            "project_title": "测试改造项目",
            "overall_difficulty": "中等",
            "time_summary": {
                "time_range": "2.5小时",
            },
            "steps_summary": {
                "total_steps": 3
            },
            "cost_summary": {
                "min_cost": 50,
                "max_cost": 100
            },
            "resources_summary": {
                "total_tools": 5,
                "total_materials": 3
            },
            "difficulty_analysis": {
                "beginner_friendly": True
            }
        }
        
        summary_text = RenovationSummaryService.generate_summary_text(overview)
        
        print(f"生成的摘要文本:")
        print(summary_text)
        
        assert "测试改造项目" in summary_text
        assert "中等" in summary_text
        assert "2.5小时" in summary_text
        assert "3步" in summary_text
        assert "50-100元" in summary_text
        assert "适合新手" in summary_text
        
        print("摘要文本生成测试通过！")
    
    def test_legacy_format_compatibility(self):
        """测试旧格式兼容性"""
        print(f"\n==== 测试旧格式兼容性 ====")
        
        # 构造包含旧格式字段的数据
        old_format_plan = {
            "project_title": "兼容性测试",
            "difficulty_level": "简单",
            "estimated_total_cost": "30-50元",  # 旧格式
            "steps": [
                {
                    "step_number": 1,
                    "title": "测试步骤",
                    "description": "测试描述",
                    "tools_needed": ["工具1"],
                    "materials_needed": ["材料1"],
                    "estimated_time": "30分钟",  # 旧格式
                    "difficulty": "简单"
                }
            ],
            "final_result": {
                "description": "测试结果"
            }
        }
        
        # 应该能够正常处理，不报错
        overview = RenovationSummaryService.extract_overview(old_format_plan)
        
        assert overview["project_title"] == "兼容性测试"
        assert overview["overall_difficulty"] == "简单"
        
        # 时间应该被正确解析
        time_summary = overview["time_summary"]
        assert time_summary["total_minutes"] == 30
        
        print("旧格式兼容性测试通过！")


if __name__ == "__main__":
    # 运行简单测试
    def simple_test():
        print("=" * 60)
        print("改造方案概览提取服务 - 功能测试")
        print("=" * 60)
        
        # 创建测试样例
        sample_plan = {
            "project_title": "老木椅翻新",
            "difficulty_level": "中等",
            "estimated_cost_range": {
                "min_cost": 60,
                "max_cost": 120,
                "cost_description": "翻新材料"
            },
            "steps": [
                {
                    "step_number": 1,
                    "title": "拆解清洁",
                    "tools_needed": ["螺丝刀", "抹布"],
                    "materials_needed": ["清洁剂"],
                    "estimated_time_minutes": 45,
                    "difficulty": "简单"
                },
                {
                    "step_number": 2,
                    "title": "修复涂装",
                    "tools_needed": ["刷子", "砂纸"],
                    "materials_needed": ["木蜡", "油漆"],
                    "estimated_time_minutes": 90,
                    "difficulty": "中等"
                }
            ],
            "safety_warnings": ["注意通风"],
            "final_result": {"description": "翻新椅子"}
        }
        
        # 提取概览
        overview = RenovationSummaryService.extract_overview(sample_plan)
        
        print(f"\n📋 项目: {overview['project_title']}")
        print(f"🎯 难度: {overview['overall_difficulty']}")
        print(f"⏱️ 时间: {overview['time_summary']['time_range']}")
        print(f"💰 成本: {overview['cost_summary']['min_cost']}-{overview['cost_summary']['max_cost']}元")
        print(f"🔧 资源: {overview['resources_summary']['total_tools']}工具+{overview['resources_summary']['total_materials']}材料")
        
        # 生成文本摘要
        summary_text = RenovationSummaryService.generate_summary_text(overview)
        print(f"\n📝 文本摘要:\n{summary_text}")
        
        print(f"\n✅ 概览服务测试完成")
    
    simple_test() 