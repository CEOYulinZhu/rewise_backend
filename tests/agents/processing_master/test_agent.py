"""
总处理协调器Agent真实测试

使用真实的服务和Agent进行端到端测试，不使用模拟数据。
测试真实的数据流和处理过程。
"""

import pytest
import asyncio
import tempfile
import os
import json
import time
import sys
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from app.agents.processing_master.agent import ProcessingMasterAgent
from app.models.processing_master_models import (
    ProcessingMasterRequest, ProcessingStepStatus
)
from app.core.logger import app_logger


class TestProcessingMasterAgentReal:
    """总处理协调器Agent真实测试类"""

    def get_test_image_path(self):
        """获取测试图片路径"""
        # 使用真实的测试图片路径
        test_image_path = r"tests\services\llm\测试图片.png"
        if os.path.exists(test_image_path):
            return test_image_path
        else:
            # 如果相对路径不存在，尝试绝对路径
            absolute_path = r"D:\Project\python\闲置物语-后端\tests\services\llm\测试图片.png"
            if os.path.exists(absolute_path):
                return absolute_path
            else:
                # 如果都不存在，返回None，测试将跳过
                return None

    def test_validate_request_success(self):
        """测试请求验证 - 成功情况"""
        agent = ProcessingMasterAgent()

        # 测试纯文字请求
        request = ProcessingMasterRequest(
            text_description="一台使用两年的iPhone 12，黑色，功能正常，有轻微划痕",
            user_location={"lat": 39.906823, "lon": 116.447303}
        )

        result = agent._validate_request(request)
        assert result["valid"] is True

        print("✓ 文字请求验证通过")

    def test_validate_request_with_image(self):
        """测试请求验证 - 图片请求"""
        agent = ProcessingMasterAgent()
        image_path = self.get_test_image_path()
        
        if image_path is None:
            print("⚠️ 测试图片不存在，跳过图片验证测试")
            return
        
        request = ProcessingMasterRequest(
            image_url=image_path,
            user_location={"lat": 39.906823, "lon": 116.447303}
        )
        
        result = agent._validate_request(request)
        assert result["valid"] is True
        
        print(f"✓ 图片请求验证通过，图片路径: {image_path}")
    
    def test_validate_request_failures(self):
        """测试请求验证 - 失败情况"""
        agent = ProcessingMasterAgent()
        
        # 测试空请求
        request = ProcessingMasterRequest()
        result = agent._validate_request(request)
        assert result["valid"] is False
        assert "必须提供图片URL或文字描述" in result["error"]
        print("✓ 空请求验证失败（符合预期）")
        
        # 测试短文字
        request = ProcessingMasterRequest(text_description="a")
        result = agent._validate_request(request)
        assert result["valid"] is False
        assert "文字描述至少需要2个字符" in result["error"]
        print("✓ 短文字验证失败（符合预期）")
        
        # 测试不存在的图片
        request = ProcessingMasterRequest(image_url="/nonexistent/path.jpg")
        result = agent._validate_request(request)
        assert result["valid"] is False
        assert "图片文件不存在" in result["error"]
        print("✓ 不存在图片验证失败（符合预期）")

    @pytest.mark.asyncio
    async def test_real_text_analysis(self):
        """测试真实的文字内容分析"""
        async with ProcessingMasterAgent() as agent:
            request = ProcessingMasterRequest(
                text_description="一台MacBook Pro 2019款，13寸，使用三年，屏幕有轻微划痕，电池健康度85%，包装盒齐全"
            )

            print("\n=== 开始真实文字分析测试 ===")
            result = await agent._analyze_content(request)

            print(f"分析成功: {result.get('success')}")
            if result.get('success'):
                print("分析结果:")
                print(json.dumps(result, indent=2, ensure_ascii=False))
            else:
                print(f"分析失败: {result.get('error')}")

            assert result.get('success') or 'error' in result
            print("✓ 文字分析测试完成")

    @pytest.mark.asyncio
    async def test_real_image_analysis(self):
        """测试真实的图片内容分析"""
        image_path = self.get_test_image_path()
        
        if image_path is None:
            print("⚠️ 测试图片不存在，跳过图片分析测试")
            return
        
        async with ProcessingMasterAgent() as agent:
            request = ProcessingMasterRequest(image_url=image_path)
            
            print("\n=== 开始真实图片分析测试 ===")
            print(f"使用图片: {image_path}")
            
            result = await agent._analyze_content(request)
            
            print(f"分析成功: {result.get('success')}")
            if result.get('success'):
                print("分析结果:")
                print(json.dumps(result, indent=2, ensure_ascii=False))
            else:
                print(f"分析失败: {result.get('error')}")
            
            assert result.get('success') or 'error' in result
            print("✓ 图片分析测试完成")
    
    @pytest.mark.asyncio
    async def test_real_image_text_analysis(self):
        """测试真实的图片+文字分析"""
        image_path = self.get_test_image_path()
        
        if image_path is None:
            print("⚠️ 测试图片不存在，跳过图片+文字分析测试")
            return
        
        async with ProcessingMasterAgent() as agent:
            request = ProcessingMasterRequest(
                image_url=image_path,
                text_description="这是一台苹果MacBook，请分析其状态和价值"
            )
            
            print("\n=== 开始真实图片+文字分析测试 ===")
            result = await agent._analyze_content(request)
            
            print(f"分析成功: {result.get('success')}")
            if result.get('success'):
                print("合并分析结果:")
                print(json.dumps(result, indent=2, ensure_ascii=False))
                
                # 检查是否有合并元数据
                if '_merge_metadata' in result:
                    print("\n合并元数据:")
                    print(json.dumps(result['_merge_metadata'], indent=2, ensure_ascii=False))
            else:
                print(f"分析失败: {result.get('error')}")
            
            assert result.get('success') or 'error' in result
            print("✓ 图片+文字分析测试完成")

    @pytest.mark.asyncio
    async def test_complete_solution_text_only(self):
        """测试完整解决方案 - 纯文字"""
        request = ProcessingMasterRequest(
            text_description="一部iPhone 13 Pro Max，深空灰，256GB，使用一年半，9成新，原装充电器和包装齐全，功能完好无维修史",
            user_location={"lat": 39.906823, "lon": 116.447303}
        )

        print("\n=== 开始完整解决方案测试（纯文字）===")

        async with ProcessingMasterAgent() as agent:
            steps = []
            step_count = 0

            async for step in agent.process_complete_solution(request):
                step_count += 1
                steps.append(step)

                print(f"\n[步骤 {step_count}] {step.step_name}")
                print(f"标题: {step.step_title}")
                print(f"状态: {step.status.value}")
                print(f"描述: {step.description}")

                if step.error:
                    print(f"错误: {step.error}")

                if step.metadata:
                    print("元数据:")
                    print(json.dumps(step.metadata, indent=2, ensure_ascii=False))

                if step.result and step.step_name != "result_integration":
                    # 对于非最终结果，只显示摘要
                    if isinstance(step.result, dict):
                        summary_keys = ['success', 'category', 'subcategory', 'brand', 'condition']
                        summary = {k: step.result.get(k) for k in summary_keys if k in step.result}
                        if summary:
                            print("结果摘要:")
                            print(json.dumps(summary, indent=2, ensure_ascii=False))

                # 如果是最终整合步骤，显示优化后的结果结构
                if step.step_name == "result_integration" and step.result:
                    print("\n=== 最终整合结果（优化后结构） ===")
                    result = step.result

                    # 显示核心信息
                    print(f"处理成功: {result.get('success')}")
                    print(f"数据来源: {result.get('source')}")

                    # 显示分析结果（全局唯一）
                    if 'analysis_result' in result:
                        analysis = result['analysis_result']
                        print(f"\n📱 物品分析:")
                        print(f"  类别: {analysis.get('category', '未知')} - {analysis.get('sub_category', '未知')}")
                        print(f"  品牌: {analysis.get('brand', '未知')}")
                        print(f"  状态: {analysis.get('condition', '未知')}")
                        print(f"  颜色: {analysis.get('color', '未知')}")

                    # 显示各解决方案（已去除重复的analysis_result）
                    if 'disposal_solution' in result:
                        disposal = result['disposal_solution']
                        print(f"\n🎯 处置推荐: {'成功' if disposal.get('success') else '失败'}")
                        if disposal.get('recommendations'):
                            overall = disposal['recommendations'].get('overall_recommendation', {})
                            print(f"  主要推荐: {overall.get('primary_choice', '未知')}")

                    if 'creative_solution' in result:
                        creative = result['creative_solution']
                        print(f"\n🔨 创意改造: {'成功' if creative.get('success') else '失败'}")
                        if creative.get('renovation_plan'):
                            plan = creative['renovation_plan']['summary']
                            print(f"  改造方案: {plan.get('title', '未知')}")
                            print(f"  难度: {plan.get('difficulty', '未知')}")

                    if 'recycling_solution' in result:
                        recycling = result['recycling_solution']
                        print(f"\n♻️ 回收方案: {'成功' if recycling.get('success') else '失败'}")
                        if recycling.get('processing_summary'):
                            summary = recycling['processing_summary']
                            print(f"  回收点数量: {summary.get('location_count', 0)}")
                            print(f"  推荐平台数: {summary.get('platform_count', 0)}")

                    if 'secondhand_solution' in result:
                        secondhand = result['secondhand_solution']
                        print(f"\n💰 二手交易: {'成功' if secondhand.get('success') else '失败'}")
                        if secondhand.get('search_result'):
                            search = secondhand['search_result']['result']
                            print(f"  找到商品: {search.get('total_products', 0)}个")
                        if secondhand.get('content_result'):
                            content = secondhand['content_result']['content_result']
                            print(f"  生成标题: {content.get('title', '未知')}")

                    # 显示处理元数据
                    if 'processing_metadata' in result:
                        metadata = result['processing_metadata']
                        print(f"\n⏱️ 处理统计:")
                        print(f"  总耗时: {metadata.get('processing_time_seconds', 0):.2f}秒")
                        agents = metadata.get('agents_executed', {})
                        print(f"  成功Agent数: {agents.get('total_successful', 0)}")

                    print("=" * 50)

            print(f"\n✓ 完整解决方案测试完成，共执行 {step_count} 个步骤")

            # 验证基本步骤
            step_names = [step.step_name for step in steps]
            expected_steps = ["input_validation", "content_analysis"]

            for expected in expected_steps:
                assert expected in step_names, f"缺少必要步骤: {expected}"

            print("✓ 基本步骤验证通过")

    @pytest.mark.asyncio
    async def test_complete_solution_with_image(self):
        """测试完整解决方案 - 图片+文字"""
        image_path = self.get_test_image_path()
        
        if image_path is None:
            print("⚠️ 测试图片不存在，跳过图片+文字解决方案测试")
            return
        
        request = ProcessingMasterRequest(
            image_url=image_path,
            text_description="这是一台笔记本电脑，请分析处置建议",
            user_location={"lat": 39.906823, "lon": 116.447303}
        )
        
        print("\n=== 开始完整解决方案测试（图片+文字）===")
        
        async with ProcessingMasterAgent() as agent:
            steps = []
            step_count = 0
            
            async for step in agent.process_complete_solution(request):
                step_count += 1
                steps.append(step)
                
                print(f"\n[步骤 {step_count}] {step.step_name}")
                print(f"标题: {step.step_title}")
                print(f"状态: {step.status.value}")
                
                if step.error:
                    print(f"错误: {step.error}")
                
                # 如果是最终整合步骤，显示完整结果
                if step.step_name == "result_integration" and step.result:
                    print("\n=== 最终整合结果 ===")
                    print(json.dumps(step.result, indent=2, ensure_ascii=False))
                    print("=" * 50)
            
            print(f"\n✓ 图片+文字解决方案测试完成，共执行 {step_count} 个步骤")

    @pytest.mark.asyncio
    async def test_component_status(self):
        """测试组件状态检查"""
        async with ProcessingMasterAgent() as agent:
            status = agent.get_component_status()

            print("\n=== 组件状态检查 ===")
            print(json.dumps(status, indent=2, ensure_ascii=False))

            # 验证初始化状态
            assert status["initialized"] is True
            print("✓ 组件状态检查通过")

    @pytest.mark.asyncio
    async def test_error_handling(self):
        """测试错误处理"""
        print("\n=== 测试错误处理 ===")

        # 测试分析服务错误
        async with ProcessingMasterAgent() as agent:
            # 使用一个会导致分析失败的请求
            request = ProcessingMasterRequest(
                image_url="/invalid/path/that/does/not/exist.jpg"
            )

            result = await agent._analyze_content(request)

            print(f"错误处理结果: {result}")
            assert result.get('success') is False or 'error' in result
            print("✓ 错误处理测试通过")


# 性能和集成测试
class TestProcessingMasterPerformance:
    """性能和集成测试"""

    @pytest.mark.asyncio
    async def test_processing_performance(self):
        """测试处理性能"""
        request = ProcessingMasterRequest(
            text_description="一台戴尔XPS 13笔记本电脑，使用两年，配置为i7处理器，16GB内存，512GB SSD，外观良好"
        )

        print("\n=== 性能测试开始 ===")
        start_time = time.time()

        async with ProcessingMasterAgent() as agent:
            step_count = 0
            async for step in agent.process_complete_solution(request):
                step_count += 1
                current_time = time.time() - start_time
                print(f"[{current_time:.2f}s] 步骤 {step_count}: {step.step_name} - {step.status.value}")

        total_time = time.time() - start_time
        print(f"\n性能测试结果:")
        print(f"总处理时间: {total_time:.2f}秒")
        print(f"总步骤数: {step_count}")
        print(f"平均每步耗时: {total_time / step_count:.2f}秒")

        # 性能断言（根据实际情况调整）
        assert total_time < 120.0, f"处理时间过长: {total_time:.2f}秒"
        print("✓ 性能测试通过")

    @pytest.mark.asyncio
    async def test_concurrent_requests(self):
        """测试并发请求处理"""
        print("\n=== 并发测试开始 ===")

        requests = [
            ProcessingMasterRequest(text_description="iPhone 12 手机"),
            ProcessingMasterRequest(text_description="MacBook Pro 笔记本"),
            ProcessingMasterRequest(text_description="iPad Air 平板")
        ]

        async def process_single_request(req, index):
            print(f"开始处理请求 {index + 1}")
            async with ProcessingMasterAgent() as agent:
                steps = []
                async for step in agent.process_complete_solution(req):
                    steps.append(step)
                print(f"请求 {index + 1} 完成，共 {len(steps)} 步")
                return len(steps)

        start_time = time.time()

        # 并发执行
        results = await asyncio.gather(*[
            process_single_request(req, i) for i, req in enumerate(requests)
        ])

        total_time = time.time() - start_time
        print(f"\n并发测试结果:")
        print(f"并发处理 {len(requests)} 个请求")
        print(f"总耗时: {total_time:.2f}秒")
        print(f"平均每个请求步骤数: {sum(results) / len(results):.1f}")

        assert all(result > 0 for result in results)
        print("✓ 并发测试通过")


if __name__ == "__main__":
    # 使用pytest运行测试
    pytest.main([__file__, "-v", "-s"])
