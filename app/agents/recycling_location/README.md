# 回收地点推荐Agent

## 概述

回收地点推荐Agent（RecyclingLocationAgent）是一个智能的回收服务模块，能够根据闲置物品的分析结果自动判断回收类型，并推荐附近的回收地点。该Agent结合了AI分析和地理位置服务，为用户提供精准的回收解决方案。

## 核心功能

### 1. 智能回收类型分析
- 基于蓝心大模型分析物品属性
- 支持四种固定回收类型：
  - **家电回收**：电视、冰箱、洗衣机、空调等家用电器
  - **电脑回收**：台式机、笔记本、显示器、键盘等电脑设备
  - **旧衣回收**：服装、鞋子、包包、纺织品等
  - **纸箱回收**：纸箱、书本、包装盒、纸制品等

### 2. 地点推荐服务
- 集成高德地图API搜索附近回收点
- 按距离自动排序，就近推荐
- 支持自定义搜索半径和数量限制
- 提供详细的地点信息（地址、电话、营业时间等）

## 技术架构

### 依赖组件
- **蓝心大模型**：提供智能分类分析
- **高德地图API**：提供地理位置搜索
- **Pydantic模型**：确保数据结构化和验证
- **异步架构**：支持高并发处理

### 核心类结构

```python
class RecyclingLocationAgent:
    """回收地点推荐Agent - 智能回收类型分析与地点推荐"""
    
    # 支持的回收类型
    RECYCLING_TYPES = {
        "家电回收": "家电回收",
        "电脑回收": "电脑回收", 
        "旧衣回收": "旧衣回收",
        "纸箱回收": "纸箱回收"
    }
```

## API接口

### 主要方法

#### `analyze_and_recommend_locations`
完整的分析和推荐服务

```python
async def analyze_and_recommend_locations(
    analysis_result: Dict[str, Any],    # 物品分析结果
    user_location: str,                 # 用户位置 "经度,纬度"
    radius: int = 50000,               # 搜索半径（米）
    max_locations: int = 20            # 最大地点数量
) -> RecyclingLocationResponse
```

### 便捷函数

```python
# 分析回收类型并推荐地点
response = await analyze_recycling_type_and_locations(
    analysis_result=item_analysis,
    user_location="116.397428,39.90923",
    radius=30000,
    max_locations=15
)
```

## 数据模型

### 输入数据格式

```python
analysis_result = {
    "category": "电子产品",
    "description": "一台使用了3年的联想笔记本电脑",
    "condition": "八成新",
    "brand": "联想",
    "model": "ThinkPad X1",
    # ... 其他分析字段
}
```

### 输出数据格式

#### RecyclingLocationResponse

```python
{
    "success": True,
    "recycling_type": "电脑回收",
    "locations_count": 15,
    "locations": [
        {
            "id": "BV10001",
            "name": "绿色回收站",
            "address": "北京市朝阳区xxx路xxx号",
            "distance_formatted": "1.2公里",
            "tel": "010-12345678",
            "opentime_today": "08:00-18:00"
        }
        // ... 更多地点
    ],
    "search_params": {
        "location": "116.397428,39.90923",
        "keyword": "电脑回收",
        "radius": 30000,
        "max_locations": 15
    }
}
```

## 使用示例

### 基础使用

```python
from app.agents.recycling_location import analyze_recycling_type_and_locations

async def recommend_recycling_locations():
    # 物品分析结果
    item_analysis = {
        "category": "家用电器",
        "description": "小米电视55寸，使用2年",
        "condition": "八成新",
        "brand": "小米"
    }
    
    # 用户位置（北京天安门）
    user_location = "116.397428,39.90923"
    
    # 获取推荐
    response = await analyze_recycling_type_and_locations(
        analysis_result=item_analysis,
        user_location=user_location,
        radius=20000,  # 20公里范围内
        max_locations=10
    )
    
    if response.success:
        print(f"回收类型: {response.recycling_type}")
        print(f"找到 {len(response.locations)} 个回收点")
        
        # 获取最近的5个地点
        top_locations = response.get_top_locations(limit=5)
        for location in top_locations:
            print(f"- {location.name}: {location.distance_formatted}")
    else:
        print(f"推荐失败: {response.error}")
```

### 高级用法

```python
from app.agents.recycling_location import RecyclingLocationAgent

async def advanced_usage():
    async with RecyclingLocationAgent() as agent:
        # 完整推荐流程
        full_result = await agent.analyze_and_recommend_locations(
            analysis_result=item_analysis,
            user_location="116.397428,39.90923",
            radius=30000,
            max_locations=15
        )
        
        if full_result.success:
            print(f"回收类型: {full_result.recycling_type}")
            print(f"找到 {len(full_result.locations)} 个回收点")
            
            # 筛选距离范围内的地点
            nearby = full_result.get_nearby_locations(max_distance_meters=5000)
            print(f"5公里内有 {len(nearby)} 个回收点")
        else:
            print(f"推荐失败: {full_result.error}")
```

## 回收类型分类规则

### 分类逻辑

1. **AI智能分析**：优先使用蓝心大模型进行智能分类
2. **关键词匹配**：基于预定义关键词进行备用分类
3. **默认归类**：无法确定时默认归为"家电回收"

### 分类标准

| 回收类型 | 主要物品 | 判断关键词 |
|---------|---------|-----------|
| 家电回收 | 电视、冰箱、洗衣机、空调、微波炉等 | 电器、家电、制冷、加热 |
| 电脑回收 | 电脑、显示器、键盘、打印机、手机等 | 数码、智能、屏幕、处理器 |
| 旧衣回收 | 服装、鞋子、包包、床单、窗帘等 | 布料、纤维、穿戴、时尚 |
| 纸箱回收 | 纸箱、书本、包装盒、报纸等 | 纸质、印刷、包装、文档 |

## 错误处理

### 常见错误类型

1. **输入验证错误**
   - 分析结果为空或格式错误
   - 用户位置格式不正确

2. **AI分析错误**
   - 模型调用失败
   - 响应解析失败

3. **地点搜索错误**
   - 高德地图API调用失败
   - 网络连接问题

### 容错机制

- **备用分类**：AI失败时使用规则分类
- **重试机制**：网络请求自动重试
- **优雅降级**：部分失败时返回可用数据

## 性能优化

### 异步处理
- 所有API调用都是异步的
- 支持并发处理多个请求

### 缓存策略
- 相同物品类型的分析结果可复用
- 地点搜索结果可短时间缓存

### 资源管理
- 自动管理HTTP连接池
- 支持上下文管理器自动清理

## 配置项

### 环境变量

```bash
# 蓝心大模型配置
LANXIN_APP_ID=your_app_id
LANXIN_APP_KEY=your_app_key
LANXIN_API_BASE_URL=https://api.lanxin.com/v1/chat
LANXIN_TEXT_MODEL=your_model_name

# 高德地图配置
AMAP_API_KEY=your_amap_key
AMAP_API_BASE_URL=https://restapi.amap.com/v3/place/around
```

### 默认参数

```python
DEFAULT_SEARCH_RADIUS = 50000      # 默认搜索半径50公里
DEFAULT_MAX_LOCATIONS = 20         # 默认最多返回20个地点
DEFAULT_AI_TEMPERATURE = 0.1       # AI模型温度（确保分类稳定）
DEFAULT_TIMEOUT = 30               # API超时时间30秒
```

## 扩展开发

### 添加新的回收类型

1. 更新 `RECYCLING_TYPES` 字典
2. 在提示词中添加新类型的描述
3. 更新关键词映射规则
4. 添加相应的测试用例

### 自定义分类逻辑

```python
class CustomRecyclingLocationAgent(RecyclingLocationAgent):
    def _get_fallback_recycling_type(self, analysis_result):
        # 实现自定义分类逻辑
        return super()._get_fallback_recycling_type(analysis_result)
```

## 最佳实践

1. **输入验证**：始终验证分析结果的完整性
2. **错误处理**：妥善处理所有可能的异常情况
3. **资源管理**：使用上下文管理器确保资源清理
4. **监控日志**：记录关键操作和性能指标
5. **用户体验**：提供清晰的错误信息和使用指导

## 注意事项

- 回收类型分析结果可能受物品描述质量影响
- 地点推荐依赖高德地图数据的完整性和准确性
- API调用需要稳定的网络连接
- 建议为生产环境配置适当的重试和超时策略 