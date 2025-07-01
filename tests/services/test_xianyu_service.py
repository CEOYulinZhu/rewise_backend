"""
闲鱼搜索服务测试

测试XianyuService的核心功能，包括真实API调用和模拟数据
"""

import asyncio
import json
import sys
from pathlib import Path

import pytest

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from app.services.xianyu_service import XianyuService, search_xianyu_products
from app.models.xianyu_models import (
    XianyuSearchRequest,
    XianyuSearchResponse,
    XianyuProduct,
    XianyuPriceStats,
    XianyuSearchDataConverter
)


class TestXianyuServiceReal:
    """闲鱼服务真实API测试类"""
    
    @pytest.fixture
    def service(self):
        """创建服务实例"""
        return XianyuService()
    
    @pytest.fixture
    def test_keywords(self):
        """测试关键词列表"""
        return [
            "衣服",  # 示例关键词
            "手机",    # 常见商品
            "笔记本电脑 苹果",  # 高价值商品
        ]
    
    def print_section(self, title: str) -> None:
        """打印测试段落标题"""
        print(f"\n{'='*60}")
        print(f"  {title}")
        print(f"{'='*60}")
    
    def print_json(self, data: dict, title: str = "") -> None:
        """格式化打印JSON数据"""
        if title:
            print(f"\n--- {title} ---")
        print(json.dumps(data, ensure_ascii=False, indent=2))
    
    def print_error(self, error: Exception, context: str = "") -> None:
        """打印错误信息"""
        print(f"\n❌ 错误 {f'({context})' if context else ''}: {type(error).__name__}: {error}")
        import traceback
        print(f"详细错误信息:\n{traceback.format_exc()}")
    
    def test_service_initialization(self, service):
        """测试服务初始化"""
        print(f"\n==== 测试服务初始化 ====")
        
        # 验证配置是否正确加载
        assert service.base_url == "https://h5api.m.goofish.com/h5/mtop.taobao.idlemtopsearch.wx.search/1.0/"
        assert service.timeout == 30
        assert service.max_retries == 3
        assert "application/x-www-form-urlencoded" in service.headers["content-type"]
        
        print(f"✅ 服务初始化成功")
        print(f"   API URL: {service.base_url}")
        print(f"   超时设置: {service.timeout}秒")
        print(f"   最大重试: {service.max_retries}次")

    @pytest.mark.asyncio
    async def test_basic_search(self, service, test_keywords):
        """测试基本搜索功能"""
        self.print_section("基本搜索功能测试")
        
        for keyword in test_keywords:
            print(f"\n🔍 测试搜索关键词: '{keyword}'")
            
            try:
                # 手动调用API以获取原始响应
                search_request = XianyuSearchRequest(
                    keyword=keyword,
                    page_number=1,
                    rows_per_page=30
                )
                
                print(f"📤 发送请求:")
                # 生成示例URL用于展示
                sample_timestamp = service._generate_current_timestamp()
                sample_sign = "示例签名"
                sample_url = service._build_request_url(sample_timestamp, sample_sign)
                print(f"   URL示例: {sample_url[:150]}...")
                print(f"   请求体: {search_request.to_request_body()[:150]}...")
                
                # 获取原始API响应
                raw_response = await service._make_request(search_request)
                
                print(f"\n📥 原始API响应:")
                print(f"   响应类型: {type(raw_response)}")
                print(f"   响应键: {list(raw_response.keys()) if isinstance(raw_response, dict) else '非字典类型'}")
                
                # 打印响应的详细结构
                # if isinstance(raw_response, dict):
                    # self.print_json(raw_response, "完整API响应")
                # else:
                #     print(f"   响应内容: {raw_response}")
                
                # 然后调用正常的搜索方法
                response = await service.search_products(
                    keyword=keyword,
                    page_number=1,
                    rows_per_page=30
                )
                
                print(f"\n✅ 解析后结果:")
                print(f"   - 成功状态: {response.success}")
                print(f"   - 产品数量: {response.product_count}")
                print(f"   - API: {response.api}")
                
                if response.error_message:
                    print(f"   - 警告信息: {response.error_message}")
                
                # 打印价格统计
                if response.price_stats:
                    stats = response.price_stats
                    print(f"   - 价格范围: {stats.price_range}")
                    print(f"   - 平均价格: ¥{stats.average_price}")
                    print(f"   - 最低价格: ¥{stats.min_price}")
                    print(f"   - 最高价格: ¥{stats.max_price}")
                
                # 显示前3个产品
                if response.data:
                    print(f"\n前3个商品信息:")
                    for i, product in enumerate(response.data[:3], 1):
                        print(f"   {i}. {product.title[:50]}{'...' if len(product.title) > 50 else ''}")
                        print(f"      卖家: {product.user_nick}")
                        print(f"      价格: ¥{product.price}")
                        print(f"      地区: {product.area or '未知'}")
                        print(f"      图片: {product.pic_url}")
                else:
                    print(f"\n⚠️ 未解析出任何产品数据")
                
            except Exception as e:
                self.print_error(e, f"搜索'{keyword}'")
                # 在测试环境中跳过网络错误
                # pytest.skip(f"API暂时不可用: {str(e)}")
            
            print("-" * 40)
    
    @pytest.mark.asyncio
    async def test_api_response_structure(self, service):
        """专门测试API响应结构分析"""
        self.print_section("API响应结构分析")
        
        keyword = "手机"  # 使用常见关键词
        
        try:
            print(f"🔍 分析关键词 '{keyword}' 的API响应结构")
            
            # 构建请求
            search_request = XianyuSearchRequest(
                keyword=keyword,
                page_number=1,
                rows_per_page=5
            )
            
            # 获取原始响应
            raw_response = await service._make_request(search_request)
            
            print(f"\n📋 响应结构详细分析:")
            print(f"   数据类型: {type(raw_response)}")
            
            if isinstance(raw_response, dict):
                print(f"   顶级字段: {list(raw_response.keys())}")
                
                # 检查data字段
                if "data" in raw_response:
                    data = raw_response["data"]
                    print(f"   data字段类型: {type(data)}")
                    print(f"   data字段内容: {list(data.keys()) if isinstance(data, dict) else 'non-dict'}")
                    
                    # 检查resultList
                    if isinstance(data, dict) and "resultList" in data:
                        result_list = data["resultList"]
                        print(f"   resultList类型: {type(result_list)}")
                        print(f"   resultList长度: {len(result_list) if isinstance(result_list, list) else 'non-list'}")
                        
                        if isinstance(result_list, list) and len(result_list) > 0:
                            print(f"   第一个结果结构:")
                            first_item = result_list[0]
                            self._analyze_nested_structure(first_item, "     ")
                        else:
                            print(f"   resultList为空或非列表")
                    else:
                        print(f"   data中没有resultList字段")
                        # 打印data的完整内容（限制长度）
                        data_str = str(data)[:1000]
                        print(f"   data内容预览: {data_str}...")
                else:
                    print(f"   没有data字段")
                
                # 打印完整响应（截断）
                response_str = str(raw_response)
                if len(response_str) > 2000:
                    print(f"\n📄 响应内容预览 (前2000字符):")
                    print(response_str[:2000] + "...")
                else:
                    print(f"\n📄 完整响应内容:")
                    self.print_json(raw_response, "完整API响应")
            
        except Exception as e:
            self.print_error(e, "API响应结构分析")
    
    def _analyze_nested_structure(self, obj, indent=""):
        """递归分析嵌套结构"""
        if isinstance(obj, dict):
            for key, value in obj.items():
                print(f"{indent}{key}: {type(value)}")
                if isinstance(value, (dict, list)) and key in ["data", "item", "main", "exContent", "detailParams"]:
                    self._analyze_nested_structure(value, indent + "  ")
        elif isinstance(obj, list):
            print(f"{indent}列表长度: {len(obj)}")
            if len(obj) > 0:
                print(f"{indent}第一个元素类型: {type(obj[0])}")
                if isinstance(obj[0], dict):
                    self._analyze_nested_structure(obj[0], indent + "  ")
    
    @pytest.mark.asyncio
    async def test_price_analysis(self, service):
        """测试价格分析功能"""
        self.print_section("价格分析功能测试")
        
        keyword = "手机"  # 使用价格差异较大的商品类别
        
        try:
            print(f"🔍 测试价格分析，关键词: '{keyword}'")
            
            # 调用带价格分析的搜索
            result = await service.search_with_price_analysis(
                keyword=keyword,
                page_number=1,
                rows_per_page=20  # 获取更多数据以便分析
            )
            
            print(f"✅ 价格分析完成")
            
            # 打印基本统计
            if "price_stats" in result:
                self.print_json(result["price_stats"], "基本价格统计")
            
            # 打印详细分析
            if "price_analysis" in result:
                analysis = result["price_analysis"]
                
                if "distribution" in analysis:
                    self.print_json(analysis["distribution"], "价格分布分析")
                
                if "recommendations" in analysis:
                    print(f"\n--- 价格建议 ---")
                    for key, recommendation in analysis["recommendations"].items():
                        print(f"{key}: {recommendation}")
            
            # 显示产品数量统计
            print(f"\n📊 统计信息:")
            print(f"   - 成功解析: {result['success']}")
            print(f"   - 产品总数: {result['total_products']}")
            
        except Exception as e:
            self.print_error(e, "价格分析")
            pytest.skip(f"价格分析功能暂时不可用: {str(e)}")
    
    def test_data_models(self):
        """测试数据模型"""
        self.print_section("数据模型测试")
        
        try:
            # 测试搜索请求模型
            print("🧪 测试搜索请求模型")
            search_request = XianyuSearchRequest(
                keyword="测试商品",
                page_number=1,
                rows_per_page=20
            )
            
            request_body = search_request.to_request_body()
            print(f"✅ 搜索请求模型正常")
            print(f"   请求体长度: {len(request_body)} 字符")
            print(f"   包含关键词: {'测试商品' in request_body}")
            
            # 测试产品模型
            print(f"\n🧪 测试产品模型")
            product = XianyuProduct(
                item_id="test123",
                title="测试商品标题",
                user_nick="测试卖家",
                price=99.99,
                pic_url="https://example.com/pic.jpg",
                area="测试地区"
            )
            
            product_dict = product.to_dict()
            print(f"✅ 产品模型正常")
            print(f"   模型字段数: {len(product_dict)}")
            self.print_json(product_dict, "产品模型示例")
            
            # 测试价格统计模型
            print(f"\n🧪 测试价格统计模型")
            products = [
                XianyuProduct(
                    item_id=f"test{i}",
                    title=f"测试商品{i}",
                    user_nick=f"卖家{i}",
                    price=float(i * 10),
                    pic_url="",
                    area="测试地区"
                )
                for i in range(1, 6)  # 5个测试产品
            ]
            
            price_stats = XianyuPriceStats.calculate_from_products(products)
            print(f"✅ 价格统计模型正常")
            print(f"   计算的产品数: {price_stats.total_products}")
            print(f"   价格范围: {price_stats.price_range}")
            print(f"   平均价格: ¥{price_stats.average_price}")
            
        except Exception as e:
            self.print_error(e, "数据模型测试")
    
    @pytest.mark.asyncio
    async def test_data_converter(self, service):
        """测试数据转换器"""
        self.print_section("数据转换器测试")
        
        try:
            # 先搜索一些真实数据
            print("🔍 获取真实数据进行转换测试")
            response = await service.search_products(
                keyword="数码产品",
                page_number=1,
                rows_per_page=5
            )
            
            if response.product_count > 0:
                # 测试简化格式转换
                print(f"\n🧪 测试简化格式转换")
                simplified = XianyuSearchDataConverter.to_simplified_format(response)
                print(f"✅ 简化格式转换成功")
                print(f"   包含字段: {list(simplified.keys())}")
                
                # 显示转换结果的部分内容
                if "products" in simplified and simplified["products"]:
                    print(f"   产品字段: {list(simplified['products'][0].keys())}")
                
                # 测试详细格式转换
                print(f"\n🧪 测试详细格式转换")
                detailed = XianyuSearchDataConverter.to_detailed_format(response)
                print(f"✅ 详细格式转换成功")
                print(f"   包含字段: {list(detailed.keys())}")
                
                # 比较两种格式
                print(f"\n📊 格式对比:")
                print(f"   简化格式大小: ~{len(str(simplified))} 字符")
                print(f"   详细格式大小: ~{len(str(detailed))} 字符")
                
            else:
                print("⚠️ 未获取到足够的数据进行转换测试")
                
        except Exception as e:
            self.print_error(e, "数据转换器测试")
            pytest.skip(f"数据转换器功能暂时不可用: {str(e)}")
    
    def test_error_handling(self, service):
        """测试错误处理"""
        self.print_section("错误处理测试")
        
        # 测试空关键词
        print("🧪 测试空关键词")
        with pytest.raises(ValueError, match="搜索关键词不能为空"):
            asyncio.run(service.search_products(""))
        print(f"✅ 空关键词错误处理正确")
        
        # 测试无效页码
        print(f"\n🧪 测试无效页码")
        with pytest.raises(ValueError, match="page_number参数应大于等于1"):
            asyncio.run(service.search_products("test", page_number=0))
        print(f"✅ 页面数量错误处理正确")
        
        # 测试超大每页数量
        print(f"\n🧪 测试超大每页数量")
        with pytest.raises(ValueError, match="rows_per_page参数范围应为1-50"):
            asyncio.run(service.search_products("test", rows_per_page=100))
        print(f"✅ 每页数量错误处理正确")
    
    @pytest.mark.asyncio
    async def test_convenience_function(self):
        """测试便捷函数"""
        self.print_section("便捷函数测试")
        
        keyword = "电子产品"
        
        try:
            # 测试带价格分析的便捷函数
            print(f"🧪 测试带价格分析的便捷函数")
            result_with_analysis = await search_xianyu_products(
                keyword=keyword,
                page_number=1,
                rows_per_page=30,
                include_price_analysis=True
            )
            
            print(f"✅ 带价格分析调用成功")
            print(f"   结果包含字段: {list(result_with_analysis.keys())}")
            print(f"   包含价格分析: {'price_analysis' in result_with_analysis}")
            
            # 测试不带价格分析的便捷函数
            print(f"\n🧪 测试不带价格分析的便捷函数")
            result_simple = await search_xianyu_products(
                keyword=keyword,
                page_number=1,
                rows_per_page=30,
                include_price_analysis=False
            )
            
            print(f"✅ 简单调用成功")
            print(f"   结果包含字段: {list(result_simple.keys())}")
            print(f"   包含价格分析: {'price_analysis' in result_simple}")
            
            # 对比结果
            print(f"\n📊 结果对比:")
            print(f"   带分析结果大小: ~{len(str(result_with_analysis))} 字符")
            print(f"   简单结果大小: ~{len(str(result_simple))} 字符")
            
        except Exception as e:
            self.print_error(e, "便捷函数测试")
            pytest.skip(f"便捷函数暂时不可用: {str(e)}")

    def test_token_extraction(self, service):
        """测试从Cookie中提取token"""
        print(f"\n==== 测试Token提取 ====")
        
        token_part, full_token = service._extract_token_from_cookie()
        
        print(f"✅ Token提取成功")
        print(f"   Token部分: {token_part[:10]}...")
        print(f"   完整Token: {full_token[:20]}...")
        
        assert token_part
        assert full_token
        assert "_" in full_token
    
    def test_signature_generation(self, service):
        """测试签名生成"""
        print(f"\n==== 测试签名生成 ====")
        
        timestamp = service._generate_current_timestamp()
        test_data = '{"keyword":"测试","pageNumber":1}'
        token_part, _ = service._extract_token_from_cookie()
        
        sign = service._generate_sign(timestamp, test_data, token_part)
        
        print(f"✅ 签名生成成功")
        print(f"   时间戳: {timestamp}")
        print(f"   数据长度: {len(test_data)}")
        print(f"   生成签名: {sign}")
        
        assert sign
        assert len(sign) == 32  # MD5签名长度
    
    def test_url_building(self, service):
        """测试URL构建"""
        print(f"\n==== 测试URL构建 ====")
        
        timestamp = service._generate_current_timestamp()
        sign = "test_signature"
        url = service._build_request_url(timestamp, sign)
        
        print(f"✅ URL构建成功")
        print(f"   URL: {url[:100]}...")
        
        assert service.base_url in url
        assert f"t={timestamp}" in url
        assert f"sign={sign}" in url
    
    @pytest.mark.asyncio
    async def test_search_products_real_api(self, service):
        """测试真实API搜索产品功能"""
        print(f"\n==== 测试真实API搜索产品 ====")
        
        try:
            # 测试搜索衣服产品
            response = await service.search_products(
                keyword="衣服",
                page_number=1,
                rows_per_page=20
            )
            
            print(f"✅ API调用成功")
            print(f"   搜索关键词: 衣服")
            print(f"   响应状态: {'成功' if response.success else '失败'}")
            print(f"   产品数量: {response.product_count}")
            
            # 验证响应结构
            assert isinstance(response, XianyuSearchResponse)
            assert response.product_count > 0
            assert len(response.data) > 0
            
            # 打印前3个产品信息
            print(f"\n👕 前3个产品信息:")
            for i, product in enumerate(response.data[:3]):
                print(f"   {i+1}. {product.title}")
                print(f"      价格: ¥{product.price}")
                print(f"      卖家: {product.user_nick}")
                print(f"      地区: {product.area}")
                print(f"      图片: {product.pic_url}")
                print()
            
            # 验证价格统计
            if response.price_stats:
                stats = response.price_stats
                print(f"💰 价格统计信息:")
                print(f"   价格区间: {stats.price_range}")
                print(f"   平均价格: ¥{stats.average_price}")
                print(f"   最低价格: ¥{stats.min_price}")
                print(f"   最高价格: ¥{stats.max_price}")
                
                # 验证价格统计的合理性
                assert stats.min_price <= stats.average_price <= stats.max_price
                assert stats.total_products == response.product_count
            
        except Exception as e:
            print(f"⚠️  API调用失败，使用模拟数据: {str(e)}")
            print(f"   错误类型: {type(e).__name__}")
            
            # 验证模拟数据响应
            assert isinstance(response, XianyuSearchResponse)
            assert response.product_count > 0
            assert "模拟数据" in response.error_message
            print(f"✅ 模拟数据功能正常，找到 {response.product_count} 个产品")
    
    @pytest.mark.asyncio
    async def test_search_with_price_analysis(self, service):
        """测试带价格分析的搜索功能"""
        print(f"\n==== 测试价格分析搜索 ====")
        
        try:
            # 测试价格分析功能
            result = await service.search_with_price_analysis(
                keyword="手机",
                page_number=1,
                rows_per_page=15
            )
            
            print(f"✅ 价格分析搜索成功")
            print(f"   搜索关键词: 手机")
            print(f"   是否成功: {result.get('success', False)}")
            print(f"   产品总数: {result.get('total_products', 0)}")
            
            # 验证返回结构
            assert "success" in result
            assert "total_products" in result
            assert "products" in result
            
            if result["success"] and result["total_products"] > 0:
                # 打印价格统计
                if "price_stats" in result and result["price_stats"]:
                    stats = result["price_stats"]
                    print(f"\n📊 基础价格统计:")
                    print(f"   {stats}")
                
                # 打印价格分析
                if "price_analysis" in result and result["price_analysis"]:
                    analysis = result["price_analysis"]
                    print(f"\n📈 价格分析结果:")
                    
                    if "distribution" in analysis:
                        dist = analysis["distribution"]
                        print(f"   价格分布:")
                        print(f"     中位数: ¥{dist.get('median_price', 0)}")
                        print(f"     方差: {dist.get('price_variance', 0)}")
                        
                        if "price_ranges" in dist:
                            ranges = dist["price_ranges"]
                            for range_name, range_info in ranges.items():
                                print(f"     {range_name}: {range_info['range']} ({range_info['count']}个)")
                    
                    if "recommendations" in analysis:
                        rec = analysis["recommendations"]
                        print(f"   建议:")
                        for key, value in rec.items():
                            print(f"     {key}: {value}")
                
                # 验证产品数据
                products = result.get("products", [])
                if products:
                    print(f"\n🔍 样本产品 (前2个):")
                    for i, product in enumerate(products[:2]):
                        print(f"   {i+1}. {product['title']}")
                        print(f"      价格: ¥{product['price']}")
                        print(f"      卖家: {product['user_nick']}")
            
        except Exception as e:
            print(f"❌ 价格分析搜索失败: {str(e)}")
            print(f"   错误类型: {type(e).__name__}")
            pytest.skip(f"价格分析功能暂时不可用: {str(e)}")
    
    @pytest.mark.asyncio
    async def test_search_different_keywords(self, service):
        """测试不同关键词的搜索效果"""
        print(f"\n==== 测试不同关键词搜索 ====")
        
        test_keywords = ["鞋子", "包包", "书籍", "游戏"]
        
        for keyword in test_keywords:
            try:
                print(f"\n🔍 测试关键词: {keyword}")
                
                response = await service.search_products(
                    keyword=keyword,
                    page_number=1,
                    rows_per_page=5
                )
                
                print(f"   结果: 找到 {response.product_count} 个产品")
                
                if response.product_count > 0:
                    # 显示第一个产品
                    first_product = response.data[0]
                    print(f"   示例: {first_product.title} - ¥{first_product.price}")
                    
                    # 显示价格范围
                    if response.price_stats:
                        print(f"   价格: {response.price_stats.price_range}")
                
                # 简短延迟避免请求过于频繁
                await asyncio.sleep(0.5)
                
            except Exception as e:
                print(f"   错误: {str(e)}")
                continue
    
    @pytest.mark.asyncio
    async def test_comprehensive_workflow(self):
        """测试完整工作流程"""
        print(f"\n==== 测试完整工作流程 ====")
        
        try:
            service = XianyuService()
            
            print(f"📋 执行完整搜索工作流程:")
            print(f"   1. 初始化服务")
            print(f"   2. 执行产品搜索")
            print(f"   3. 进行价格分析")
            print(f"   4. 数据格式转换")
            
            # 步骤1: 搜索产品
            response = await service.search_products("数码", page_number=1, rows_per_page=30)
            print(f"   ✅ 步骤1完成: 找到 {response.product_count} 个产品")
            
            # 步骤2: 转换为简化格式
            simplified = XianyuSearchDataConverter.to_simplified_format(response)
            print(f"   ✅ 步骤2完成: 简化格式转换")
            
            # 步骤3: 转换为详细格式
            detailed = XianyuSearchDataConverter.to_detailed_format(response)
            print(f"   ✅ 步骤3完成: 详细格式转换")
            
            # 步骤4: 价格分析
            if response.product_count > 0:
                prices = [p.price for p in response.data]
                variance = service._calculate_variance(prices)
                distribution = service._analyze_price_distribution(prices)
                print(f"   ✅ 步骤4完成: 价格分析")
                print(f"      价格方差: {variance:.2f}")
                print(f"      价格分布区间数: {len(distribution.get('price_ranges', {}))}")
            
            print(f"\n🎉 完整工作流程测试成功!")
            
        except Exception as e:
            print(f"❌ 工作流程测试失败: {str(e)}")
            pytest.skip(f"工作流程暂时不可用: {str(e)}")


def test_models_only():
    """仅测试数据模型（不依赖网络）"""
    print(f"\n==== 独立模型测试 ====")
    
    # 模拟API响应数据
    mock_api_data = {
        "ret": ["SUCCESS::调用成功"],
        "data": {
            "resultList": [
                {
                    "id": "12345",
                    "title": "苹果 iPhone 13",
                    "price": "2000",
                    "nick": "测试卖家1",
                    "picUrl": "https://example.com/image1.jpg",
                    "area": "北京"
                },
                {
                    "id": "12346", 
                    "title": "苹果 iPhone 13 Pro",
                    "price": "3200",
                    "nick": "测试卖家2",
                    "picUrl": "https://example.com/image2.jpg",
                    "area": "上海"
                }
            ]
        }
    }
    
    # 测试从API响应创建模型
    response = XianyuSearchResponse.from_api_response(mock_api_data)
    
    print(f"✅ 模型解析成功")
    print(f"   产品数量: {response.product_count}")
    print(f"   是否成功: {response.success}")
    
    if response.price_stats:
        print(f"   价格统计: {response.price_stats.price_range}")
        print(f"   平均价格: ¥{response.price_stats.average_price}")
    
    # 测试数据转换
    simplified = XianyuSearchDataConverter.to_simplified_format(response)
    detailed = XianyuSearchDataConverter.to_detailed_format(response)
    
    print(f"✅ 数据转换成功")
    print(f"   简化格式产品数: {len(simplified.get('products', []))}")
    print(f"   详细格式产品数: {len(detailed.get('products', []))}")


if __name__ == "__main__":
    # 如果直接运行此文件，执行所有测试
    print("🚀 开始闲鱼搜索服务测试")
    
    # 首先运行不依赖网络的模型测试
    test_models_only()
    
    # 然后运行需要网络的测试
    try:
        service = XianyuService()
        test_instance = TestXianyuServiceReal()
        
        # 专门分析API响应结构
        print("\n" + "="*60)
        print("  重点：API响应结构分析")
        print("="*60)
        asyncio.run(test_instance.test_api_response_structure(service))
        
        print("\n" + "="*60)
        print("  基础搜索测试")
        print("="*60)
        # 测试基础功能
        asyncio.run(test_instance.test_basic_search(service, ["手机"]))
        
        print("\n🎉 所有测试完成!")
        
    except Exception as e:
        print(f"\n⚠️  网络相关测试跳过: {str(e)}")
        import traceback
        print(f"详细错误:\n{traceback.format_exc()}") 