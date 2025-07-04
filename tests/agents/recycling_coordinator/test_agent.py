"""
回收捐赠总协调器Agent测试

测试协调器Agent的各种功能，包括并行/串行处理、错误处理等
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

from app.agents.recycling_coordinator import RecyclingCoordinatorAgent
from app.core.logger import app_logger
from app.models.recycling_coordinator_models import RecyclingCoordinatorResponse


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


def print_ai_recommendation_process(platform_recommendation):
    """打印AI推荐过程的详细信息"""
    if not platform_recommendation or not platform_recommendation.success:
        return
    
    print_subsection("AI推荐过程详细分析")
    
    # 1. RAG检索阶段
    if platform_recommendation.rag_metadata:
        metadata = platform_recommendation.rag_metadata
        print("🔍 第一阶段: RAG知识检索")
        print(f"  检索到候选平台: {metadata.get('total_results', 0)}个")
        print(f"  相似度阈值: {metadata.get('similarity_threshold', 0)}")
        print(f"  检索模式: {metadata.get('search_mode', 'unknown')}")
    
    # 2. 平台详细数据
    if platform_recommendation.platform_details:
        print(f"\n📊 第二阶段: 平台基础数据加载")
        print(f"  加载平台详细数据: {len(platform_recommendation.platform_details)}个")
        for i, platform in enumerate(platform_recommendation.platform_details, 1):
            print(f"    {i}. {platform.get('platform_name', 'N/A')}")
            print(f"       类别匹配: {platform.get('focus_categories', [])}")
            print(f"       特色标签: {platform.get('tags', [])}")
    
    # 3. AI推荐生成
    if platform_recommendation.ai_recommendations:
        recommendations = platform_recommendation.ai_recommendations.recommendations
        print(f"\n🤖 第三阶段: AI智能推荐生成")
        print(f"  生成个性化推荐: {len(recommendations)}个")
        
        for i, rec in enumerate(recommendations, 1):
            print(f"\n    推荐 {i}: {rec.platform_name}")
            print(f"    ├─ 适合度评分: {rec.suitability_score}/10")
            print(f"    ├─ 优势分析 ({len(rec.pros)}项): {rec.pros}")
            print(f"    ├─ 劣势分析 ({len(rec.cons)}项): {rec.cons}")
            print(f"    └─ 推荐理由长度: {len(rec.recommendation_reason)}字符")
            
            # 分析推荐理由的关键词
            reason = rec.recommendation_reason.lower()
            keywords = []
            if '用户' in reason:
                keywords.append('用户群体')
            if '交易' in reason:
                keywords.append('交易便利')
            if '价格' in reason or '费用' in reason:
                keywords.append('价格因素')
            if '保障' in reason or '验证' in reason:
                keywords.append('服务保障')
            if '专业' in reason:
                keywords.append('专业性')
            
            if keywords:
                print(f"       推荐理由关键因素: {', '.join(keywords)}")
    
    # 4. AI原始响应分析
    if platform_recommendation.ai_raw_response:
        raw_response = platform_recommendation.ai_raw_response
        print(f"\n🔤 第四阶段: AI响应解析")
        print(f"  原始响应长度: {len(raw_response)}字符")
        
        # 分析响应格式
        if '```json' in raw_response:
            print("  响应格式: JSON代码块格式")
        elif raw_response.strip().startswith('{'):
            print("  响应格式: 纯JSON格式")
        else:
            print("  响应格式: 文本格式")
        
        # 检查JSON结构
        if '"recommendations"' in raw_response:
            print("  ✅ 包含推荐结构")
        if '"platform_name"' in raw_response:
            print("  ✅ 包含平台名称")
        if '"suitability_score"' in raw_response:
            print("  ✅ 包含适合度评分")
        if '"pros"' in raw_response and '"cons"' in raw_response:
            print("  ✅ 包含优劣势分析")
        if '"recommendation_reason"' in raw_response:
            print("  ✅ 包含推荐理由")


def print_location_recommendations(location_recommendation):
    """打印地点推荐详情"""
    if not location_recommendation:
        print("❌ 无地点推荐数据")
        return
    
    print_subsection("回收地点推荐详情")
    print(f"✅ 推荐成功: {location_recommendation.success}")
    print(f"📍 回收类型: {location_recommendation.recycling_type}")
    print(f"🏠 地点数量: {len(location_recommendation.locations)}")
    
    if location_recommendation.error:
        print(f"❌ 错误信息: {location_recommendation.error}")
    
    # 显示前5个地点
    if location_recommendation.locations:
        print("\n推荐回收地点 (前5个):")
        for i, location in enumerate(location_recommendation.locations[:5], 1):
            distance_text = f"{location.distance_meters}米" if location.distance_meters else "距离未知"
            print(f"{i}. {location.name}")
            print(f"   地址: {location.address}")
            print(f"   距离: {distance_text}")
            if location.tel:
                print(f"   电话: {location.tel}")
            print()


def print_platform_recommendations(platform_recommendation):
    """打印平台推荐详情"""
    if not platform_recommendation:
        print("❌ 无平台推荐数据")
        return
    
    print_subsection("平台推荐详情")
    print(f"✅ 推荐成功: {platform_recommendation.success}")
    
    if platform_recommendation.error:
        print(f"❌ 错误信息: {platform_recommendation.error}")
        return
    
    # 打印AI推荐结果
    if platform_recommendation.ai_recommendations:
        recommendations = platform_recommendation.ai_recommendations.recommendations
        print(f"🏪 AI推荐平台数量: {len(recommendations)}")
        
        print("\n🤖 AI推荐平台详情:")
        for i, rec in enumerate(recommendations, 1):
            print(f"  {i}. 【{rec.platform_name}】 (适合度评分: {rec.suitability_score}/10)")
            print(f"     ✅ 优势: {', '.join(rec.pros)}")
            print(f"     ❌ 劣势: {', '.join(rec.cons)}")
            print(f"     💡 推荐理由: {rec.recommendation_reason}")
            print()
    
    # 打印平台详细数据
    if platform_recommendation.platform_details:
        print("📊 推荐平台详细数据:")
        for i, platform in enumerate(platform_recommendation.platform_details, 1):
            print(f"  {i}. 平台: {platform.get('platform_name', 'N/A')}")
            print(f"     图标: {platform.get('platform_icon', 'N/A')}")
            print(f"     描述: {platform.get('description', 'N/A')}")
            print(f"     主要品类: {', '.join(platform.get('focus_categories', []))}")
            print(f"     平台特色: {', '.join(platform.get('tags', []))}")
            print(f"     交易模式: {platform.get('transaction_model', 'N/A')}")
            
            # 用户数据
            user_data = platform.get('user_data', {})
            if user_data:
                print(f"     用户数据:")
                for key, value in user_data.items():
                    print(f"       {key}: {value}")
            
            # 用户评分
            rating = platform.get('rating', {})
            if rating:
                print(f"     用户评分:")
                for store, score in rating.items():
                    print(f"       {store}: {score}")
            print()
    
    # 显示RAG元数据
    if platform_recommendation.rag_metadata:
        print("🔍 RAG检索元数据:")
        metadata = platform_recommendation.rag_metadata
        print(f"  检索结果总数: {metadata.get('total_results', 0)}")
        print(f"  相似度阈值: {metadata.get('similarity_threshold', 0)}")
        print(f"  搜索模式: {metadata.get('search_mode', 'unknown')}")
    
    # 打印AI原始响应（如果有）
    if platform_recommendation.ai_raw_response:
        print("\n🔤 AI模型原始响应 (截取前200字符):")
        raw_response = platform_recommendation.ai_raw_response
        preview = raw_response[:200] + "..." if len(raw_response) > 200 else raw_response
        print(f"  {preview}")
    
    # 打印AI推荐过程详细分析
    print_ai_recommendation_process(platform_recommendation)


def print_processing_summary(response: RecyclingCoordinatorResponse):
    """打印处理摘要"""
    print_subsection("处理摘要")
    summary = response.get_processing_summary()
    
    print(f"✅ 处理成功: {summary.get('success')}")
    print(f"📍 包含地点推荐: {summary.get('has_locations')}")
    print(f"🏪 包含平台推荐: {summary.get('has_platforms')}")
    print(f"♻️ 回收类型: {summary.get('recycling_type', '未知')}")
    
    if summary.get('location_count'):
        print(f"🏠 地点总数: {summary.get('location_count')}")
        print(f"📍 附近地点数: {summary.get('nearby_location_count')}")
    
    if summary.get('platform_count'):
        print(f"🏪 平台总数: {summary.get('platform_count')}")
        
        top_platform = summary.get('top_platform')
        if top_platform:
            print(f"⭐ 最佳平台: {top_platform.get('name')} (评分: {top_platform.get('score')}/10)")
    
    if response.processing_metadata:
        metadata = response.processing_metadata
        print(f"⚙️ 处理模式: {metadata.get('processing_mode')}")
        if metadata.get('processing_time_seconds'):
            print(f"⏱️ 处理耗时: {metadata.get('processing_time_seconds')}秒")


def print_complete_data_structure(response: RecyclingCoordinatorResponse):
    """打印完整的数据结构和汇总格式"""
    print_subsection("完整数据结构汇总")
    
    # 转换为字典格式并打印
    data_dict = response.to_dict()
    
    print("📋 响应数据完整结构:")
    print_json(data_dict, "协调器完整响应数据")
    
    # 打印数据统计
    print_subsection("数据统计信息")
    
    # 基础统计
    print("🔢 基础统计:")
    print(f"  响应状态: {'✅ 成功' if response.success else '❌ 失败'}")
    print(f"  数据来源: {response.source}")
    print(f"  错误信息: {response.error or '无'}")
    
    # 地点推荐统计
    if response.location_recommendation:
        loc_rec = response.location_recommendation
        print(f"\n📍 地点推荐统计:")
        print(f"  推荐成功: {'✅' if loc_rec.success else '❌'}")
        print(f"  回收类型: {loc_rec.recycling_type or '未识别'}")
        print(f"  地点总数: {len(loc_rec.locations)}")
        
        if loc_rec.locations:
            distances = [loc.distance_meters for loc in loc_rec.locations if loc.distance_meters is not None]
            if distances:
                print(f"  最近距离: {min(distances):.0f}米")
                print(f"  最远距离: {max(distances):.0f}米")
                print(f"  平均距离: {sum(distances)/len(distances):.0f}米")
        
        if loc_rec.search_params:
            search_params = loc_rec.search_params
            print(f"  搜索半径: {search_params.get('radius', 0)/1000:.1f}公里")
            print(f"  搜索关键词: {search_params.get('keyword', 'N/A')}")
    
    # 平台推荐统计
    if response.platform_recommendation:
        plat_rec = response.platform_recommendation
        print(f"\n🏪 平台推荐统计:")
        print(f"  推荐成功: {'✅' if plat_rec.success else '❌'}")
        
        if plat_rec.ai_recommendations:
            recommendations = plat_rec.ai_recommendations.recommendations
            print(f"  AI推荐数量: {len(recommendations)}")
            
            if recommendations:
                scores = [rec.suitability_score for rec in recommendations]
                print(f"  最高评分: {max(scores)}/10")
                print(f"  最低评分: {min(scores)}/10")
                print(f"  平均评分: {sum(scores)/len(scores):.1f}/10")
                
                # 统计优势和劣势
                all_pros = []
                all_cons = []
                for rec in recommendations:
                    all_pros.extend(rec.pros)
                    all_cons.extend(rec.cons)
                print(f"  总优势点数: {len(all_pros)}")
                print(f"  总劣势点数: {len(all_cons)}")
        
        if plat_rec.platform_details:
            print(f"  平台详细数据: {len(plat_rec.platform_details)}个")
        
        if plat_rec.rag_metadata:
            rag_meta = plat_rec.rag_metadata
            print(f"  RAG检索结果: {rag_meta.get('total_results', 0)}个")
            print(f"  相似度阈值: {rag_meta.get('similarity_threshold', 0)}")
    
    # 处理元数据统计
    if response.processing_metadata:
        metadata = response.processing_metadata
        print(f"\n⚙️ 处理元数据:")
        print(f"  处理模式: {metadata.get('processing_mode', 'unknown')}")
        
        if metadata.get('processing_time_seconds'):
            processing_time = metadata.get('processing_time_seconds')
            print(f"  总处理时间: {processing_time:.2f}秒")
        
        # 子服务状态
        loc_meta = metadata.get('location_recommendation', {})
        plat_meta = metadata.get('platform_recommendation', {})
        
        print(f"  地点推荐状态: {'✅ 成功' if loc_meta.get('success') else '❌ 失败'}")
        if loc_meta.get('error'):
            print(f"    错误: {loc_meta.get('error')}")
        
        print(f"  平台推荐状态: {'✅ 成功' if plat_meta.get('success') else '❌ 失败'}")
        if plat_meta.get('error'):
            print(f"    错误: {plat_meta.get('error')}")
    
    # 数据质量评估
    print_subsection("数据质量评估")
    
    quality_score = 0
    max_score = 10
    
    # 基础成功性 (30%)
    if response.success:
        quality_score += 3
    
    # 地点推荐质量 (35%)
    if response.has_location_recommendations():
        quality_score += 2  # 基础分
        loc_count = len(response.location_recommendation.locations)
        if loc_count >= 10:
            quality_score += 1.5  # 数量充足
        elif loc_count >= 5:
            quality_score += 1
        
        # 距离质量
        nearby_count = len(response.get_nearby_locations(max_distance_meters=5000))
        if nearby_count > 0:
            quality_score += 1  # 有5公里内的地点
    
    # 平台推荐质量 (35%)
    if response.has_platform_recommendations():
        quality_score += 2  # 基础分
        recommendations = response.platform_recommendation.ai_recommendations.recommendations
        if recommendations:
            avg_score = sum(rec.suitability_score for rec in recommendations) / len(recommendations)
            if avg_score >= 8:
                quality_score += 1.5  # 高质量推荐
            elif avg_score >= 6:
                quality_score += 1
            
            # 推荐理由质量
            if all(len(rec.recommendation_reason) > 20 for rec in recommendations):
                quality_score += 1  # 详细的推荐理由
    
    quality_percentage = (quality_score / max_score) * 100
    print(f"📊 数据质量评分: {quality_score:.1f}/{max_score} ({quality_percentage:.1f}%)")
    
    if quality_percentage >= 80:
        print("   评级: ⭐⭐⭐ 优秀")
    elif quality_percentage >= 60:
        print("   评级: ⭐⭐ 良好")
    elif quality_percentage >= 40:
        print("   评级: ⭐ 一般")
    else:
        print("   评级: 需要改进")


@pytest.mark.asyncio
async def test_complete_coordination():
    """测试完整协调功能"""
    print_separator("测试完整协调功能")

    # 准备测试数据 - 模拟分析结果
    analysis_result = {
        "category": "电子产品",
        "sub_category": "智能手机",
        "brand": "苹果",
        "condition": "八成新",
        "description": "iPhone 12，使用两年，外观良好，功能正常，有些许磨损",
        "keywords": ["手机", "iPhone", "苹果", "电子产品"],
        "special_features": "Face ID正常，电池健康度85%"
    }
    
    # 模拟用户位置 (北京市朝阳区)
    user_location = "116.447303,39.906823"
    
    print("🔍 输入分析结果:")
    print_json(analysis_result)
    print(f"📍 用户位置: {user_location}")

    async with RecyclingCoordinatorAgent() as coordinator:
        print("\n🚀 开始协调回收捐赠推荐...")
        start_time = time.time()

        # 测试并行模式
        print("\n【并行处理模式】")
        result = await coordinator.coordinate_recycling_donation(
            analysis_result=analysis_result,
            user_location=user_location,
            radius=30000,  # 30公里搜索半径
            max_locations=15,  # 最多15个地点
            enable_parallel=True
        )

        end_time = time.time()
        processing_time = end_time - start_time

        print(f"⏱️ 处理时间: {processing_time:.2f} 秒")
        print(f"✅ 协调结果: {'成功' if result.success else '失败'}")
        
        if result.success:
            # 打印处理摘要
            print_processing_summary(result)
            
            # 打印地点推荐
            print_location_recommendations(result.location_recommendation)
            
            # 打印平台推荐
            print_platform_recommendations(result.platform_recommendation)
            
            # 打印完整数据结构和汇总
            print_complete_data_structure(result)
            
        else:
            print(f"❌ 错误信息: {result.error}")
            # 即使失败也打印数据结构以便调试
            print_complete_data_structure(result)


@pytest.mark.asyncio
async def test_serial_vs_parallel():
    """测试串行与并行处理模式对比"""
    print_separator("测试串行与并行处理模式对比")

    # 准备测试数据
    analysis_result = {
        "category": "家用电器",
        "sub_category": "电视",
        "brand": "小米",
        "condition": "七成新",
        "description": "55寸智能电视，使用三年，画质清晰，遥控器齐全",
        "keywords": ["电视", "家电", "智能电视"],
        "special_features": "4K分辨率，支持HDR"
    }
    
    user_location = "121.473701,31.230416"  # 上海市黄浦区
    
    async with RecyclingCoordinatorAgent() as coordinator:
        
        # 测试串行模式
        print_subsection("串行处理模式")
        start_time = time.time()
        
        serial_result = await coordinator.coordinate_recycling_donation(
            analysis_result=analysis_result,
            user_location=user_location,
            enable_parallel=False
        )
        
        serial_time = time.time() - start_time
        print(f"⏱️ 串行处理时间: {serial_time:.2f} 秒")
        print(f"✅ 串行处理结果: {'成功' if serial_result.success else '失败'}")
        
        # 测试并行模式
        print_subsection("并行处理模式")
        start_time = time.time()
        
        parallel_result = await coordinator.coordinate_recycling_donation(
            analysis_result=analysis_result,
            user_location=user_location,
            enable_parallel=True
        )
        
        parallel_time = time.time() - start_time
        print(f"⏱️ 并行处理时间: {parallel_time:.2f} 秒")
        print(f"✅ 并行处理结果: {'成功' if parallel_result.success else '失败'}")
        
        # 性能对比
        print_subsection("性能对比")
        if serial_time > 0 and parallel_time > 0:
            speedup = serial_time / parallel_time
            print(f"⚡ 性能提升: {speedup:.2f}x")
            print(f"⏱️ 时间节省: {(serial_time - parallel_time):.2f} 秒")
        
        # 结果一致性检查
        print_subsection("结果一致性检查")
        both_success = serial_result.success and parallel_result.success
        print(f"✅ 两种模式都成功: {both_success}")
        
        if both_success:
            # 比较回收类型
            serial_type = serial_result.get_recycling_type()
            parallel_type = parallel_result.get_recycling_type()
            print(f"♻️ 回收类型一致: {serial_type == parallel_type} ({serial_type} vs {parallel_type})")
            
            # 比较地点数量
            serial_locations = len(serial_result.get_nearby_locations()) if serial_result.has_location_recommendations() else 0
            parallel_locations = len(parallel_result.get_nearby_locations()) if parallel_result.has_location_recommendations() else 0
            print(f"📍 附近地点数: 串行{serial_locations}个, 并行{parallel_locations}个")
            
            # 比较平台推荐
            serial_has_platforms = serial_result.has_platform_recommendations()
            parallel_has_platforms = parallel_result.has_platform_recommendations()
            print(f"🏪 平台推荐一致: {serial_has_platforms == parallel_has_platforms}")
            
            # 详细对比平台推荐结果
            if serial_has_platforms and parallel_has_platforms:
                serial_platforms = [rec.platform_name for rec in serial_result.platform_recommendation.ai_recommendations.recommendations]
                parallel_platforms = [rec.platform_name for rec in parallel_result.platform_recommendation.ai_recommendations.recommendations]
                print(f"🏪 推荐平台名称: 串行{serial_platforms}, 并行{parallel_platforms}")
                print(f"🏪 平台名称一致: {set(serial_platforms) == set(parallel_platforms)}")
        
        # 打印串行模式详细结果
        print_subsection("串行模式详细结果")
        if serial_result.success:
            print("✅ 串行模式执行成功")
            print_complete_data_structure(serial_result)
        else:
            print("❌ 串行模式执行失败")
            print(f"错误信息: {serial_result.error}")
        
        # 打印并行模式详细结果  
        print_subsection("并行模式详细结果")
        if parallel_result.success:
            print("✅ 并行模式执行成功")
            print_complete_data_structure(parallel_result)
        else:
            print("❌ 并行模式执行失败")
            print(f"错误信息: {parallel_result.error}")


@pytest.mark.asyncio
async def test_error_handling():
    """测试错误处理"""
    print_separator("测试错误处理")

    async with RecyclingCoordinatorAgent() as coordinator:
        
        # 测试无效分析结果
        print_subsection("测试无效分析结果")
        result = await coordinator.coordinate_recycling_donation(
            analysis_result=None,
            user_location="116.447303,39.906823"
        )
        print(f"❌ 空分析结果处理: {'✓ 正确拒绝' if not result.success else '✗ 应该失败'}")
        if not result.success:
            print(f"错误信息: {result.error}")
        
        # 测试无效位置
        print_subsection("测试无效用户位置")
        result = await coordinator.coordinate_recycling_donation(
            analysis_result={"category": "电子产品", "description": "测试物品"},
            user_location=""
        )
        print(f"❌ 空位置处理: {'✓ 正确拒绝' if not result.success else '✗ 应该失败'}")
        if not result.success:
            print(f"错误信息: {result.error}")


@pytest.mark.asyncio 
async def test_component_status():
    """测试组件状态"""
    print_separator("测试组件状态")

    coordinator = RecyclingCoordinatorAgent()
    
    # 测试初始状态
    initial_status = coordinator.get_component_status()
    print("初始组件状态:")
    print_json(initial_status)
    
    # 初始化后状态
    await coordinator._ensure_initialized()
    initialized_status = coordinator.get_component_status()
    print("\n初始化后组件状态:")
    print_json(initialized_status)
    
    # 清理资源
    await coordinator.close()
    final_status = coordinator.get_component_status()
    print("\n清理后组件状态:")
    print_json(final_status)


async def main():
    """主测试函数"""
    print_separator("回收捐赠总协调器Agent测试开始", 100)
    
    # 设置日志级别
    logging.basicConfig(level=logging.INFO)
    app_logger.setLevel(logging.INFO)
    
    try:
        # 基本功能测试
        await test_complete_coordination()
        
        # 性能对比测试
        await test_serial_vs_parallel()
        
        # 错误处理测试
        await test_error_handling()
        
        # 组件状态测试
        await test_component_status()
        
        print_separator("所有测试完成", 100)
        print("✅ 测试执行完毕，请查看上方结果")
        
    except Exception as e:
        print(f"❌ 测试过程中出现错误: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main()) 