"""
二手交易平台协调器Agent测试模块
"""

import pytest
import asyncio
import sys
import time
import json
from pathlib import Path
from typing import Any, Dict

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from app.agents.secondhand_coordinator.agent import SecondhandTradingAgent
from app.models.secondhand_coordinator_models import (
    SecondhandTradingRequest, 
    SecondhandTradingResponse,
    SecondhandTradingDataConverter
)


def print_separator(title: str = "", width: int = 70):
    """打印分隔线"""
    if title:
        print(f"\n{'=' * width}")
        print(f" {title} ".center(width))
        print('=' * width)
    else:
        print('=' * width)


def print_response_data(response: SecondhandTradingResponse, title: str = "返回数据"):
    """打印完整的响应数据"""
    print_separator(f"📤 {title}")
    
    # 转换为字典
    response_dict = response.to_dict()
    
    # JSON格式输出
    try:
        def serialize_obj(obj):
            if hasattr(obj, 'dict'):
                return obj.dict()
            elif hasattr(obj, '__dict__'):
                return {k: serialize_obj(v) for k, v in obj.__dict__.items()}
            elif isinstance(obj, dict):
                return {k: serialize_obj(v) for k, v in obj.items()}
            elif isinstance(obj, list):
                return [serialize_obj(item) for item in obj]
            return obj
        
        serializable = serialize_obj(response_dict)
        json_str = json.dumps(serializable, ensure_ascii=False, indent=2)
        
        print("🔍 完整JSON数据:")
        print("-" * 60)
        print(json_str)
        print("-" * 60)
        
    except Exception as e:
        print(f"⚠️ JSON序列化失败: {e}")
        print(f"📊 字典数据: {response_dict}")
    
    # 关键信息汇总
    print(f"\n🎯 关键字段:")
    print(f"   success: {response.success}")
    print(f"   source: {response.source}")
    error_msg = response.error if response.error else 'null'
    print(f"   error: {error_msg}")
    
    if response.has_search_results():
        print(f"   搜索结果: 成功，共 {response.get_total_products()} 个商品")
    else:
        print(f"   搜索结果: 失败或无结果")
    
    if response.has_content_results():
        title = response.get_generated_title() or "无标题"
        print(f"   文案生成: 成功")
        print(f"   生成标题: {title}")
    else:
        print(f"   文案生成: 失败或无结果")
    
    if response.processing_metadata:
        meta = response.processing_metadata
        print(f"   处理模式: {meta.processing_mode}")
        print(f"   处理耗时: {meta.processing_time_seconds:.3f}秒")
        print(f"   搜索状态: {'成功' if meta.search_success else '失败'}")
        print(f"   文案状态: {'成功' if meta.content_success else '失败'}")


class TestSecondhandTradingAgent:
    """测试SecondhandTradingAgent类"""
    
    @pytest.fixture
    def sample_data(self):
        """测试数据"""
        return {
            "category": "电子产品",
            "sub_category": "智能手机",
            "brand": "苹果",
            "model": "iPhone 12",
            "condition": "八成新",
            "description": "iPhone 12，黑色，128GB，使用两年，外观良好",
            "keywords": ["iPhone", "苹果", "手机"]
        }
    
    @pytest.mark.asyncio
    async def test_basic_functionality(self, sample_data):
        """测试基础功能"""
        print_separator("🧪 基础功能测试")
        print(f"📝 输入: {sample_data}")
        
        agent = SecondhandTradingAgent()
        try:
            start_time = time.time()
            result = await agent.coordinate_trading(
                analysis_result=sample_data,
                max_results_per_platform=5,
                enable_parallel=True
            )
            elapsed = time.time() - start_time
            print(f"⏱️ 耗时: {elapsed:.2f}秒")
            
            # 验证基本结构
            assert isinstance(result.success, bool)
            assert result.source == "secondhand_trading_coordinator"
            
            # 打印完整返回数据
            print_response_data(result, "基础功能返回数据")
            print("✅ 基础功能测试通过")
            
        finally:
            await agent.close()
    
    @pytest.mark.asyncio
    async def test_request_object(self, sample_data):
        """测试请求对象模式"""
        print_separator("🧪 请求对象测试")
        
        # 创建请求对象
        request = SecondhandTradingDataConverter.create_request(
            analysis_result=sample_data,
            max_results_per_platform=3,
            include_xianyu=True,
            include_aihuishou=False,
            enable_parallel=True
        )
        print(f"📝 请求对象: {request.dict()}")
        
        agent = SecondhandTradingAgent()
        try:
            start_time = time.time()
            result = await agent.coordinate_with_request(request)
            elapsed = time.time() - start_time
            print(f"⏱️ 耗时: {elapsed:.2f}秒")
            
            # 验证结果
            assert isinstance(result.success, bool)
            
            # 打印完整返回数据
            print_response_data(result, "请求对象返回数据")
            print("✅ 请求对象测试通过")
            
        finally:
            await agent.close()
    
    @pytest.mark.asyncio
    async def test_parallel_vs_serial(self, sample_data):
        """测试并行vs串行"""
        print_separator("🧪 并行串行对比测试")
        
        agent = SecondhandTradingAgent()
        try:
            # 并行处理
            print("\n⚡ 并行处理:")
            start = time.time()
            parallel_result = await agent.coordinate_trading(
                analysis_result=sample_data,
                max_results_per_platform=3,
                enable_parallel=True
            )
            parallel_time = time.time() - start
            print(f"   耗时: {parallel_time:.2f}秒")
            
            # 串行处理
            print("\n🔄 串行处理:")
            start = time.time()
            serial_result = await agent.coordinate_trading(
                analysis_result=sample_data,
                max_results_per_platform=3,
                enable_parallel=False
            )
            serial_time = time.time() - start
            print(f"   耗时: {serial_time:.2f}秒")
            
            # 性能对比
            if parallel_time > 0 and serial_time > 0:
                speedup = serial_time / parallel_time
                print(f"\n📊 性能提升: {speedup:.2f}x")
            
            # 打印两种结果
            print_response_data(parallel_result, "并行处理返回数据")
            print_response_data(serial_result, "串行处理返回数据")
            print("✅ 并行串行测试通过")
            
        finally:
            await agent.close()
    
    @pytest.mark.asyncio
    async def test_error_handling(self):
        """测试错误处理"""
        print_separator("🧪 错误处理测试")
        
        agent = SecondhandTradingAgent()
        try:
            # 空输入测试
            print("\n❌ 空输入测试:")
            try:
                result = await agent.coordinate_trading(analysis_result=None)  # type: ignore
                print_response_data(result, "空输入返回数据")
                assert result.success is False
            except Exception as e:
                print(f"   异常: {e}")
            
            # 无效格式测试
            print("\n❌ 无效格式测试:")
            try:
                result = await agent.coordinate_trading(analysis_result="invalid")  # type: ignore
                print_response_data(result, "无效格式返回数据")
                assert result.success is False
            except Exception as e:
                print(f"   异常: {e}")
            
            # 空字典测试
            print("\n📋 空字典测试:")
            result = await agent.coordinate_trading(analysis_result={})
            print_response_data(result, "空字典返回数据")
            
            print("✅ 错误处理测试通过")
            
        finally:
            await agent.close()
    
    @pytest.mark.asyncio
    async def test_concurrent_requests(self, sample_data):
        """测试并发请求"""
        print_separator("🧪 并发请求测试")
        
        agent = SecondhandTradingAgent()
        try:
            num_requests = 3
            print(f"🔄 发起 {num_requests} 个并发请求")
            
            tasks = [
                agent.coordinate_trading(
                    analysis_result=sample_data,
                    max_results_per_platform=2
                )
                for _ in range(num_requests)
            ]
            
            start = time.time()
            results = await asyncio.gather(*tasks, return_exceptions=True)
            total_time = time.time() - start
            
            # 分析结果
            successful = []
            failed = []
            
            for i, result in enumerate(results):
                if isinstance(result, Exception):
                    print(f"   请求#{i+1}: 异常 - {result}")
                    failed.append(result)
                else:
                    print(f"   请求#{i+1}: 成功 - {result.success}")
                    successful.append(result)
            
            print(f"⏱️ 总耗时: {total_time:.2f}秒")
            print(f"📊 成功率: {len(successful)}/{num_requests}")
            
            # 显示第一个成功结果
            if successful:
                print_response_data(successful[0], "并发请求示例返回数据")
            
            assert len(successful) >= num_requests * 0.7
            print("✅ 并发请求测试通过")
            
        finally:
            await agent.close()
    
    @pytest.mark.asyncio
    async def test_performance(self, sample_data):
        """测试性能基准"""
        print_separator("🧪 性能基准测试")
        
        agent = SecondhandTradingAgent()
        try:
            start = time.time()
            result = await agent.coordinate_trading(
                analysis_result=sample_data,
                max_results_per_platform=5
            )
            response_time = time.time() - start
            
            # 性能评级
            if response_time < 5:
                grade = "优秀 🥇"
            elif response_time < 10:
                grade = "良好 🥈"
            elif response_time < 20:
                grade = "一般 🥉"
            else:
                grade = "需优化 ⚠️"
            
            print(f"⏱️ 响应时间: {response_time:.2f}秒")
            print(f"🎖️ 性能等级: {grade}")
            
            assert response_time < 30.0, f"响应时间过长: {response_time:.2f}秒"
            
            # 打印完整返回数据
            print_response_data(result, "性能测试返回数据")
            print("✅ 性能测试通过")
            
        finally:
            await agent.close()
    
    def test_data_converter(self, sample_data):
        """测试数据转换器"""
        print_separator("🧪 数据转换器测试")
        
        # 创建请求
        request = SecondhandTradingDataConverter.create_request(
            analysis_result=sample_data,
            max_results_per_platform=10
        )
        print(f"📝 请求对象: {request.dict()}")
        
        # 创建元数据
        metadata = SecondhandTradingDataConverter.create_processing_metadata(
            processing_mode="parallel",
            processing_time_seconds=2.5,
            search_success=True,
            content_success=True
        )
        print(f"📊 元数据对象: {metadata.dict()}")
        
        # 创建响应
        response = SecondhandTradingDataConverter.create_response(
            success=True,
            analysis_result=sample_data,
            processing_metadata=metadata
        )
        print(f"📤 响应对象: {response.dict()}")
        
        # 验证
        assert request.analysis_result == sample_data
        assert metadata.processing_mode == "parallel"
        assert response.success is True
        
        print("✅ 数据转换器测试通过")
    
    @pytest.mark.asyncio
    async def test_context_manager(self, sample_data):
        """测试上下文管理器"""
        print_separator("🧪 上下文管理器测试")
        
        async with SecondhandTradingAgent() as agent:
            result = await agent.coordinate_trading(
                analysis_result=sample_data,
                max_results_per_platform=2
            )
            
            print_response_data(result, "上下文管理器返回数据")
            assert isinstance(result.success, bool)
            print("✅ 上下文管理器测试通过")


if __name__ == "__main__":
    print_separator("🧪 二手交易协调器Agent测试套件")
    print("💡 运行命令: pytest tests/agents/secondhand_coordinator/test_agent.py -v -s")
    print_separator() 