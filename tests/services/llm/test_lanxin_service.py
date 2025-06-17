"""
蓝心大模型服务真实API测试

测试VIVO BlueLM API的真实调用功能
"""

import pytest
import asyncio
import json
import os
import sys
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from app.services.llm.lanxin_service import LanxinService


class TestLanxinServiceReal:
    """蓝心服务真实API测试类"""
    
    @pytest.fixture
    def service(self):
        """创建服务实例"""
        return LanxinService()
    
    def test_service_initialization(self, service):
        """测试服务初始化"""
        # 验证配置是否正确加载
        assert service.app_id == "2025251747"
        assert service.app_key == "wmuPTuICigJsKdYU"
        assert "vivo.com.cn" in service.base_url
        assert service.text_model == "vivo-BlueLM-TB-Pro"
        print(f"✅ 服务初始化成功")
        print(f"   App ID: {service.app_id}")
        print(f"   API URL: {service.base_url}")
        print(f"   模型: {service.text_model}")
    
    def test_auth_headers_generation(self, service):
        """测试鉴权头部生成"""
        from urllib.parse import urlparse
        
        # 模拟请求参数
        parsed_url = urlparse(service.base_url)
        uri = parsed_url.path
        query_params = {"requestId": "test-request-id"}
        
        headers = service._get_auth_headers("POST", uri, query_params)
        
        # 验证必需的头部存在
        required_headers = [
            "Content-Type",
            "X-AI-GATEWAY-APP-ID",
            "X-AI-GATEWAY-TIMESTAMP", 
            "X-AI-GATEWAY-NONCE",
            "X-AI-GATEWAY-SIGNED-HEADERS",
            "X-AI-GATEWAY-SIGNATURE"
        ]
        
        for header in required_headers:
            assert header in headers, f"缺少必需的头部: {header}"
        
        # 验证头部值的格式
        assert headers["Content-Type"] == "application/json"
        assert headers["X-AI-GATEWAY-APP-ID"] == "2025251747"
        assert headers["X-AI-GATEWAY-SIGNED-HEADERS"] == "x-ai-gateway-app-id;x-ai-gateway-timestamp;x-ai-gateway-nonce"
        
        print(f"✅ 鉴权头部生成测试通过")
        for key, value in headers.items():
            if key == "X-AI-GATEWAY-SIGNATURE":
                print(f"   {key}: {value[:16]}...")
            else:
                print(f"   {key}: {value}")
    
    @pytest.mark.asyncio
    async def test_analyze_text_simple(self, service):
        """测试简单文本分析"""
        print("\n=== 测试简单文本分析 ===")
        
        test_text = "一台黑色苹果iPhone手机"
        
        try:
            result = await service.analyze_text(test_text)
            
            # 验证返回结果结构
            assert isinstance(result, dict), "返回结果应为字典"
            assert "category" in result, "结果应包含category字段"
            assert "description" in result, "结果应包含description字段"
            
            print(f"✅ 文本分析成功")
            print(f"   输入: {test_text}")
            print(f"   结果: {json.dumps(result, ensure_ascii=False, indent=2)}")
            
            return result
            
        except Exception as e:
            print(f"❌ 文本分析失败: {e}")
            raise
    
    @pytest.mark.asyncio
    async def test_analyze_text_detailed(self, service):
        """测试详细文本分析"""
        print("\n=== 测试详细文本分析 ===")
        
        test_text = "一台2020年购买的联想ThinkPad笔记本电脑，14寸屏幕，Intel i5处理器，8GB内存，256GB固态硬盘，外观九成新，功能正常，电池续航约4小时"
        
        try:
            result = await service.analyze_text(test_text)
            
            # 验证返回结果
            assert isinstance(result, dict), "返回结果应为字典"
            
            print(f"✅ 详细文本分析成功")
            print(f"   输入: {test_text}")
            print(f"   结果:")
            for key, value in result.items():
                print(f"     {key}: {value}")
            
            return result
            
        except Exception as e:
            print(f"❌ 详细文本分析失败: {e}")
            raise
    
    @pytest.mark.asyncio
    async def test_generate_disposal_recommendations(self, service):
        """测试处置建议生成"""
        print("\n=== 测试处置建议生成 ===")
        
        # 模拟物品信息
        item_info = {
            "category": "电器",
            "sub_category": "笔记本电脑",
            "brand": "联想",
            "condition": "九成新",
            "material": "塑料和金属",
            "color": "黑色",
            "keywords": ["ThinkPad", "笔记本", "联想"],
            "description": "联想ThinkPad笔记本电脑，黑色，九成新",
            "estimated_age": "3年",
            "special_features": "商务办公本"
        }
        
        knowledge = {
            "recycling_methods": ["电子产品回收点", "品牌以旧换新"],
            "environmental_impact": "减少电子垃圾，保护环境",
            "creative_ideas": ["改造为家用服务器", "拆解零件再利用"]
        }
        
        market_data = {
            "avg_price": "2000-3000元",
            "demand": "中等",
            "best_platforms": ["闲鱼", "转转", "京东拍拍"],
            "price_trend": "稳定下降"
        }
        
        try:
            result = await service.generate_disposal_recommendations(
                item_info, knowledge, market_data
            )
            
            # 验证返回结果结构
            assert isinstance(result, dict), "返回结果应为字典"
            
            print(f"✅ 处置建议生成成功")
            print(f"   输入物品: {item_info['description']}")
            print(f"   建议结果:")
            
            # 打印结果
            for key, value in result.items():
                if isinstance(value, (list, dict)):
                    print(f"     {key}: {json.dumps(value, ensure_ascii=False)}")
                else:
                    print(f"     {key}: {value}")
            
            return result
            
        except Exception as e:
            print(f"❌ 处置建议生成失败: {e}")
            raise
    
    @pytest.mark.asyncio
    async def test_chat_with_text(self, service):
        """测试通用文本对话"""
        print("\n=== 测试通用文本对话 ===")
        
        # 测试多轮对话
        messages = [
            {"role": "user", "content": "你好，我有一台旧手机想要处理，你能给我一些建议吗？"},
            {"role": "assistant", "content": "你好！我很乐意帮助你处理旧手机。请告诉我这台手机的具体情况，比如品牌、型号、使用年限和当前状态？"},
            {"role": "user", "content": "是一台iPhone 12，用了2年，功能正常，外观有轻微磨损"}
        ]
        
        try:
            result = await service.chat_with_text(
                messages,
                system_prompt="你是一个专业的物品处置顾问，能够为用户提供环保、经济的物品处理建议。",
                temperature=0.7,
                max_tokens=500
            )
            
            # 验证返回结果
            assert isinstance(result, str), "返回结果应为字符串"
            assert len(result) > 0, "返回结果不应为空"
            
            print(f"✅ 文本对话成功")
            print(f"   对话轮数: {len(messages)}")
            print(f"   最后输入: {messages[-1]['content']}")
            print(f"   AI回复: {result}")
            
            return result
            
        except Exception as e:
            print(f"❌ 文本对话失败: {e}")
            raise
    
    @pytest.mark.asyncio
    async def test_error_handling(self, service):
        """测试错误处理"""
        print("\n=== 测试错误处理 ===")
        
        # 测试空文本
        try:
            result = await service.analyze_text("")
            print(f"✅ 空文本处理: {result.get('description', '无描述')}")
        except Exception as e:
            print(f"⚠️ 空文本处理异常: {e}")
        
        # 测试过长文本（超过模型限制）
        try:
            long_text = "这是一个很长的文本。" * 1000  # 创建一个很长的文本
            result = await service.analyze_text(long_text)
            print(f"✅ 长文本处理: {result.get('description', '无描述')[:100]}...")
        except Exception as e:
            print(f"⚠️ 长文本处理异常: {e}")
    
    @pytest.mark.asyncio
    async def test_performance(self, service):
        """测试性能"""
        print("\n=== 测试性能 ===")
        
        import time
        
        test_texts = [
            "苹果手机",
            "联想笔记本电脑",
            "小米充电宝"
        ]
        
        start_time = time.time()
        
        for i, text in enumerate(test_texts):
            try:
                result = await service.analyze_text(text)
                print(f"   测试 {i+1}: {text} -> {result.get('category', '未知')}")
            except Exception as e:
                print(f"   测试 {i+1} 失败: {e}")
        
        end_time = time.time()
        total_time = end_time - start_time
        avg_time = total_time / len(test_texts)
        
        print(f"✅ 性能测试完成")
        print(f"   总时间: {total_time:.2f}秒")
        print(f"   平均时间: {avg_time:.2f}秒/请求")
    
    @pytest.mark.asyncio
    async def test_all_functions(self, service):
        """综合功能测试"""
        print("\n" + "="*60)
        print("🚀 开始蓝心服务综合功能测试")
        print("="*60)
        
        try:
            # 运行所有测试
            await self.test_analyze_text_simple(service)
            await self.test_analyze_text_detailed(service)
            await self.test_generate_disposal_recommendations(service)
            await self.test_chat_with_text(service)
            await self.test_error_handling(service)
            await self.test_performance(service)
            
            print("\n" + "="*60)
            print("🎉 所有功能测试通过！")
            print("="*60)
            
        except Exception as e:
            print(f"\n❌ 综合测试失败: {e}")
            raise
        
        finally:
            # 确保关闭客户端
            await service.client.aclose()


# 单独运行的函数
async def run_quick_test():
    """快速测试函数"""
    print("🔧 快速API连接测试")
    print("-" * 40)
    
    service = LanxinService()
    
    try:
        # 测试基本功能
        print("1. 测试服务初始化...")
        print(f"   App ID: {service.app_id}")
        print(f"   API URL: {service.base_url}")
        
        print("\n2. 测试鉴权头部生成...")
        from urllib.parse import urlparse
        parsed_url = urlparse(service.base_url)
        uri = parsed_url.path
        query_params = {"requestId": "test-request-id"}
        headers = service._get_auth_headers("POST", uri, query_params)
        print(f"   头部数量: {len(headers)}")
        print(f"   APP ID: {headers.get('X-AI-GATEWAY-APP-ID')}")
        
        print("\n4. 测试文本分析...")
        result = await service.analyze_text("一台旧手机")
        print(f"   分析结果: {result.get('category', '未知')}")
        
        print("\n✅ 快速测试完成！")
        
    except Exception as e:
        print(f"\n❌ 快速测试失败: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        await service.client.aclose()


if __name__ == "__main__":
    # 如果直接运行此文件，执行快速测试
    asyncio.run(run_quick_test()) 