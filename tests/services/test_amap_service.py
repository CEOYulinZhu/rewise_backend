"""
高德地图服务真实API测试

测试高德地图API的真实搜索功能和筛选功能
"""

import pytest
import traceback

from app.services.amap_service import AmapService, search_nearby_places
from app.models.amap_models import AmapSearchRequest


@pytest.mark.asyncio
async def test_real_api_call():
    """
    真实API调用测试（使用真实的高德地图API）
    
    测试坐标：113.365382,23.133827（广州某地）
    测试关键词：家电回收
    """
    try:
        print("\n=== 开始真实API调用测试 ===")
        print(f"测试坐标: 113.365382,23.133827")
        print(f"测试关键词: 家电回收")
        
        pois = await search_nearby_places(
            location="113.365382,23.133827",
            keywords="家电回收",
            radius=50000,  # 50公里范围
            page_size=20
        )
        
        print(f"\n搜索结果数量: {len(pois)}")
        
        # 检查结果
        assert isinstance(pois, list)
        
        if pois:
            print("\n=== POI详细信息 ===")
            for i, poi in enumerate(pois, 1):
                print(f"\n--- POI {i} ---")
                print(f"ID: {poi.id}")
                print(f"名称: {poi.name}")
                print(f"地址: {poi.address}")
                print(f"坐标: {poi.location}")
                print(f"经度: {poi.longitude}")
                print(f"纬度: {poi.latitude}")
                print(f"类型: {poi.type}")
                print(f"类型编码: {poi.typecode}")
                print(f"省份: {poi.pname}")
                print(f"城市: {poi.cityname}")
                print(f"区县: {poi.adname}")
                
                # 距离信息
                if poi.distance_meters is not None:
                    print(f"距离: {poi.distance_meters:.1f}米")
                if poi.distance_formatted:
                    print(f"格式化距离: {poi.distance_formatted}")
                
                # 营业信息
                if poi.tel:
                    print(f"电话: {poi.tel}")
                if poi.opentime_today:
                    print(f"今日营业时间: {poi.opentime_today}")
                if poi.opentime_week:
                    print(f"营业时间描述: {poi.opentime_week}")
                
                # 图片信息
                if poi.photos:
                    print(f"图片数量: {len(poi.photos)}")
                    for j, photo in enumerate(poi.photos, 1):
                        print(f"  图片{j} - 标题: {photo.title}")
                        print(f"  图片{j} - URL: {photo.url}")
                else:
                    print("无图片信息")
                
                # 验证基本属性
                assert hasattr(poi, 'name')
                assert hasattr(poi, 'location')
                assert hasattr(poi, 'address')
                assert poi.name is not None
                assert poi.location is not None
                assert poi.address is not None
                
                # 验证距离属性
                assert hasattr(poi, 'distance_meters')
                assert hasattr(poi, 'distance_formatted')
                if poi.distance_meters is not None:
                    assert poi.distance_meters >= 0  # 距离应该非负
                    assert isinstance(poi.distance_meters, float)
                if poi.distance_formatted is not None:
                    assert isinstance(poi.distance_formatted, str)
                    assert ('米' in poi.distance_formatted or '公里' in poi.distance_formatted)
        else:
            print("未找到相关POI，可能是因为:")
            print("1. 该区域没有相关的家电回收点")
            print("2. 关键词匹配度不高")
            print("3. API配置或网络问题")
            
            # 尝试不带关键词的搜索，看看该区域有什么
            print("\n=== 尝试搜索该区域的所有POI ===")
            all_pois = await search_nearby_places(
                location="113.365382,23.133827",
                radius=1000,  # 缩小到1公里
                page_size=5
            )
            
            print(f"该区域POI数量: {len(all_pois)}")
            if all_pois:
                for i, poi in enumerate(all_pois[:3], 1):  # 只显示前3个
                    print(f"{i}. {poi.name} - {poi.type}")
        
        print("\n=== 真实API调用测试完成 ===")
        
    except Exception as e:
        print(f"\n真实API调用失败: {e}")
        print(f"错误类型: {type(e).__name__}")
        print(f"详细错误信息:\n{traceback.format_exc()}")
        pytest.fail(f"真实API调用失败: {e}")


@pytest.mark.asyncio
async def test_real_api_service_direct():
    """
    直接使用AmapService进行真实API调用测试
    """
    try:
        print("\n=== 使用AmapService直接调用测试 ===")
        
        service = AmapService()
        
        # 先获取原始API响应数据
        search_request = AmapSearchRequest(
            location="113.365382,23.133827",
            keywords="家电回收",
            radius=50000,
            page_size=20
        )
        
        params = search_request.to_params_dict(service.api_key)
        print(f"请求参数: {params}")
        
        # 直接调用_make_request来看原始响应
        raw_data = await service._make_request(params)
        print(f"\n=== 原始API响应数据 ===")
        print(f"响应状态: {raw_data.get('status')}")
        print(f"响应信息: {raw_data.get('info')}")
        print(f"响应代码: {raw_data.get('infocode')}")
        print(f"POI数量: {raw_data.get('count')}")
        
        if raw_data.get('pois') and len(raw_data['pois']) > 0:
            first_poi = raw_data['pois'][0]
            print(f"\n=== 第一个POI的原始数据结构 ===")
            print(f"POI ID: {first_poi.get('id')}")
            print(f"POI 名称: {first_poi.get('name')}")
            print(f"POI 地址: {first_poi.get('address')}")
            
            # 检查是否有business字段
            if 'business' in first_poi:
                print(f"包含business字段: {first_poi['business']}")
            else:
                print("不包含business字段")
            
            # 检查根级别的字段
            root_level_fields = ['tel', 'opentime_today', 'opentime_week']
            for field in root_level_fields:
                if field in first_poi:
                    print(f"根级别包含{field}: {first_poi[field]}")
                else:
                    print(f"根级别不包含{field}")
            
            # 打印所有可用字段
            print(f"POI包含的所有字段: {list(first_poi.keys())}")
        
        # 然后测试我们的解析逻辑
        response = await service.search_around(
            location="113.365382,23.133827",
            keywords="家电回收",
            radius=50000,
            page_size=20
        )
        
        print(f"\n=== 解析后的响应 ===")
        print(f"API响应状态: {response.status}")
        print(f"API响应信息: {response.info}")
        print(f"API响应代码: {response.infocode}")
        print(f"是否成功: {response.is_success}")
        print(f"POI数量: {response.poi_count}")
        print(f"实际POI列表长度: {len(response.pois)}")
        
        if not response.is_success:
            print(f"API调用失败: {response.info}")
            
        # 验证响应结构
        assert hasattr(response, 'status')
        assert hasattr(response, 'info')
        assert hasattr(response, 'pois')
        
        print("=== AmapService直接调用测试完成 ===")
        
    except Exception as e:
        print(f"\nAmapService直接调用失败: {e}")
        print(f"详细错误信息:\n{traceback.format_exc()}")
        pytest.fail(f"AmapService直接调用失败: {e}")


@pytest.mark.asyncio
async def test_real_api_call_with_filtering():
    """
    真实API调用测试（使用真实的高德地图API）并测试筛选功能
    """
    try:
        print("\n=== 开始真实API调用筛选测试 ===")
        print(f"测试坐标: 113.365382,23.133827")
        print(f"测试关键词: 家电回收")
        
        # 测试不启用筛选
        print("\n--- 测试不启用筛选 ---")
        pois_unfiltered = await search_nearby_places(
            location="113.365382,23.133827",
            keywords="家电回收",
            radius=50000,
            page_size=20,
            enable_filter=False
        )
        
        print(f"未筛选结果数量: {len(pois_unfiltered)}")
        if pois_unfiltered:
            print("未筛选的POI列表:")
            for i, poi in enumerate(pois_unfiltered, 1):
                print(f"  {i}. {poi.name}")
        
        # 测试启用筛选
        print("\n--- 测试启用筛选 ---")
        pois_filtered = await search_nearby_places(
            location="113.365382,23.133827",
            keywords="家电回收",
            radius=50000,
            page_size=20,
            enable_filter=True
        )
        
        print(f"筛选后结果数量: {len(pois_filtered)}")
        if pois_filtered:
            print("筛选后的POI列表:")
            for i, poi in enumerate(pois_filtered, 1):
                print(f"  {i}. {poi.name}")
                print(f"     地址: {poi.address}")
                print(f"     类型: {poi.type}")
                if poi.distance_formatted:
                    print(f"     距离: {poi.distance_formatted}")
        
        # 验证筛选效果
        print(f"\n筛选效果: {len(pois_unfiltered)} -> {len(pois_filtered)}")
        
        # 检查筛选后的结果是否都包含相关关键词
        if pois_filtered:
            print("\n=== 筛选结果验证 ===")
            for poi in pois_filtered:
                search_text = f"{poi.name} {poi.address} {poi.type}".lower()
                has_appliance = any(keyword in search_text for keyword in ["家电", "电器", "电机", "空调", "冰箱", "洗衣机", "电视"])
                has_recycling = any(keyword in search_text for keyword in ["回收", "收购", "废品", "再生", "循环"])
                print(f"POI: {poi.name}")
                print(f"  包含家电关键词: {has_appliance}")
                print(f"  包含回收关键词: {has_recycling}")
                print(f"  筛选有效: {has_appliance and has_recycling}")
        
        print("\n=== 真实API调用筛选测试完成 ===")
        
    except Exception as e:
        print(f"\n真实API调用筛选测试失败: {e}")
        print(f"详细错误信息:\n{traceback.format_exc()}")
        pytest.fail(f"真实API调用筛选测试失败: {e}")


@pytest.mark.asyncio
async def test_distance_calculation():
    """
    测试距离计算功能
    """
    try:
        print("\n=== 测试距离计算功能 ===")
        
        # 使用一个固定的坐标进行测试
        user_location = "113.365382,23.133827"
        print(f"用户位置: {user_location}")
        
        # 搜索周边POI
        pois = await search_nearby_places(
            location=user_location,
            radius=10000,  # 10公里范围
            page_size=10
        )
        
        print(f"找到 {len(pois)} 个POI")
        
        if pois:
            print("\n=== 距离信息验证 ===")
            for i, poi in enumerate(pois, 1):
                print(f"\n--- POI {i}: {poi.name} ---")
                print(f"坐标: {poi.location}")
                
                # 验证距离字段存在
                assert hasattr(poi, 'distance_meters'), "POI应该包含distance_meters字段"
                assert hasattr(poi, 'distance_formatted'), "POI应该包含distance_formatted字段"
                
                if poi.distance_meters is not None:
                    print(f"距离(米): {poi.distance_meters:.1f}")
                    assert poi.distance_meters >= 0, "距离应该非负"
                    assert poi.distance_meters <= 10000, "距离应该在搜索半径内"
                    
                if poi.distance_formatted is not None:
                    print(f"格式化距离: {poi.distance_formatted}")
                    assert isinstance(poi.distance_formatted, str), "格式化距离应该是字符串"
                    assert ('米' in poi.distance_formatted or '公里' in poi.distance_formatted), \
                           "格式化距离应该包含单位"
                    
                # 验证距离和格式化距离的一致性
                if poi.distance_meters is not None and poi.distance_formatted is not None:
                    if poi.distance_meters < 1000:
                        assert '米' in poi.distance_formatted, "小于1000米应该显示米单位"
                    else:
                        assert '公里' in poi.distance_formatted, "大于等于1000米应该显示公里单位"
                
                # 手动验证距离计算（使用第一个POI）
                if i == 1:
                    from app.utils.distance_utils import calculate_distance_from_location
                    manual_distance = calculate_distance_from_location(user_location, poi.location)
                    
                    print(f"手动计算距离: {manual_distance:.1f}米")
                    
                    if poi.distance_meters is not None:
                        # 允许小的浮点误差
                        distance_diff = abs(poi.distance_meters - manual_distance)
                        assert distance_diff < 1.0, f"距离计算误差过大: {distance_diff}米"
                        print("距离计算验证通过 ✓")
        
        print("\n=== 距离计算功能测试完成 ===")
        
    except Exception as e:
        print(f"\n距离计算功能测试失败: {e}")
        print(f"详细错误信息:\n{traceback.format_exc()}")
        pytest.fail(f"距离计算功能测试失败: {e}")


@pytest.mark.asyncio
async def test_distance_sorting():
    """
    测试距离排序功能
    """
    try:
        print("\n=== 测试距离排序功能 ===")
        
        user_location = "113.365382,23.133827"
        print(f"用户位置: {user_location}")
        
        # 测试关键词搜索的距离排序
        print("\n--- 测试关键词搜索的距离排序 ---")
        pois_sorted = await search_nearby_places(
            location=user_location,
            keywords="家电回收",
            radius=50000,
            page_size=15,
            enable_filter=True,
            sort_by_distance=True
        )
        
        # 测试关键词搜索不排序
        print("\n--- 测试关键词搜索不排序 ---")
        pois_unsorted = await search_nearby_places(
            location=user_location,
            keywords="家电回收",
            radius=50000,
            page_size=15,
            enable_filter=True,
            sort_by_distance=False
        )
        
        print(f"排序结果数量: {len(pois_sorted)}")
        print(f"不排序结果数量: {len(pois_unsorted)}")
        
        # 验证排序结果
        if pois_sorted:
            print("\n=== 验证距离排序效果 ===")
            
            # 检查距离是否递增
            distances = [poi.distance_meters for poi in pois_sorted if poi.distance_meters is not None]
            
            if len(distances) > 1:
                print("距离序列（前10个）:")
                for i, distance in enumerate(distances[:10], 1):
                    formatted_dist = f"{distance/1000:.1f}公里" if distance >= 1000 else f"{distance:.0f}米"
                    print(f"  {i}. {formatted_dist}")
                
                # 验证距离是否递增
                is_sorted = all(distances[i] <= distances[i+1] for i in range(len(distances)-1))
                assert is_sorted, "距离应该按递增顺序排列"
                print("✓ 距离排序验证通过")
                
                # 显示排序后的POI信息
                print("\n排序后的POI（前5个）:")
                for i, poi in enumerate(pois_sorted[:5], 1):
                    print(f"  {i}. {poi.name}")
                    if poi.distance_formatted:
                        print(f"     距离: {poi.distance_formatted}")
                    print(f"     地址: {poi.address}")
            else:
                print("找到的POI数量不足，无法验证排序效果")
        
        # 测试无关键词搜索的距离排序
        print("\n--- 测试无关键词搜索的距离排序 ---")
        pois_no_keyword = await search_nearby_places(
            location=user_location,
            radius=5000,
            page_size=10,
            sort_by_distance=True
        )
        
        print(f"无关键词搜索结果数量: {len(pois_no_keyword)}")
        
        if pois_no_keyword:
            # 验证无关键词搜索也按距离排序
            distances_no_keyword = [poi.distance_meters for poi in pois_no_keyword if poi.distance_meters is not None]
            
            if len(distances_no_keyword) > 1:
                is_sorted_no_keyword = all(distances_no_keyword[i] <= distances_no_keyword[i+1] 
                                         for i in range(len(distances_no_keyword)-1))
                assert is_sorted_no_keyword, "无关键词搜索的距离也应该按递增顺序排列"
                print("✓ 无关键词搜索距离排序验证通过")
        
        print("\n=== 距离排序功能测试完成 ===")
        
    except Exception as e:
        print(f"\n距离排序功能测试失败: {e}")
        print(f"详细错误信息:\n{traceback.format_exc()}")
        pytest.fail(f"距离排序功能测试失败: {e}")


@pytest.mark.asyncio
async def test_real_api_all_recycling_types():
    """
    测试所有回收类型的真实API调用
    """
    try:
        print("\n=== 测试所有回收类型 ===")
        
        recycling_types = ["家电回收", "电脑回收", "旧衣回收", "纸箱回收"]
        location = "113.365382,23.133827"
        
        for recycling_type in recycling_types:
            print(f"\n--- 测试 {recycling_type} ---")
            
            pois = await search_nearby_places(
                location=location,
                keywords=recycling_type,
                radius=50000,
                page_size=20,
                enable_filter=True
            )
            
            print(f"{recycling_type} 搜索结果: {len(pois)} 个")
            
            if pois:
                print("找到的POI:")
                for i, poi in enumerate(pois[:3], 1):  # 只显示前3个
                    print(f"  {i}. {poi.name}")
                    print(f"     地址: {poi.address}")
                    print(f"     类型: {poi.type}")
                    if poi.distance_formatted:
                        print(f"     距离: {poi.distance_formatted}")
            else:
                print(f"  未找到 {recycling_type} 相关POI")
        
        print("\n=== 所有回收类型测试完成 ===")
        
    except Exception as e:
        print(f"\n所有回收类型测试失败: {e}")
        print(f"详细错误信息:\n{traceback.format_exc()}")
        pytest.fail(f"所有回收类型测试失败: {e}")


if __name__ == "__main__":
    # 运行测试
    pytest.main([__file__, "-v", "-s"])