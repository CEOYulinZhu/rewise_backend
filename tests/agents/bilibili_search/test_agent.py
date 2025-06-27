"""
测试Bilibili搜索Agent（基于分析结果版本）
"""

import asyncio
import sys
from pathlib import Path

import pytest

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from app.agents.bilibili_search.agent import BilibiliSearchAgent


class TestBilibiliSearchAgent:
    """Bilibili搜索Agent测试类"""
    
    @pytest.fixture
    def sample_analysis_results(self):
        """样例分析结果"""
        return [
            {
                "category": "生活用品",
                "sub_category": "纸箱",
                "condition": "完好",
                "description": "一个大纸箱，想要改造成收纳盒",
                "material": "纸质",
                "keywords": ["纸箱", "收纳", "DIY"],
                "special_features": "比较大，可以分隔"
            },
            {
                "category": "服装",
                "sub_category": "T恤",
                "condition": "八成新",
                "description": "一件棉质T恤，有些发黄但没有破损",
                "material": "棉布",
                "keywords": ["T恤", "棉质", "改造"],
                "special_features": "发黄但完整"
            },
            {
                "category": "电子产品",
                "sub_category": "手机",
                "condition": "损坏",
                "description": "一台旧手机，屏幕碎了但其他功能正常",
                "brand": "小米",
                "material": "金属塑料",
                "keywords": ["手机", "旧手机", "废物利用"],
                "special_features": "屏幕损坏"
            },
            {
                "category": "生活用品",
                "sub_category": "玻璃瓶",
                "condition": "完好",
                "description": "收集了很多空的玻璃瓶，想要做成装饰品",
                "material": "玻璃",
                "keywords": ["玻璃瓶", "装饰", "创意"],
                "special_features": "多个空瓶"
            }
        ]
    
    @pytest.mark.asyncio
    async def test_search_from_analysis(self, sample_analysis_results):
        """测试从分析结果搜索视频"""
        print("\n" + "="*50)
        print("测试：从分析结果搜索DIY教程视频")
        print("="*50)
        
        # 使用第一个样例：纸箱改造
        analysis_result = sample_analysis_results[0]
        print(f"输入分析结果: {analysis_result}")
        
        async with BilibiliSearchAgent() as agent:
            result = await agent.search_from_analysis(
                analysis_result=analysis_result,
                max_videos=10
            )
            
            print(f"搜索结果: {result.get('success', False)}")
            assert "success" in result
            
            if result.get("success"):
                print(f"来源: {result['source']}")
                print(f"分析结果: {result.get('analysis_result', {})}")
                print(f"提取的关键词: {result.get('keywords', [])}")
                print(f"搜索意图: {result.get('search_intent', 'N/A')}")
                print(f"找到视频数量: {len(result.get('videos', []))}")
                print(f"总结果数: {result.get('total', 0)}")
                
                # Function Calling结果
                fc_result = result.get('function_call_result', {})
                if fc_result.get('success'):
                    print(f"Function Calling成功提取关键词: {fc_result['keywords']}")
                    print(f"Function Calling来源: {fc_result.get('source', 'function_calling')}")
                else:
                    print(f"Function Calling失败: {fc_result.get('error', 'N/A')}")
                
                # 显示前5个视频
                for i, video in enumerate(result.get("videos", [])[:5]):
                    print(f"\n视频 {i+1}:")
                    print(f"  标题: {video['title']}")
                    print(f"  UP主: {video['uploader']}")
                    print(f"  播放量: {video['play_count']}")
                    print(f"  时长: {video['duration']}")
                    print(f"  链接: {video['url']}")
                    print(f"  简介: {video['description']}")
                    print(f"  封面: {video['cover_url']}")
                    print(f"  弹幕数: {video['danmaku_count']}")

                # 验证必要字段
                assert result["source"] == "analysis_result"
                assert "analysis_result" in result
                assert "keywords" in result
                assert "videos" in result
                assert "function_call_result" in result
                
            else:
                print(f"搜索失败: {result.get('error', 'Unknown error')}")
                # 对于失败的情况，也要验证基本结构
                assert "error" in result
                assert "source" in result

    @pytest.mark.asyncio
    async def test_search_multiple_scenarios(self, sample_analysis_results):
        """测试多个分析结果场景"""
        print("\n" + "="*50)
        print("测试：多个分析结果场景")
        print("="*50)
        
        scenario_names = ["纸箱改造", "T恤改造", "手机废物利用", "玻璃瓶装饰"]
        
        async with BilibiliSearchAgent() as agent:
            for i, analysis_result in enumerate(sample_analysis_results):
                print(f"\n--- 场景 {i+1}: {scenario_names[i]} ---")
                print(f"类别: {analysis_result['category']} - {analysis_result['sub_category']}")
                print(f"描述: {analysis_result['description']}")
                
                result = await agent.search_from_analysis(
                    analysis_result=analysis_result,
                    max_videos=5
                )
                
                print(f"搜索结果: {result.get('success', False)}")
                
                if result.get("success"):
                    print(f"提取的关键词: {result.get('keywords', [])}")
                    print(f"搜索意图: {result.get('search_intent', 'N/A')}")
                    print(f"找到视频数量: {len(result.get('videos', []))}")
                    
                    # Function Calling结果来源
                    fc_result = result.get('function_call_result', {})
                    print(f"关键词来源: {fc_result.get('source', 'unknown')}")
                    
                    # 显示第一个视频
                    videos = result.get("videos", [])
                    if videos:
                        video = videos[0]
                        print(f"推荐视频: {video['title']} - {video['uploader']}")
                else:
                    print(f"搜索失败: {result.get('error', 'Unknown error')}")
    
    @pytest.mark.asyncio
    async def test_error_handling(self):
        """测试错误处理"""
        print("\n" + "="*50)
        print("测试：错误处理")
        print("="*50)
        
        async with BilibiliSearchAgent() as agent:
            # 测试空分析结果
            result = await agent.search_from_analysis(None)
            print(f"空分析结果测试: {result.get('success', False)}")
            assert not result["success"]
            assert "分析结果为空" in result["error"]
            
            # 测试空字典
            result = await agent.search_from_analysis({})
            print(f"空字典测试: {result.get('success', False)}")
            # 空字典可能被接受但导致后续处理问题
            
            # 测试格式错误的分析结果
            result = await agent.search_from_analysis("not a dict")
            print(f"格式错误测试: {result.get('success', False)}")
            assert not result["success"]
            assert "格式错误" in result["error"]
    
    def test_validation_logic(self, sample_analysis_results):
        """测试输入验证逻辑"""
        print(f"\n==== 测试输入验证逻辑 ====")
        
        # 测试正常输入
        analysis_result = sample_analysis_results[0]
        assert isinstance(analysis_result, dict)
        assert "category" in analysis_result
        assert "description" in analysis_result
        print("输入验证逻辑测试通过！")


async def run_search_from_analysis():
    """运行分析结果搜索测试"""
    sample_analysis = {
        "category": "生活用品",
        "sub_category": "纸箱",
        "condition": "完好",
        "description": "一个大纸箱，想要改造成收纳盒",
        "material": "纸质",
        "keywords": ["纸箱", "收纳", "DIY"]
    }
    
    async with BilibiliSearchAgent() as agent:
        result = await agent.search_from_analysis(sample_analysis, max_videos=3)
        
        if result.get("success"):
            print("✅ 搜索成功!")
            print(f"关键词: {result['keywords']}")
            print(f"找到 {len(result['videos'])} 个视频")
            for video in result["videos"]:
                print(f"- {video['title']} ({video['uploader']})")
        else:
            print(f"❌ 搜索失败: {result.get('error')}")

async def run_multiple_scenarios():
    """运行多场景测试"""
    scenarios = [
        {
            "category": "服装",
            "sub_category": "T恤",
            "description": "旧T恤改造",
            "material": "棉布"
        },
        {
            "category": "电子产品", 
            "sub_category": "手机",
            "description": "旧手机废物利用",
            "condition": "损坏"
        }
    ]
    
    async with BilibiliSearchAgent() as agent:
        for i, scenario in enumerate(scenarios):
            print(f"\n场景 {i+1}: {scenario['description']}")
            result = await agent.search_from_analysis(scenario, max_videos=2)
            
            if result.get("success"):
                print(f"关键词: {result['keywords']}")
                videos = result["videos"]
                if videos:
                    print(f"推荐: {videos[0]['title']}")
            else:
                print(f"失败: {result.get('error')}")

async def run_error_handling():
    """运行错误处理测试"""
    async with BilibiliSearchAgent() as agent:
        # 测试空输入
        result = await agent.search_from_analysis(None)
        print(f"空输入测试: {'通过' if not result['success'] else '失败'}")

async def main():
    """主测试函数"""
    print("=" * 60)
    print("Bilibili搜索Agent - 简单功能测试")
    print("=" * 60)
    
    print("\n1. 测试分析结果搜索...")
    await run_search_from_analysis()
    
    print("\n2. 测试多个场景...")
    await run_multiple_scenarios()
    
    print("\n3. 测试错误处理...")
    await run_error_handling()
    
    print("\n测试完成!")

if __name__ == "__main__":
    asyncio.run(main()) 