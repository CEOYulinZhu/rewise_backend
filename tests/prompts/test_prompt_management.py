"""
提示词管理功能测试
"""

from app.prompts import LLMPrompts


class TestLLMPrompts:
    """LLM提示词测试"""
    
    def test_get_text_analysis_system_prompt(self):
        """测试获取文本分析系统提示词"""
        prompt = LLMPrompts.get_text_analysis_system_prompt()
        assert isinstance(prompt, str)
        assert "物品分析专家" in prompt
    
    def test_get_text_analysis_prompt(self):
        """测试获取文本分析用户提示词"""
        test_description = "这是一台二手笔记本电脑"
        prompt = LLMPrompts.get_text_analysis_prompt(test_description)
        
        assert isinstance(prompt, str)
        assert test_description in prompt
        assert "category" in prompt
        assert "sub_category" in prompt
    
    def test_get_image_analysis_prompt(self):
        """测试获取图像分析提示词"""
        prompt = LLMPrompts.get_image_analysis_prompt()
        assert isinstance(prompt, str)
        assert "图片" in prompt
        assert "JSON格式" in prompt
    

    
    def test_get_all_prompts(self):
        """测试获取所有提示词"""
        prompts = LLMPrompts.get_all_prompts()
        assert isinstance(prompts, dict)
        assert "text_analysis_system" in prompts
        assert "image_analysis" in prompts


 