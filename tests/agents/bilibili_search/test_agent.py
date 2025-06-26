"""
测试Bilibili搜索Agent（Function Calling版本）
"""

import asyncio
import sys
import pytest
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from app.agents.bilibili_search.agent import BilibiliSearchAgent
from app.core.logger import app_logger


class TestBilibiliSearchAgent:
    """Bilibili搜索Agent测试类"""
    
    @pytest.mark.asyncio
    async def test_search_from_image(self):
        """测试从图片文件搜索视频（完整流程）"""
        print("\n" + "="*50)
        print("测试：从图片文件搜索DIY教程视频")
        print("="*50)
        
        # 使用测试图片 - 使用项目根目录的绝对路径
        project_root = Path(__file__).parent.parent.parent.parent
        image_path = project_root / "tests" / "services" / "llm" / "测试图片.png"
        
        if not image_path.exists():
            print(f"测试图片不存在: {image_path}")
            print("跳过图片文件测试")
            pytest.skip(f"测试图片不存在: {image_path}")
            return
        
        # 转换为字符串路径
        image_path_str = str(image_path)
        
        async with BilibiliSearchAgent() as agent:
            result = await agent.search_from_image(
                image_path=image_path_str,
                max_videos=10
            )
            
            print(f"搜索结果: {result.get('success', False)}")
            assert "success" in result
            
            if result.get("success"):
                print(f"来源: {result['source']}")
                print(f"图片路径: {result.get('image_path', 'N/A')}")
                print(f"图片分析结果: {result.get('analysis_result', {})}")
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
                assert result["source"] == "image"
                assert "image_path" in result
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
    async def test_search_from_text(self):
        """测试从文字描述搜索视频（完整流程）"""
        print("\n" + "="*50)
        print("测试：从文字描述搜索DIY教程视频")
        print("="*50)
        
        text_description = "我有一个旧的纸箱，想要把它改造成可以放书的收纳盒，纸箱比较大，想要分隔成几个小格子"
        print(f"输入文字描述: {text_description}")
        
        async with BilibiliSearchAgent() as agent:
            result = await agent.search_from_text(
                text_description=text_description,
                max_videos=10
            )
            
            print(f"搜索结果: {result.get('success', False)}")
            assert "success" in result
            
            if result.get("success"):
                print(f"来源: {result['source']}")
                print(f"原始文字: {result.get('original_text', 'N/A')}")
                print(f"文字分析结果: {result.get('analysis_result', {})}")
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
                assert result["source"] == "text"
                assert "original_text" in result
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
    async def test_search_from_text_multiple_scenarios(self):
        """测试多个文字描述场景"""
        print("\n" + "="*50)
        print("测试：多个文字描述场景")
        print("="*50)
        
        test_scenarios = [
            {
                "description": "一件穿了很久的棉质T恤，虽然有些发黄但没有破损，想改造成实用的东西",
                "category": "服装改造"
            },
            {
                "description": "家里有个坏掉的旧手机，屏幕碎了但其他功能正常，想废物利用",
                "category": "电子产品"
            },
            {
                "description": "收集了很多空的玻璃瓶，想要做成装饰品或者收纳用具",
                "category": "生活用品"
            }
        ]
        
        async with BilibiliSearchAgent() as agent:
            for i, scenario in enumerate(test_scenarios):
                print(f"\n--- 场景 {i+1}: {scenario['category']} ---")
                print(f"描述: {scenario['description']}")
                
                result = await agent.search_from_text(
                    text_description=scenario['description'],
                    max_videos=5
                )
                
                print(f"搜索结果: {result.get('success', False)}")
                
                if result.get("success"):
                    print(f"提取的关键词: {result.get('keywords', [])}")
                    print(f"搜索意图: {result.get('search_intent', 'N/A')}")
                    print(f"找到视频数量: {len(result.get('videos', []))}")
                    
                    # 显示第一个视频
                    videos = result.get("videos", [])
                    if videos:
                        video = videos[0]
                        print(f"推荐视频: {video['title']} - {video['uploader']}")
                else:
                    print(f"搜索失败: {result.get('error', 'Unknown error')}")
                
                # 基本验证
                assert "success" in result
                if result.get("success"):
                    assert "keywords" in result
                    assert "search_intent" in result
                    assert "videos" in result

    @pytest.mark.asyncio
    async def test_error_handling(self):
        """测试错误处理"""
        print("\n" + "="*50)
        print("测试：错误处理")
        print("="*50)
        
        async with BilibiliSearchAgent() as agent:
            # 测试不存在的图片文件
            print("测试不存在的图片文件...")
            result = await agent.search_from_image(
                image_path="nonexistent_image.jpg",
                max_videos=5
            )
            
            print(f"不存在图片的搜索结果: {result.get('success', False)}")
            assert result.get("success") == False
            assert "error" in result
            assert "source" in result
            
            # 测试空文字描述
            print("\n测试空文字描述...")
            result = await agent.search_from_text(
                text_description="",
                max_videos=5
            )
            
            print(f"空文字描述的搜索结果: {result.get('success', False)}")
            # 空文字描述可能成功（返回默认关键词）或失败
            assert "success" in result
            if not result.get("success"):
                assert "error" in result


# 单独的异步测试函数，用于直接运行
async def run_search_from_image():
    """运行图片搜索测试"""
    test_instance = TestBilibiliSearchAgent()
    await test_instance.test_search_from_image()


async def run_search_from_text():
    """运行文字搜索测试"""
    test_instance = TestBilibiliSearchAgent()
    await test_instance.test_search_from_text()


async def run_multiple_scenarios():
    """运行多场景测试"""
    test_instance = TestBilibiliSearchAgent()
    await test_instance.test_search_from_text_multiple_scenarios()


async def run_error_handling():
    """运行错误处理测试"""
    test_instance = TestBilibiliSearchAgent()
    await test_instance.test_error_handling()


async def main():
    """主测试函数 - 用于直接运行"""
    print("开始测试Bilibili搜索Agent（端到端版本）")
    print("请确保已正确配置蓝心大模型API密钥")
    
    try:
        # 测试1：从图片搜索
        await run_search_from_image()
        
        # 测试2：从文字描述搜索
        await run_search_from_text()
        
        # 测试3：多个场景测试
        await run_multiple_scenarios()
        
        # 测试4：错误处理
        await run_error_handling()
        
        print("\n" + "="*50)
        print("所有测试完成")
        print("="*50)
        
    except Exception as e:
        app_logger.error(f"测试过程中出现错误: {e}")
        print(f"测试失败: {e}")


if __name__ == "__main__":
    # 直接运行时使用asyncio
    asyncio.run(main()) 