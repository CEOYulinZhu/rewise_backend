"""
改造方案概览提取服务

从创意改造方案中提取关键信息，生成概览统计数据
"""

from typing import Dict, Any, List

from app.core.logger import app_logger


class RenovationSummaryService:
    """改造方案概览提取服务"""
    
    @staticmethod
    def extract_overview(renovation_plan: Dict[str, Any]) -> Dict[str, Any]:
        """
        从改造方案中提取概览信息
        
        Args:
            renovation_plan: 完整的改造方案字典
            
        Returns:
            包含概览信息的字典
        """
        try:
            app_logger.info("开始提取改造方案概览信息")
            
            # 基础信息提取
            project_title = renovation_plan.get("project_title", "未知项目")
            difficulty_level = renovation_plan.get("difficulty_level", "未知")
            
            # 成本信息提取
            cost_info = RenovationSummaryService._extract_cost_info(renovation_plan)
            
            # 时间信息提取
            time_info = RenovationSummaryService._extract_time_info(renovation_plan)
            
            # 步骤信息提取
            steps_info = RenovationSummaryService._extract_steps_info(renovation_plan)
            
            # 资源信息提取
            resources_info = RenovationSummaryService._extract_resources_info(renovation_plan)
            
            # 难度分析
            difficulty_analysis = RenovationSummaryService._analyze_difficulty(renovation_plan)
            
            overview = {
                "project_title": project_title,
                "overall_difficulty": difficulty_level,
                "cost_summary": cost_info,
                "time_summary": time_info,
                "steps_summary": steps_info,
                "resources_summary": resources_info,
                "difficulty_analysis": difficulty_analysis,
                "has_safety_warnings": len(renovation_plan.get("safety_warnings", [])) > 0,
                "safety_warnings_count": len(renovation_plan.get("safety_warnings", [])),
                "has_alternative_ideas": len(renovation_plan.get("alternative_ideas", [])) > 0,
                "alternative_ideas_count": len(renovation_plan.get("alternative_ideas", []))
            }
            
            app_logger.info("改造方案概览信息提取完成")
            return overview
            
        except Exception as e:
            app_logger.error(f"提取改造方案概览信息失败: {e}")
            return {
                "project_title": "概览提取失败",
                "error": str(e),
                "overall_difficulty": "未知",
                "cost_summary": {"min_cost": 0, "max_cost": 0, "total_estimated_cost": 0},
                "time_summary": {"total_minutes": 0, "total_hours": 0, "time_range": "未知"},
                "steps_summary": {"total_steps": 0, "difficulty_distribution": {}},
                "resources_summary": {"total_tools": 0, "total_materials": 0},
                "difficulty_analysis": {"complexity_score": 0, "beginner_friendly": False}
            }
    
    @staticmethod
    def _extract_cost_info(renovation_plan: Dict[str, Any]) -> Dict[str, Any]:
        """提取成本信息"""
        cost_range = renovation_plan.get("estimated_cost_range", {})
        
        if isinstance(cost_range, dict):
            min_cost = cost_range.get("min_cost", 0)
            max_cost = cost_range.get("max_cost", 0)
            cost_description = cost_range.get("cost_description", "")
        else:
            # 兼容旧格式
            min_cost = 0
            max_cost = 0
            cost_description = str(cost_range) if cost_range else ""
        
        # 计算平均成本
        avg_cost = (min_cost + max_cost) / 2 if min_cost and max_cost else 0
        
        return {
            "min_cost": min_cost,
            "max_cost": max_cost,
            "average_cost": round(avg_cost, 2),
            "cost_description": cost_description,
            "cost_level": RenovationSummaryService._classify_cost_level(avg_cost)
        }
    
    @staticmethod
    def _extract_time_info(renovation_plan: Dict[str, Any]) -> Dict[str, Any]:
        """提取时间信息"""
        steps = renovation_plan.get("steps", [])
        total_minutes = 0
        step_times = []
        
        for step in steps:
            # 优先使用新格式 estimated_time_minutes
            if "estimated_time_minutes" in step:
                minutes = step["estimated_time_minutes"]
                if isinstance(minutes, (int, float)):
                    total_minutes += minutes
                    step_times.append(minutes)
            else:
                # 兼容旧格式 estimated_time
                time_str = step.get("estimated_time", "")
                minutes = RenovationSummaryService._parse_time_string(time_str)
                total_minutes += minutes
                step_times.append(minutes)
        
        total_hours = total_minutes / 60
        
        return {
            "total_minutes": int(total_minutes),
            "total_hours": round(total_hours, 1),
            "time_range": RenovationSummaryService._format_time_range(total_minutes),
            "step_times": step_times,
            "average_step_time": round(sum(step_times) / len(step_times), 1) if step_times else 0,
            "longest_step_time": max(step_times) if step_times else 0,
            "time_level": RenovationSummaryService._classify_time_level(total_hours)
        }
    
    @staticmethod
    def _extract_steps_info(renovation_plan: Dict[str, Any]) -> Dict[str, Any]:
        """提取步骤信息"""
        steps = renovation_plan.get("steps", [])
        total_steps = len(steps)
        
        # 难度分布统计
        difficulty_count = {"简单": 0, "中等": 0, "困难": 0, "未知": 0}
        
        for step in steps:
            difficulty = step.get("difficulty", "未知")
            if difficulty in difficulty_count:
                difficulty_count[difficulty] += 1
            else:
                difficulty_count["未知"] += 1
        
        # 计算步骤复杂度
        complexity_score = (
            difficulty_count["简单"] * 1 +
            difficulty_count["中等"] * 2 +
            difficulty_count["困难"] * 3
        ) / max(total_steps, 1)
        
        return {
            "total_steps": total_steps,
            "difficulty_distribution": difficulty_count,
            "complexity_score": round(complexity_score, 2),
            "has_difficult_steps": difficulty_count["困难"] > 0,
            "simple_steps_ratio": round(difficulty_count["简单"] / max(total_steps, 1), 2)
        }
    
    @staticmethod
    def _extract_resources_info(renovation_plan: Dict[str, Any]) -> Dict[str, Any]:
        """提取资源信息"""
        steps = renovation_plan.get("steps", [])
        all_tools = set()
        all_materials = set()
        
        for step in steps:
            tools = step.get("tools_needed", [])
            materials = step.get("materials_needed", [])
            
            if isinstance(tools, list):
                all_tools.update(tools)
            if isinstance(materials, list):
                all_materials.update(materials)
        
        # 工具分类
        tool_categories = RenovationSummaryService._categorize_tools(list(all_tools))
        
        return {
            "total_tools": len(all_tools),
            "total_materials": len(all_materials),
            "tools_list": sorted(list(all_tools)),
            "materials_list": sorted(list(all_materials)),
            "tool_categories": tool_categories,
            "resource_complexity": RenovationSummaryService._assess_resource_complexity(all_tools, all_materials)
        }
    
    @staticmethod
    def _analyze_difficulty(renovation_plan: Dict[str, Any]) -> Dict[str, Any]:
        """分析难度"""
        overall_difficulty = renovation_plan.get("difficulty_level", "未知")
        steps = renovation_plan.get("steps", [])
        required_skills = renovation_plan.get("required_skills", [])
        
        # 计算复杂度评分
        difficulty_scores = {"简单": 1, "中等": 2, "困难": 3, "未知": 2}
        base_score = difficulty_scores.get(overall_difficulty, 2)
        
        # 根据步骤数调整
        steps_factor = min(len(steps) / 5, 1.5)  # 5步以上增加难度
        
        # 根据技能要求调整
        skills_factor = min(len(required_skills) / 3, 1.3)  # 3个以上技能增加难度
        
        complexity_score = base_score * steps_factor * skills_factor
        
        # 判断是否适合新手
        beginner_friendly = (
            overall_difficulty in ["简单", "中等"] and
            len(steps) <= 5 and
            len(required_skills) <= 2 and
            complexity_score <= 3
        )
        
        return {
            "complexity_score": round(complexity_score, 2),
            "beginner_friendly": beginner_friendly,
            "skill_requirements": required_skills,
            "skill_count": len(required_skills),
            "difficulty_factors": {
                "base_difficulty": overall_difficulty,
                "steps_complexity": steps_factor,
                "skills_complexity": skills_factor
            }
        }
    
    @staticmethod
    def _parse_time_string(time_str: str) -> int:
        """解析时间字符串，返回分钟数"""
        if not time_str:
            return 0
        
        time_str = time_str.lower()
        minutes = 0
        
        # 提取小时数
        if "小时" in time_str:
            try:
                # 匹配 "1-2小时" 或 "2小时" 等格式
                import re
                hour_match = re.search(r'(\d+(?:\.\d+)?)-?(\d+(?:\.\d+)?)?小时', time_str)
                if hour_match:
                    hour1 = float(hour_match.group(1))
                    hour2 = float(hour_match.group(2)) if hour_match.group(2) else hour1
                    avg_hours = (hour1 + hour2) / 2
                    minutes += avg_hours * 60
            except:
                pass
        
        # 提取分钟数
        if "分钟" in time_str:
            try:
                import re
                min_match = re.search(r'(\d+)-?(\d+)?分钟', time_str)
                if min_match:
                    min1 = int(min_match.group(1))
                    min2 = int(min_match.group(2)) if min_match.group(2) else min1
                    minutes += (min1 + min2) / 2
            except:
                pass
        
        return int(minutes)
    
    @staticmethod
    def _format_time_range(total_minutes: int) -> str:
        """格式化时间范围"""
        if total_minutes < 60:
            return f"{total_minutes}分钟"
        else:
            hours = total_minutes / 60
            if hours < 2:
                return f"{hours:.1f}小时"
            else:
                return f"{hours:.1f}小时"
    
    @staticmethod
    def _classify_cost_level(avg_cost: float) -> str:
        """分类成本等级"""
        if avg_cost <= 50:
            return "低成本"
        elif avg_cost <= 150:
            return "中等成本"
        elif avg_cost <= 300:
            return "高成本"
        else:
            return "昂贵"
    
    @staticmethod
    def _classify_time_level(total_hours: float) -> str:
        """分类时间等级"""
        if total_hours <= 1:
            return "快速"
        elif total_hours <= 3:
            return "中等耗时"
        elif total_hours <= 6:
            return "较长耗时"
        else:
            return "长时间项目"
    
    @staticmethod
    def _categorize_tools(tools: List[str]) -> Dict[str, List[str]]:
        """工具分类"""
        categories = {
            "基础工具": [],
            "电动工具": [],
            "测量工具": [],
            "清洁工具": [],
            "其他工具": []
        }
        
        basic_tools = ["螺丝刀", "扳手", "钳子", "锤子", "刷子", "剪刀"]
        power_tools = ["电钻", "电动砂光机", "喷枪", "电锯"]
        measure_tools = ["尺子", "量角器", "水平仪"]
        clean_tools = ["抹布", "清洁剂", "吸尘器"]
        
        for tool in tools:
            categorized = False
            for basic in basic_tools:
                if basic in tool:
                    categories["基础工具"].append(tool)
                    categorized = True
                    break
            
            if not categorized:
                for power in power_tools:
                    if power in tool:
                        categories["电动工具"].append(tool)
                        categorized = True
                        break
            
            if not categorized:
                for measure in measure_tools:
                    if measure in tool:
                        categories["测量工具"].append(tool)
                        categorized = True
                        break
            
            if not categorized:
                for clean in clean_tools:
                    if clean in tool:
                        categories["清洁工具"].append(tool)
                        categorized = True
                        break
            
            if not categorized:
                categories["其他工具"].append(tool)
        
        # 移除空分类
        return {k: v for k, v in categories.items() if v}
    
    @staticmethod
    def _assess_resource_complexity(tools: set, materials: set) -> str:
        """评估资源复杂度"""
        total_resources = len(tools) + len(materials)
        
        if total_resources <= 5:
            return "简单"
        elif total_resources <= 10:
            return "中等"
        elif total_resources <= 15:
            return "复杂"
        else:
            return "非常复杂"
    
    @staticmethod
    def generate_summary_text(overview: Dict[str, Any]) -> str:
        """生成概览文本描述"""
        try:
            project_title = overview.get("project_title", "改造项目")
            difficulty = overview.get("overall_difficulty", "未知")
            
            cost_info = overview.get("cost_summary", {})
            time_info = overview.get("time_summary", {})
            steps_info = overview.get("steps_summary", {})
            
            summary_parts = [
                f"📋 {project_title}",
                f"🎯 难度等级：{difficulty}",
                f"⏱️ 预计耗时：{time_info.get('time_range', '未知')}（共{steps_info.get('total_steps', 0)}步）",
            ]
            
            if cost_info.get("min_cost", 0) > 0:
                summary_parts.append(
                    f"💰 预算范围：{cost_info['min_cost']}-{cost_info['max_cost']}元"
                )
            
            resources_info = overview.get("resources_summary", {})
            if resources_info.get("total_tools", 0) > 0:
                summary_parts.append(
                    f"🔧 所需资源：{resources_info['total_tools']}种工具，{resources_info['total_materials']}种材料"
                )
            
            difficulty_analysis = overview.get("difficulty_analysis", {})
            if difficulty_analysis.get("beginner_friendly", False):
                summary_parts.append("✅ 适合新手")
            
            return "\n".join(summary_parts)
            
        except Exception as e:
            return f"概览生成失败: {str(e)}" 