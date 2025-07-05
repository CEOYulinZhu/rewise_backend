"""
图片+文字分析结果比较和合并工具

当用户同时提供图片和文字描述时，需要分别调用两个分析服务，
然后比较两者差异，如果有不同，以文字分析结果为准
"""

from typing import Dict, Any, Optional, List
from app.core.logger import app_logger


class AnalysisMerger:
    """分析结果比较和合并器"""
    
    # 重要字段权重 - 用于判断冲突时的优先级
    FIELD_WEIGHTS = {
        "category": 10,
        "sub_category": 8,
        "brand": 7,
        "model": 6,
        "condition": 9,
        "material": 5,
        "color": 4,
        "size": 3,
        "keywords": 2,
        "description": 1
    }
    
    # 需要合并而非覆盖的字段
    MERGE_FIELDS = ["keywords", "special_features"]
    
    @staticmethod
    def compare_and_merge(
        image_analysis: Dict[str, Any], 
        text_analysis: Dict[str, Any]
    ) -> Dict[str, Any]:
        """比较图片和文字分析结果，合并为最终结果
        
        Args:
            image_analysis: 图片分析结果
            text_analysis: 文字分析结果
            
        Returns:
            合并后的分析结果，包含来源信息和冲突报告
        """
        try:
            app_logger.info("开始比较和合并图片与文字分析结果")
            
            # 验证输入
            if not image_analysis or not isinstance(image_analysis, dict):
                app_logger.warning("图片分析结果无效，使用文字分析结果")
                return AnalysisMerger._add_merge_metadata(text_analysis, "text_only", [])
            
            if not text_analysis or not isinstance(text_analysis, dict):
                app_logger.warning("文字分析结果无效，使用图片分析结果")
                return AnalysisMerger._add_merge_metadata(image_analysis, "image_only", [])
            
            # 比较两个结果
            conflicts = AnalysisMerger._find_conflicts(image_analysis, text_analysis)
            
            # 合并结果 - 以文字分析为基础，补充图片分析的信息
            merged_result = AnalysisMerger._merge_results(
                base_result=text_analysis,
                supplement_result=image_analysis,
                conflicts=conflicts
            )
            
            # 添加元数据
            if conflicts:
                app_logger.info(f"发现 {len(conflicts)} 个字段冲突，以文字分析结果为准")
                source = "text_priority_with_conflicts"
            else:
                app_logger.info("图片和文字分析结果一致，成功合并")
                source = "merged_consistent"
            
            return AnalysisMerger._add_merge_metadata(merged_result, source, conflicts)
            
        except Exception as e:
            app_logger.error(f"分析结果合并失败: {e}")
            # 发生错误时，优先返回文字分析结果
            return AnalysisMerger._add_merge_metadata(
                text_analysis or image_analysis, 
                "error_fallback", 
                [{"error": str(e)}]
            )
    
    @staticmethod
    def _find_conflicts(image_result: Dict[str, Any], text_result: Dict[str, Any]) -> List[Dict[str, Any]]:
        """找出两个分析结果的冲突字段
        
        Args:
            image_result: 图片分析结果
            text_result: 文字分析结果
            
        Returns:
            冲突列表，每个冲突包含字段名、图片值、文字值
        """
        conflicts = []
        
        # 获取所有需要比较的字段
        all_fields = set(image_result.keys()) | set(text_result.keys())
        
        for field in all_fields:
            image_value = image_result.get(field)
            text_value = text_result.get(field)
            
            # 跳过None值和相同值
            if image_value is None or text_value is None:
                continue
            
            # 对于列表类型，检查是否有实质性差异
            if isinstance(image_value, list) and isinstance(text_value, list):
                if AnalysisMerger._lists_are_different(image_value, text_value):
                    conflicts.append({
                        "field": field,
                        "image_value": image_value,
                        "text_value": text_value,
                        "conflict_type": "list_difference"
                    })
            
            # 对于字符串类型，进行规范化比较
            elif isinstance(image_value, str) and isinstance(text_value, str):
                if AnalysisMerger._strings_are_different(image_value, text_value):
                    conflicts.append({
                        "field": field,
                        "image_value": image_value,
                        "text_value": text_value,
                        "conflict_type": "string_difference"
                    })
            
            # 其他类型直接比较
            elif image_value != text_value:
                conflicts.append({
                    "field": field,
                    "image_value": image_value,
                    "text_value": text_value,
                    "conflict_type": "value_difference"
                })
        
        return conflicts
    
    @staticmethod
    def _lists_are_different(list1: List, list2: List) -> bool:
        """判断两个列表是否有实质性差异"""
        # 转换为小写并去重
        set1 = {str(item).lower().strip() for item in list1 if item}
        set2 = {str(item).lower().strip() for item in list2 if item}
        
        # 如果交集占比较大的集合的50%以上，认为没有实质性差异
        if not set1 or not set2:
            return True
        
        intersection = set1 & set2
        max_set_size = max(len(set1), len(set2))
        
        return len(intersection) / max_set_size < 0.5
    
    @staticmethod
    def _strings_are_different(str1: str, str2: str) -> bool:
        """判断两个字符串是否有实质性差异"""
        # 规范化字符串进行比较
        norm_str1 = str1.lower().strip()
        norm_str2 = str2.lower().strip()
        
        # 直接相等
        if norm_str1 == norm_str2:
            return False
        
        # 检查是否一个是另一个的子集
        if norm_str1 in norm_str2 or norm_str2 in norm_str1:
            return False
        
        # 检查关键词重叠
        words1 = set(norm_str1.split())
        words2 = set(norm_str2.split())
        
        if not words1 or not words2:
            return True
        
        intersection = words1 & words2
        max_word_count = max(len(words1), len(words2))
        
        # 如果重叠词汇占比超过50%，认为没有实质性差异
        return len(intersection) / max_word_count < 0.5
    
    @staticmethod
    def _merge_results(
        base_result: Dict[str, Any], 
        supplement_result: Dict[str, Any], 
        conflicts: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """合并两个分析结果
        
        Args:
            base_result: 基础结果（优先级高）
            supplement_result: 补充结果
            conflicts: 冲突列表
            
        Returns:
            合并后的结果
        """
        merged = base_result.copy()
        conflict_fields = {conflict["field"] for conflict in conflicts}
        
        # 对于非冲突字段，从补充结果中添加缺失的信息
        for field, value in supplement_result.items():
            if field not in merged or merged[field] is None:
                merged[field] = value
            elif field in AnalysisMerger.MERGE_FIELDS and field not in conflict_fields:
                # 对于需要合并的字段（如keywords），进行智能合并
                merged[field] = AnalysisMerger._merge_field_values(
                    merged[field], value, field
                )
        
        return merged
    
    @staticmethod
    def _merge_field_values(base_value: Any, supplement_value: Any, field_name: str) -> Any:
        """合并单个字段的值"""
        if field_name == "keywords":
            # keywords字段进行去重合并
            if isinstance(base_value, list) and isinstance(supplement_value, list):
                combined = list(base_value)
                for item in supplement_value:
                    if item and item not in combined:
                        combined.append(item)
                return combined[:10]  # 最多保留10个关键词
        
        elif field_name == "special_features":
            # special_features字段进行文本拼接
            if isinstance(base_value, str) and isinstance(supplement_value, str):
                if supplement_value not in base_value:
                    return f"{base_value}；{supplement_value}"
        
        # 默认返回基础值
        return base_value
    
    @staticmethod
    def _add_merge_metadata(
        result: Dict[str, Any], 
        source: str, 
        conflicts: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """为结果添加合并元数据
        
        Args:
            result: 分析结果
            source: 数据来源类型
            conflicts: 冲突列表
            
        Returns:
            包含元数据的结果
        """
        result_with_metadata = result.copy()
        
        result_with_metadata["_merge_metadata"] = {
            "source": source,
            "has_conflicts": len(conflicts) > 0,
            "conflict_count": len(conflicts),
            "conflicts": conflicts[:5],  # 最多保留5个冲突记录
            "merge_strategy": "text_priority"
        }
        
        return result_with_metadata
    
    @staticmethod
    def get_merge_summary(merged_result: Dict[str, Any]) -> Dict[str, Any]:
        """获取合并摘要信息
        
        Args:
            merged_result: 包含元数据的合并结果
            
        Returns:
            合并摘要
        """
        metadata = merged_result.get("_merge_metadata", {})
        
        return {
            "source_type": metadata.get("source", "unknown"),
            "has_conflicts": metadata.get("has_conflicts", False),
            "conflict_count": metadata.get("conflict_count", 0),
            "merge_strategy": metadata.get("merge_strategy", "unknown"),
            "is_reliable": metadata.get("conflict_count", 0) <= 2  # 冲突少于等于2个认为可靠
        } 