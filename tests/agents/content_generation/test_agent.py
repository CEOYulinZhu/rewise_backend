"""
文案生成Agent测试

测试文案生成Agent的核心功能
"""

import asyncio

import pytest

from app.agents.content_generation.agent import ContentGenerationAgent
from app.prompts.content_generation_prompts import ContentGenerationPrompts
from app.models.content_generation_models import (
    ContentGenerationResponse,
    ContentGenerationResult,
    ContentGenerationDataConverter
)


class TestContentGenerationAgent:
    """文案生成Agent测试类"""
    
    @pytest.fixture
    def agent(self):
        """创建Agent实例"""
        return ContentGenerationAgent()
    
    def test_data_models(self):
        """测试数据模型"""
        print(f"\n==== 测试数据模型 ====")
        
        # 测试文案生成结果
        content_result = ContentGenerationResult(
            title="苹果 iPhone 13 八成新 诚信出售",
            description="出售iPhone 13一台，使用一年多，外观良好，功能正常，电池健康度85%，支持Face ID，诚信交易，支持当面验货。"
        )
        assert content_result.title.startswith("苹果")
        assert "iPhone 13" in content_result.description
        
        # 测试数据验证 - 标题长度 (创建一个确实超过100字符的标题)
        try:
            # 这个标题有102个字符，应该触发验证错误
            super_long_title = "这是一个非常非常非常非常非常非常非常非常非常非常非常非常非常非常非常非常非常非常非常非常非常非常非常非常非常非常非常非常非常非常非常非常非常非常非常非常非常非常非常非常非常非常非常非常非常非常非常非常非常长的标题"
            invalid_result = ContentGenerationResult(
                title=super_long_title,
                description="正常描述"
            )
            assert False, "应该抛出验证错误"
        except ValueError as e:
            print(f"✅ 标题长度验证正常: {e}")
        
        # 测试数据验证 - 空标题
        try:
            invalid_result = ContentGenerationResult(
                title="",
                description="正常描述"
            )
            assert False, "应该抛出验证错误"
        except ValueError as e:
            print(f"✅ 空标题验证正常: {e}")
        
        # 测试数据转换器
        result = ContentGenerationDataConverter.create_content_result(
            title="测试标题",
            description="测试描述"
        )
        assert result.title == "测试标题"
        assert result.description == "测试描述"
        
        # 测试字典转换
        dict_result = content_result.to_dict()
        assert "title" in dict_result
        assert "description" in dict_result
        assert dict_result["title"] == content_result.title
        
        print("数据模型测试通过！")
    
    @pytest.fixture
    def sample_analysis_result(self):
        """样例分析结果"""
        return {
            "category": "电子产品",
            "sub_category": "智能手机",
            "condition": "八成新",
            "description": "iPhone 13，使用一年多，外观良好，功能正常，电池稍有老化",
            "brand": "苹果",
            "material": "金属玻璃",
            "keywords": ["手机", "iPhone", "苹果"],
            "special_features": "Face ID，5G网络"
        }
    
    def test_prompts_initialization(self):
        """测试提示词初始化"""
        print(f"\n==== 测试提示词初始化 ====")
        
        system_prompt = ContentGenerationPrompts.get_system_prompt()
        print(f"系统提示词长度: {len(system_prompt)}")
        print(f"系统提示词前200字符: {system_prompt[:200]}...")
        
        assert isinstance(system_prompt, str)
        assert len(system_prompt) > 0
        assert "文案生成" in system_prompt or "交易平台" in system_prompt
        
        # 测试用户提示词模板
        sample_analysis = {
            "category": "测试类别",
            "condition": "测试状态",
            "description": "测试描述"
        }
        user_prompt = ContentGenerationPrompts.get_user_prompt(sample_analysis)
        print(f"用户提示词模板长度: {len(user_prompt)}")
        print(f"用户提示词包含分析结果: {'category: 测试类别' in user_prompt}")
        
        assert isinstance(user_prompt, str)
        assert "测试类别" in user_prompt
        assert "测试状态" in user_prompt
        
        print("提示词模块初始化测试通过！")
    
    def test_fallback_content_generation(self):
        """测试备用文案生成逻辑"""
        print(f"\n==== 测试备用文案生成逻辑 ====")
        
        # 测试电子产品
        print(f"测试类别: 电子产品, 品牌: 苹果, 状态: 八成新")
        
        result = ContentGenerationPrompts.get_fallback_content({
            "category": "电子产品",
            "sub_category": "智能手机",
            "brand": "苹果",
            "condition": "八成新",
            "description": "iPhone 13，外观良好"
        })
        
        print(f"备用文案生成结果:")
        print(f"标题: {result['title']}")
        print(f"描述: {result['description']}")
        
        assert isinstance(result, dict)
        assert "title" in result
        assert "description" in result
        assert "苹果" in result["title"]
        assert "八成新" in result["title"]
        assert "出售" in result["title"]
        
        # 测试服装类别
        print(f"\n测试类别: 服装")
        clothing_result = ContentGenerationPrompts.get_fallback_content({
            "category": "服装",
            "brand": "耐克",
            "condition": "九成新"
        })
        print(f"服装标题: {clothing_result['title']}")
        print(f"服装描述: {clothing_result['description']}")
        
        assert "耐克" in clothing_result["title"]
        assert "无破损" in clothing_result["description"] or "诚信出售" in clothing_result["description"]
        
        print("备用文案生成逻辑测试通过！")
    
    def test_ai_response_parsing(self):
        """测试AI响应解析"""
        print(f"\n==== 测试AI响应解析 ====")
        
        # 测试正确JSON格式
        json_response = """{"title": "苹果 iPhone 13 八成新 出售", "description": "出售iPhone 13一台，功能正常，诚信交易"}"""
        
        result = ContentGenerationDataConverter.parse_ai_response(json_response)
        assert result is not None
        assert result.title == "苹果 iPhone 13 八成新 出售"
        assert "iPhone 13" in result.description
        print(f"✅ JSON格式解析成功")
        
        # 测试代码块格式
        code_block_response = """```json
{"title": "联想 笔记本电脑 九成新", "description": "联想笔记本电脑，配置不错，使用时间短"}
```"""
        
        result = ContentGenerationDataConverter.parse_ai_response(code_block_response)
        assert result is not None
        assert "联想" in result.title
        print(f"✅ 代码块格式解析成功")
        
        # 测试混合文本格式
        mixed_response = """根据您的要求，我为您生成以下文案：
        
{"title": "华为 平板电脑 七成新 急售", "description": "华为平板，屏幕清晰，电池续航良好，因换新机急售"}

希望这个文案对您有帮助。"""
        
        result = ContentGenerationDataConverter.parse_ai_response(mixed_response)
        assert result is not None
        assert "华为" in result.title
        print(f"✅ 混合文本格式解析成功")
        
        # 测试无效格式
        invalid_response = "这不是一个有效的JSON响应"
        result = ContentGenerationDataConverter.parse_ai_response(invalid_response)
        assert result is None
        print(f"✅ 无效格式正确处理")
        
        print("AI响应解析测试通过！")
    
    @pytest.mark.asyncio
    async def test_generate_content(self, agent, sample_analysis_result):
        """测试文案生成功能"""
        print(f"\n==== 测试文案生成功能 ====")
        print(f"输入分析结果: {sample_analysis_result}")
        
        try:
            response = await agent.generate_content(sample_analysis_result)
            
            print(f"生成成功: {response.success}")
            print(f"数据来源: {response.source}")
            print(f"生成来源: {response.generation_source}")
            
            assert isinstance(response, ContentGenerationResponse)
            assert response.source == "content_generation_agent"
            
            if response.success:
                print(f"\n--- 物品分析结果 ---")
                analysis = response.analysis_result
                print(f"类别: {analysis.get('category')}")
                print(f"子类别: {analysis.get('sub_category')}")
                print(f"品牌: {analysis.get('brand')}")
                print(f"状态: {analysis.get('condition')}")
                
                assert response.content_result is not None
                assert response.analysis_result is not None
                
                content = response.content_result
                assert isinstance(content, ContentGenerationResult)
                
                print(f"\n--- 生成的交易文案 ---")
                print(f"标题: {content.title}")
                print(f"描述: {content.description}")
                
                # 验证文案质量
                assert len(content.title) > 0
                assert len(content.description) > 0
                assert len(content.title) <= 100
                assert len(content.description) <= 1000
                
                # 检查是否包含关键信息
                title_lower = content.title.lower()
                desc_lower = content.description.lower()
                
                # 应该包含品牌或类别信息
                has_brand_or_category = (
                    "苹果" in content.title or "iphone" in title_lower or 
                    "电子产品" in content.title or "手机" in content.title
                )
                assert has_brand_or_category, "标题应包含品牌或类别信息"
                
                # 描述应该更详细
                assert len(content.description) > len(content.title)
                
                print(f"\n📊 文案质量分析:")
                print(f"标题长度: {len(content.title)} 字符")
                print(f"描述长度: {len(content.description)} 字符")
                print(f"生成来源: {response.generation_source}")
                
                if response.ai_raw_response:
                    print(f"AI原始响应长度: {len(response.ai_raw_response)} 字符")
                
            else:
                print(f"生成失败: {response.error}")
                
        finally:
            await agent.close()
    
    def test_validation_logic(self, sample_analysis_result):
        """测试输入验证逻辑"""
        print(f"\n==== 测试输入验证逻辑 ====")
        
        agent = ContentGenerationAgent()
        
        # 测试空输入
        print("测试空输入...")
        import asyncio
        
        async def test_empty_input():
            response = await agent.generate_content(None)
            assert not response.success
            assert "分析结果为空" in response.error
            
            response = await agent.generate_content({})
            # 空字典应该被接受但使用备用逻辑
            print(f"空字典输入结果: {response.success}")
            print(f"生成来源: {response.generation_source}")
        
        asyncio.run(test_empty_input())
        
        # 测试正常输入
        print("测试正常输入格式...")
        assert isinstance(sample_analysis_result, dict)
        assert "category" in sample_analysis_result
        assert "condition" in sample_analysis_result
        print("输入验证逻辑测试通过！")


async def simple_test():
    """简单快速测试"""
    print("\n" + "="*50)
    print("文案生成Agent - 简单测试")
    print("="*50)
    
    # 创建样例分析结果
    analysis_result = {
        "category": "电子产品",
        "sub_category": "智能手机",
        "condition": "八成新",
        "description": "iPhone 13，外观良好，功能正常，电池健康度85%",
        "brand": "苹果",
        "material": "金属玻璃",
        "keywords": ["手机", "iPhone", "苹果"],
        "special_features": "Face ID，5G网络"
    }
    
    async with ContentGenerationAgent() as agent:
        response = await agent.generate_content(analysis_result)
        
        if response.success:
            content = response.content_result
            print(f"✅ 文案生成成功!")
            print(f"\n📱 生成的交易文案:")
            print(f"标题: {content.title}")
            print(f"描述: {content.description}")
            
            print(f"\n📊 质量分析:")
            print(f"标题长度: {len(content.title)} 字符")
            print(f"描述长度: {len(content.description)} 字符")
            print(f"生成来源: {response.generation_source}")
            
            if response.generation_source == "ai" and response.ai_raw_response:
                print(f"AI响应长度: {len(response.ai_raw_response)} 字符")
            
        else:
            print(f"❌ 文案生成失败: {response.error}")


if __name__ == "__main__":
    # 运行简单测试
    asyncio.run(simple_test()) 