"""
创意改造协调器Agent测试

测试协调器Agent的各种功能，包括完整方案生成、仅改造、仅视频搜索等模式
"""

import asyncio
import json
import logging
import time
import sys
from pathlib import Path
from typing import Dict, Any

import pytest

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from app.agents.creative_coordinator import CreativeCoordinatorAgent
from app.core.logger import app_logger
from app.models.creative_coordinator_models import CoordinatorResponse


def print_separator(title: str, width: int = 80):
    """打印分隔线"""
    print("\n" + "=" * width)
    print(f" {title} ".center(width))
    print("=" * width)


def print_subsection(title: str, width: int = 60):
    """打印子章节标题"""
    print("\n" + "-" * width)
    print(f" {title} ".center(width))
    print("-" * width)


def print_json(data: Any, title: str = None):
    """格式化打印JSON数据"""
    if title:
        print(f"\n【{title}】")
    print(json.dumps(data, ensure_ascii=False, indent=2))


def print_renovation_plan(plan: Dict[str, Any]):
    """打印改造方案详情"""
    print_subsection("改造方案详情")

    print(f"项目标题: {plan.get('project_title', 'N/A')}")
    print(f"项目描述: {plan.get('project_description', 'N/A')}")
    print(f"难度等级: {plan.get('difficulty_level', 'N/A')}")
    print(f"预计总时间: {plan.get('estimated_total_time', 'N/A')}")
    print(f"预计总成本: {plan.get('estimated_total_cost', 'N/A')}")

    # 打印所需技能
    skills = plan.get('required_skills', [])
    print(f"所需技能: {', '.join(skills) if skills else 'N/A'}")

    # 打印安全警告
    warnings = plan.get('safety_warnings', [])
    if warnings:
        print("安全注意事项:")
        for i, warning in enumerate(warnings, 1):
            print(f"  {i}. {warning}")

    # 打印改造步骤
    steps = plan.get('steps', [])
    print(f"\n改造步骤 (共{len(steps)}步):")
    for step in steps:
        print(f"\n步骤 {step.get('step_number', 'N/A')}: {step.get('title', 'N/A')}")
        print(f"  描述: {step.get('description', 'N/A')}")
        print(f"  预计用时: {step.get('estimated_time_minutes', 'N/A')} 分钟")
        print(f"  难度: {step.get('difficulty', 'N/A')}")

        tools = step.get('tools_needed', [])
        materials = step.get('materials_needed', [])
        print(f"  所需工具: {', '.join(tools) if tools else '无'}")
        print(f"  所需材料: {', '.join(materials) if materials else '无'}")


def print_videos(videos: list):
    """打印视频信息"""
    print_subsection("相关教程视频")

    if not videos:
        print("未找到相关视频")
        return

    print(f"找到 {len(videos)} 个相关视频:\n")

    for i, video in enumerate(videos, 1):
        print(f"{i}. {video.get('title', 'N/A')}")
        print(f"   UP主: {video.get('uploader', 'N/A')}")
        print(f"   时长: {video.get('duration', 'N/A')}")
        print(f"   播放量: {video.get('play_count', 'N/A')}")
        print(f"   链接: {video.get('url', 'N/A')}")

        description = video.get('description', '')
        if description:
            desc_preview = description[:50] + "..." if len(description) > 50 else description
            print(f"   简介: {desc_preview}")
        print()


def print_statistics(stats: Dict[str, Any]):
    """打印统计信息"""
    print_subsection("统计信息")

    print(f"改造步骤数: {stats.get('total_steps', 0)}")
    print(f"相关视频数: {stats.get('video_count', 0)}")
    print(f"包含改造方案: {'是' if stats.get('has_renovation_plan') else '否'}")
    print(f"包含视频教程: {'是' if stats.get('has_videos') else '否'}")
    print(f"组件成功率: {stats.get('components_success_rate', 0):.1%}")


@pytest.mark.asyncio
async def test_complete_solution():
    """测试完整解决方案生成"""
    print_separator("测试完整解决方案生成")

    # 准备测试数据
    analysis_result = {
        "category": "家具",
        "sub_category": "桌子",
        "condition": "八成新",
        "description": "一张旧木桌，表面有划痕但结构完好，桌腿稳固",
        "material": "木质",
        "color": "棕色",
        "keywords": ["桌子", "木质", "家具", "改造"],
        "special_features": "有抽屉，适合改造"
    }

    print("🔍 输入分析结果:")
    print_json(analysis_result)

    async with CreativeCoordinatorAgent() as coordinator:
        print("\n🚀 开始生成完整解决方案...")
        start_time = time.time()

        # 测试并行模式
        print("\n【并行处理模式】")
        result = await coordinator.generate_complete_solution(
            analysis_result=analysis_result,
            enable_parallel=True
        )

        end_time = time.time()
        processing_time = end_time - start_time

        print(f"⏱️ 处理时间: {processing_time:.2f} 秒")
        print(f"✅ 生成结果: {'成功' if result.success else '失败'}")
        
        if result.success:
            # 打印改造方案
            if result.renovation_plan:
                print_subsection("改造方案摘要")
                summary = result.renovation_plan.summary
                print(f"项目标题: {summary.title}")
                print(f"难度等级: {summary.difficulty}")
                print(f"总耗时: {summary.total_time_hours} 小时")
                print(f"预算范围: {summary.budget_range}")
                print(f"成本描述: {summary.cost_description}")
                print(f"所需技能: {', '.join(summary.required_skills)}")
                print(f"工具清单: {', '.join(summary.tools)}")
                print(f"材料清单: {', '.join(summary.materials)}")
                print(f"改造步骤总数: {summary.total_steps}")
                
                print_subsection("详细改造步骤")
                for i, step in enumerate(result.renovation_plan.steps, 1):
                    print(f"\n步骤 {i}: {step.title}")
                    print(f"  描述: {step.description}")
                    print(f"  预计用时: {step.estimated_time_minutes} 分钟")
                    print(f"  难度: {step.difficulty}")
                    print(f"  工具: {', '.join(step.tools) if step.tools else '无'}")
                    print(f"  材料: {', '.join(step.materials) if step.materials else '无'}")
            
            # 打印视频信息
            if result.videos:
                print_subsection("推荐视频")
                print(f"找到 {len(result.videos)} 个优质视频:\n")
                
                for i, video in enumerate(result.videos, 1):
                    print(f"{i}. {video.title}")
                    print(f"   UP主: {video.uploader}")
                    print(f"   时长: {video.duration}")
                    print(f"   播放量: {video.play_count}")
                    print(f"   评分: {video.score:.3f}")
                    print(f"   链接: {video.url}")
                    
                    description = video.description
                    if description:
                        desc_preview = description[:50] + "..." if len(description) > 50 else description
                        print(f"   简介: {desc_preview}")
                    print()
        
        else:
            print(f"❌ 错误信息: {result.error or 'N/A'}")

    return result


@pytest.mark.asyncio
async def test_component_status():
    """测试组件状态检查"""
    print_separator("测试组件状态检查")

    coordinator = CreativeCoordinatorAgent()

    print("🔍 初始状态:")
    status = coordinator.get_component_status()
    print_json(status)

    async with coordinator:
        print("\n🔍 初始化后状态:")
        status = coordinator.get_component_status()
        print_json(status)

    print("\n🔍 关闭后状态:")
    status = coordinator.get_component_status()


@pytest.mark.asyncio
async def test_error_handling():
    """测试错误处理"""
    print_separator("测试错误处理")

    # 测试无效输入
    print("🧪 测试无效输入...")

    async with CreativeCoordinatorAgent() as coordinator:
        # 测试空输入
        result = await coordinator.generate_complete_solution(None)
        print("空输入测试:")
        print(f"  成功: {result.success}")
        print(f"  错误: {result.error}")

        # 测试空字典
        result = await coordinator.generate_complete_solution({})
        print("\n空字典测试:")
        print(f"  成功: {result.success}")
        print(f"  错误: {result.error}")

        # 测试不完整的分析结果
        incomplete_analysis = {"category": "测试"}
        result = await coordinator.generate_complete_solution(incomplete_analysis)
        print("\n不完整分析结果测试:")
        print(f"  成功: {result.success}")
        print(f"  有改造方案: {result.renovation_plan is not None}")
        print(f"  有视频: {len(result.videos)}")


@pytest.mark.asyncio
async def test_performance_comparison():
    """测试性能对比"""
    print_separator("性能对比测试")

    analysis_result = {
        "category": "生活用品",
        "sub_category": "花瓶",
        "condition": "有磨损",
        "description": "一个陶瓷花瓶，底部有小裂纹",
        "material": "陶瓷",
        "color": "白色",
        "keywords": ["花瓶", "陶瓷", "装饰"]
    }

    async with CreativeCoordinatorAgent() as coordinator:
        # 测试并行模式
        print("🚀 测试并行处理模式...")
        start_time = time.time()

        result_parallel = await coordinator.generate_complete_solution(
            analysis_result=analysis_result,
            enable_parallel=True
        )

        parallel_time = time.time() - start_time

        # 测试串行模式
        print("\n🔄 测试串行处理模式...")
        start_time = time.time()

        result_sequential = await coordinator.generate_complete_solution(
            analysis_result=analysis_result,
            enable_parallel=False
        )

        sequential_time = time.time() - start_time

        # 对比结果
        print_subsection("性能对比结果")
        print(f"并行模式耗时: {parallel_time:.2f} 秒")
        print(f"串行模式耗时: {sequential_time:.2f} 秒")
        print(f"性能提升: {((sequential_time - parallel_time) / sequential_time * 100):.1f}%")

        print(f"\n并行模式成功: {result_parallel.success}")
        print(f"串行模式成功: {result_sequential.success}")
        print(f"并行模式视频数: {len(result_parallel.videos)}")
        print(f"串行模式视频数: {len(result_sequential.videos)}")


async def main():
    """主测试函数"""
    print_separator("创意改造协调器Agent 全面测试", 100)
    print("🧪 开始执行测试套件...")

    try:
        # 1. 测试完整解决方案生成
        await test_complete_solution()

        # 2. 测试组件状态
        await test_component_status()

        # 3. 测试错误处理
        await test_error_handling()

        # 4. 测试性能对比
        await test_performance_comparison()

        print_separator("测试完成", 100)
        print("🎉 所有测试已完成！")

    except Exception as e:
        print_separator("测试异常", 100)
        print(f"❌ 测试过程中发生异常: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    # 设置日志级别
    logging.basicConfig(level=logging.INFO)

    # 运行测试
    asyncio.run(main())
