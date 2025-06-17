"""
蓝心视觉大模型服务测试

测试VIVO BlueLM Vision API的图片分析功能
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


class TestLanxinVisionService:
    """蓝心视觉服务测试类"""
    
    @pytest.fixture
    def service(self):
        """创建服务实例"""
        return LanxinService()
    
    @pytest.fixture
    def test_image_path(self):
        """测试图片路径"""
        return str(Path(__file__).parent / "测试图片.png")
    
    def test_service_initialization(self, service):
        """测试服务初始化"""
        assert service.app_id is not None
        assert service.app_key is not None
        assert service.base_url is not None
        print(f"✅ 视觉服务初始化成功")
        print(f"   App ID: {service.app_id}")
        print(f"   API URL: {service.base_url}")
    
    def test_image_file_exists(self, test_image_path):
        """测试图片文件是否存在"""
        assert Path(test_image_path).exists(), f"测试图片不存在: {test_image_path}"
        
        # 获取图片信息
        file_size = Path(test_image_path).stat().st_size
        print(f"✅ 测试图片文件检查通过")
        print(f"   路径: {test_image_path}")
        print(f"   大小: {file_size / 1024:.2f} KB")
    
    @pytest.mark.asyncio
    async def test_analyze_image_basic(self, service, test_image_path):
        """测试基础图片分析功能"""
        print("\n=== 测试基础图片分析 ===")
        
        try:
            result = await service.analyze_image(test_image_path)
            
            # 验证返回结果结构
            assert isinstance(result, dict), "返回结果应为字典"
            assert "category" in result, "结果应包含category字段"
            assert "description" in result, "结果应包含description字段"
            
            print(f"✅ 图片分析成功")
            print(f"   图片路径: {test_image_path}")
            print(f"   分析结果:")
            for key, value in result.items():
                if isinstance(value, list):
                    print(f"     {key}: {', '.join(str(v) for v in value)}")
                else:
                    print(f"     {key}: {value}")
            
            return result
            
        except Exception as e:
            print(f"❌ 图片分析失败: {e}")
            raise
    
    @pytest.mark.asyncio
    async def test_error_handling(self, service):
        """测试错误处理"""
        print("\n=== 测试错误处理 ===")
        
        # 测试不存在的图片文件
        try:
            result = await service.analyze_image("/不存在的/图片.jpg")
            print(f"✅ 不存在文件处理: {result.get('description', '无描述')}")
            assert result.get('category') == '错误'
        except Exception as e:
            print(f"⚠️ 不存在文件处理异常: {e}")
        
        # 测试空路径
        try:
            result = await service.analyze_image("")
            print(f"✅ 空路径处理: {result.get('description', '无描述')}")
        except Exception as e:
            print(f"⚠️ 空路径处理异常: {e}")
    
    @pytest.mark.asyncio
    async def test_json_parsing(self, service, test_image_path):
        """测试JSON解析"""
        print("\n=== 测试JSON解析 ===")
        
        try:
            result = await service.analyze_image(test_image_path)
            
            # 验证JSON结构
            required_fields = ["category", "sub_category", "description"]
            for field in required_fields:
                assert field in result, f"缺少必需字段: {field}"
            
            print(f"✅ JSON解析测试通过")
            print(f"   类别: {result.get('category', '未知')}")
            print(f"   子类别: {result.get('sub_category', '未知')}")
            print(f"   描述长度: {len(str(result.get('description', '')))}")
            
            return result
            
        except Exception as e:
            print(f"❌ JSON解析测试失败: {e}")
            raise
    
    @pytest.mark.asyncio
    async def test_performance(self, service, test_image_path):
        """测试性能"""
        print("\n=== 测试性能 ===")
        
        import time
        
        start_time = time.time()
        
        try:
            result = await service.analyze_image(test_image_path)
            end_time = time.time()
            duration = end_time - start_time
            
            print(f"✅ 性能测试完成")
            print(f"   响应时间: {duration:.2f}秒")
            print(f"   分析结果类别: {result.get('category', '未知')}")
            
            # 性能断言（应该在合理时间内完成）
            assert duration < 30, f"响应时间过长: {duration:.2f}秒"
            
        except Exception as e:
            print(f"❌ 性能测试失败: {e}")
            raise
    
    @pytest.mark.asyncio
    async def test_all_vision_functions(self, service, test_image_path):
        """综合视觉功能测试"""
        print("\n" + "="*60)
        print("🔍 开始蓝心视觉服务综合功能测试")
        print("="*60)
        
        try:
            # 运行所有测试
            await self.test_analyze_image_basic(service, test_image_path)
            await self.test_error_handling(service)
            await self.test_json_parsing(service, test_image_path)
            await self.test_performance(service, test_image_path)
            
            print("\n" + "="*60)
            print("🎉 所有视觉功能测试通过！")
            print("="*60)
            
        except Exception as e:
            print(f"\n❌ 综合视觉测试失败: {e}")
            raise
        
        finally:
            # 确保关闭客户端
            await service.client.aclose()


# 单独运行的函数
async def run_vision_quick_test():
    """快速视觉测试函数"""
    print("🔍 快速视觉API连接测试")
    print("-" * 40)
    
    service = LanxinService()
    test_image_path = str(Path(__file__).parent / "测试图片.png")
    
    try:
        # 检查图片文件
        if not Path(test_image_path).exists():
            print(f"❌ 测试图片不存在: {test_image_path}")
            return
        
        print("1. 测试图片文件检查...")
        file_size = Path(test_image_path).stat().st_size
        print(f"   图片大小: {file_size / 1024:.2f} KB")
        
        print("\n2. 测试基础图片分析...")
        result = await service.analyze_image(test_image_path)
        print(f"   分析结果: {result.get('category', '未知')}")
        print(f"   描述: {result.get('description', '无描述')[:100]}...")
        
        print("\n✅ 快速视觉测试完成！")
        
    except Exception as e:
        print(f"\n❌ 快速视觉测试失败: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        await service.client.aclose()


if __name__ == "__main__":
    # 如果直接运行此文件，执行快速测试
    asyncio.run(run_vision_quick_test()) 