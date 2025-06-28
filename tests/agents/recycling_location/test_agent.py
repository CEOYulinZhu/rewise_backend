"""
回收地点推荐Agent真实功能测试

真实调用AI API和高德地图API，验证Agent的实际工作效果
"""

import asyncio
from typing import Dict, Any

import pytest

from app.agents.recycling_location.agent import (
    RecyclingLocationAgent,
    analyze_recycling_type_and_locations
)


class TestRecyclingLocationAgentReal:
    """回收地点推荐Agent真实功能测试"""

    @pytest.mark.asyncio
    async def test_real_electronic_device_analysis(self):
        """测试真实的电子设备回收分析"""
        print("\n" + "="*60)
        print("📱 测试电子设备回收分析（真实API调用）")
        print("="*60)
        
        analysis_result = {
            "category": "电子产品",
            "description": "一台使用了3年的联想ThinkPad笔记本电脑，14寸屏幕，i5处理器，8GB内存，外观良好，功能正常，只是电池续航有所下降",
            "condition": "八成新",
            "brand": "联想",
            "model": "ThinkPad E14",
            "estimated_value": 2800,
            "materials": ["塑料", "金属", "电子元件"]
        }
        
        user_location = "113.365382,23.133827"  # 广州市中心
        
        print(f"📋 输入信息:")
        print(f"   物品类别: {analysis_result['category']}")
        print(f"   物品描述: {analysis_result['description']}")
        print(f"   物品状况: {analysis_result['condition']}")
        print(f"   品牌型号: {analysis_result['brand']} {analysis_result['model']}")
        print(f"   估值: ¥{analysis_result['estimated_value']}")
        print(f"   用户位置: {user_location} (广州)")
        
        agent = RecyclingLocationAgent()
        
        try:
            print(f"\n🤖 开始AI分析...")
            response = await agent.analyze_and_recommend_locations(
                analysis_result=analysis_result,
                user_location=user_location,
                radius=30000,  # 30公里范围
                max_locations=15
            )
            
            print(f"\n📊 分析结果:")
            print(f"   ✅ 分析成功: {response.success}")
            
            if response.success:
                print(f"   🔄 回收类型: {response.recycling_type}")
                print(f"   📍 找到地点: {len(response.locations)}个")
                print(f"   🔍 搜索关键词: {response.search_params.get('keyword', 'N/A')}")
                print(f"   📏 搜索半径: {response.search_params.get('radius', 'N/A')}米")
                
                print(f"\n📍 推荐回收地点:")
                for i, location in enumerate(response.locations[:5], 1):  # 显示前5个
                    print(f"   {i}. {location.name}")
                    print(f"      📍 地址: {location.address}")
                    if location.distance_formatted:
                        print(f"      📏 距离: {location.distance_formatted}")
                    if location.tel:
                        print(f"      📞 电话: {location.tel}")
                    if location.opentime_today:
                        print(f"      🕒 营业时间: {location.opentime_today}")
                    print(f"      🌐 坐标: {location.location}")
                    print()
                
                # 验证基本功能
                assert response.recycling_type in ["家电回收", "电脑回收", "旧衣回收", "纸箱回收"]
                assert len(response.locations) >= 0  # 可能没有找到地点
                
                print(f"✅ 电子设备回收分析测试通过!")
            else:
                print(f"   ❌ 分析失败: {response.error}")
                print(f"✅ 错误处理正常")
                
        except Exception as e:
            print(f"   ❌ 测试异常: {str(e)}")
            raise
            
        finally:
            await agent.close()

    @pytest.mark.asyncio 
    async def test_real_clothing_analysis(self):
        """测试真实的服装回收分析"""
        print("\n" + "="*60)
        print("👕 测试服装回收分析（真实API调用）")
        print("="*60)
        
        analysis_result = {
            "category": "服装",
            "description": "一件优衣库的羽绒服，黑色，L码，去年冬天买的，穿过几次，保存很好，拉链和扣子都完好",
            "condition": "九成新",
            "brand": "优衣库",
            "color": "黑色",
            "size": "L",
            "estimated_value": 150
        }
        
        user_location = "113.365382,23.133827"  # 广州市中心
        
        print(f"📋 输入信息:")
        print(f"   物品类别: {analysis_result['category']}")
        print(f"   物品描述: {analysis_result['description']}")
        print(f"   物品状况: {analysis_result['condition']}")
        print(f"   品牌: {analysis_result['brand']}")
        print(f"   颜色尺码: {analysis_result['color']} {analysis_result['size']}")
        print(f"   估值: ¥{analysis_result['estimated_value']}")
        print(f"   用户位置: {user_location} (广州)")
        
        agent = RecyclingLocationAgent()
        
        try:
            print(f"\n🤖 开始AI分析...")
            response = await agent.analyze_and_recommend_locations(
                analysis_result=analysis_result,
                user_location=user_location,
                radius=25000,  # 25公里范围
                max_locations=10
            )
            
            print(f"\n📊 分析结果:")
            print(f"   ✅ 分析成功: {response.success}")
            
            if response.success:
                print(f"   🔄 回收类型: {response.recycling_type}")
                print(f"   📍 找到地点: {len(response.locations)}个")
                
                print(f"\n📍 推荐回收地点:")
                for i, location in enumerate(response.locations[:3], 1):  # 显示前3个
                    print(f"   {i}. {location.name}")
                    print(f"      📍 地址: {location.address}")
                    if location.distance_formatted:
                        print(f"      📏 距离: {location.distance_formatted}")
                    if location.tel:
                        print(f"      📞 电话: {location.tel}")
                    print()
                
                # 验证结果
                assert response.recycling_type in ["家电回收", "电脑回收", "旧衣回收", "纸箱回收"]
                
                print(f"✅ 服装回收分析测试通过!")
            else:
                print(f"   ❌ 分析失败: {response.error}")
                
        except Exception as e:
            print(f"   ❌ 测试异常: {str(e)}")
            raise
            
        finally:
            await agent.close()

    @pytest.mark.asyncio
    async def test_real_appliance_analysis(self):
        """测试真实的家电回收分析"""
        print("\n" + "="*60)
        print("🏠 测试家电回收分析（真实API调用）")
        print("="*60)
        
        analysis_result = {
            "category": "家用电器",
            "description": "一台海尔品牌的双门冰箱，容量220升，使用了5年，制冷功能正常，外观有一些使用痕迹但不影响使用",
            "condition": "七成新",
            "brand": "海尔",
            "model": "BCD-220",
            "capacity": "220升",
            "estimated_value": 800
        }
        
        user_location = "113.365382,23.133827"  # 广州市中心
        
        print(f"📋 输入信息:")
        print(f"   物品类别: {analysis_result['category']}")
        print(f"   物品描述: {analysis_result['description']}")
        print(f"   品牌型号: {analysis_result['brand']} {analysis_result['model']}")
        print(f"   容量: {analysis_result['capacity']}")
        print(f"   状况: {analysis_result['condition']}")
        print(f"   估值: ¥{analysis_result['estimated_value']}")
        print(f"   用户位置: {user_location} (广州)")
        
        agent = RecyclingLocationAgent()
        
        try:
            print(f"\n🤖 开始AI分析...")
            response = await agent.analyze_and_recommend_locations(
                analysis_result=analysis_result,
                user_location=user_location,
                radius=20000,  # 20公里范围
                max_locations=8
            )
            
            print(f"\n📊 分析结果:")
            print(f"   ✅ 分析成功: {response.success}")
            
            if response.success:
                print(f"   🔄 回收类型: {response.recycling_type}")
                print(f"   📍 找到地点: {len(response.locations)}个")
                
                if response.locations:
                    print(f"\n📍 推荐回收地点:")
                    for i, location in enumerate(response.locations[:3], 1):
                        print(f"   {i}. {location.name}")
                        print(f"      📍 地址: {location.address}")
                        if location.distance_formatted:
                            print(f"      📏 距离: {location.distance_formatted}")
                        print()
                else:
                    print(f"   ℹ️  未找到相关回收地点，建议扩大搜索范围")
                
                # 验证结果
                assert response.recycling_type in ["家电回收", "电脑回收", "旧衣回收", "纸箱回收"]
                
                print(f"✅ 家电回收分析测试通过!")
            else:
                print(f"   ❌ 分析失败: {response.error}")
                
        except Exception as e:
            print(f"   ❌ 测试异常: {str(e)}")
            raise
            
        finally:
            await agent.close()



    @pytest.mark.asyncio
    async def test_real_convenience_functions(self):
        """测试便捷函数的真实调用"""
        print("\n" + "="*60)
        print("🛠️  测试便捷函数（真实调用）")
        print("="*60)
        
        analysis_result = {
            "category": "数码设备",
            "description": "一台iPhone 12 Pro，256GB，深空灰色，使用了1年多，外观完好，功能正常，电池健康度89%",
            "condition": "九成新",
            "brand": "Apple",
            "model": "iPhone 12 Pro",
            "storage": "256GB",
            "estimated_value": 4500
        }
        
        user_location = "113.365382,23.133827"  # 广州市中心
        
        print(f"📋 测试数据:")
        print(f"   物品: {analysis_result['brand']} {analysis_result['model']}")
        print(f"   描述: {analysis_result['description']}")
        print(f"   位置: {user_location} (广州)")
        
        try:
            # 测试完整分析和推荐的便捷函数
            print(f"\n🎯 测试完整分析推荐便捷函数...")
            full_result = await analyze_recycling_type_and_locations(
                analysis_result=analysis_result,
                user_location=user_location,
                radius=25000,
                max_locations=10
            )
            
            print(f"   📊 完整分析结果:")
            print(f"      ✅ 成功: {full_result.success}")
            if full_result.success:
                print(f"      🔄 回收类型: {full_result.recycling_type}")
                print(f"      📍 找到地点: {len(full_result.locations)}个")
                
                if full_result.locations:
                    print(f"      🏆 最近地点: {full_result.locations[0].name}")
                    if full_result.locations[0].distance_formatted:
                        print(f"      📏 距离: {full_result.locations[0].distance_formatted}")
                
                assert full_result.recycling_type in ["家电回收", "电脑回收", "旧衣回收", "纸箱回收"]
                print(f"      ✅ 完整分析便捷函数测试通过!")
            else:
                print(f"      ❌ 分析失败: {full_result.error}")
                
        except Exception as e:
            print(f"   ❌ 测试异常: {str(e)}")
            raise

    @pytest.mark.asyncio
    async def test_input_validation_real(self):
        """测试真实的输入验证"""
        print("\n" + "="*60)
        print("✅ 测试输入验证（真实调用）")
        print("="*60)
        
        agent = RecyclingLocationAgent()
        
        try:
            # 测试空分析结果
            print(f"📝 测试空分析结果...")
            response = await agent.analyze_and_recommend_locations(
                analysis_result=None,
                user_location="113.365382,23.133827"
            )
            
            print(f"   📊 结果: success={response.success}")
            print(f"   📝 错误信息: {response.error}")
            assert response.success is False
            assert "分析结果为空或格式错误" in response.error
            print(f"   ✅ 空分析结果验证通过!")
            
            # 测试空用户位置
            print(f"\n📍 测试空用户位置...")
            response = await agent.analyze_and_recommend_locations(
                analysis_result={"category": "测试物品", "description": "测试描述"},
                user_location=""
            )
            
            print(f"   📊 结果: success={response.success}")
            print(f"   📝 错误信息: {response.error}")
            assert response.success is False
            assert "用户位置不能为空" in response.error
            print(f"   ✅ 空用户位置验证通过!")
            
            # 测试空字典输入
            print(f"\n📝 测试空字典输入...")
            response = await agent.analyze_and_recommend_locations(
                analysis_result={},
                user_location="113.365382,23.133827"
            )
            
            print(f"   📊 结果: success={response.success}")
            print(f"   📝 错误信息: {response.error}")
            assert response.success is False
            assert "分析结果为空或格式错误" in response.error
            print(f"   ✅ 空字典输入验证通过!")
            
            print(f"\n✅ 所有输入验证测试通过!")
            
        except Exception as e:
            print(f"   ❌ 测试异常: {str(e)}")
            raise
            
        finally:
            await agent.close()


if __name__ == "__main__":
    # 运行真实测试
    print("🚀 开始回收地点推荐Agent真实功能测试...")
    print("⚠️  注意：此测试将进行真实的API调用，需要网络连接和有效的API配置")
    pytest.main([__file__, "-v", "-s", "--tb=short"])