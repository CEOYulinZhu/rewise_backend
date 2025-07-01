# 二手平台搜索Agent

## 概述

二手平台搜索Agent是一个专业的二手商品搜索智能体，使用蓝心大模型的Function Calling功能，基于物品分析结果智能提取搜索关键词，并在闲鱼、爱回收等平台搜索相关商品信息，提供市场价格参考和回收价值评估。

## 核心特性

### 🧠 智能关键词提取
- **Function Calling**：使用蓝心大模型的Function Calling技术
- **多维度理解**：深度理解物品品牌、型号、状态、类别等特征
- **平台优化**：针对不同平台特点生成优化关键词
- **搜索意图**：自动生成搜索意图和平台策略

### 🛒 多平台搜索
- **闲鱼平台**：个人闲置交易平台，关注成色、个人转让
- **爱回收平台**：专业回收估价平台，关注品牌、回收价值
- **并行搜索**：同时搜索多个平台，提高效率
- **统一结果**：标准化的搜索结果格式

### 💰 价格分析
- **市场行情**：获取同类商品的市场价格范围
- **回收价值**：了解专业回收平台的估价
- **价格统计**：提供最低、最高、平均价格等统计信息
- **趋势分析**：帮助用户了解商品保值情况

### 🔄 智能备用机制
- **双重保障**：Function Calling + 规则备用
- **分类映射**：预设多个物品类别的关键词映射
- **品牌识别**：智能识别品牌并优化搜索策略
- **状态映射**：根据物品状态调整搜索关键词

## 架构优化

### 📈 性能提升
- **并行搜索**：同时搜索多个平台，减少等待时间
- **专业提取**：专注于关键词提取和商品搜索
- **缓存友好**：分析结果可被多个模块复用
- **资源管理**：自动管理HTTP连接和API调用

### 🔧 维护性提升
- **单一职责**：专注核心搜索功能
- **模块解耦**：不依赖图片/文字分析服务
- **标准接口**：统一的分析结果输入格式
- **扩展性**：易于添加新的二手平台

## 输入输出规范

### 输入格式

```python
analysis_result = {
    "category": "电子产品",           # 必需：物品类别
    "sub_category": "手机",          # 可选：子类别
    "brand": "苹果",                 # 可选：品牌信息
    "model": "iPhone 13",           # 可选：型号信息
    "condition": "95新",            # 必需：物品状态
    "description": "苹果iPhone13...", # 必需：详细描述
    "color": "黑色",                # 可选：颜色
    "storage": "128GB",             # 可选：存储容量
    "keywords": ["iPhone", "手机"],  # 可选：已有关键词
    "special_features": "Face ID"   # 可选：特殊功能
}
```

### 输出格式

```python
{
    "success": True,
    "source": "analysis_result",
    "analysis_result": {...},       # 原始分析结果
    "result": {
        "success": True,
        "total_products": 25,
        "products": [
            {
                "platform": "闲鱼",
                "title": "苹果iPhone13 128G 黑色",
                "seller": "用户123",
                "price": 4500,
                "image_url": "https://...",
                "location": "上海",
                "platform_type": "C2C"
            },
            {
                "platform": "爱回收",
                "title": "iPhone 13 128GB",
                "seller": "爱回收官方",
                "price": 4200,
                "image_url": "https://...",
                "location": "全国",
                "platform_type": "B2C"
            }
        ],
        "platform_stats": {
            "xianyu": {
                "success": True,
                "product_count": 15,
                "price_stats": {
                    "min_price": 4000,
                    "max_price": 5200,
                    "average_price": 4600,
                    "price_range": "¥4000 - ¥5200"
                }
            },
            "aihuishou": {
                "success": True,
                "product_count": 10,
                "price_stats": {
                    "min_price": 3800,
                    "max_price": 4500,
                    "average_price": 4150,
                    "price_range": "¥3800 - ¥4500"
                }
            }
        },
        "keywords": {
            "keywords": ["iPhone 13", "苹果", "128GB"],
            "search_intent": "寻找同款手机的二手市场价格和回收价值",
            "platform_suggestions": {
                "xianyu": ["iPhone 13", "95新", "个人转让"],
                "aihuishou": ["iPhone 13", "苹果", "手机回收"]
            }
        }
    },
    "function_call_result": {
        "success": True,
        "source": "function_calling",
        "keywords": [...],
        "search_intent": "..."
    }
}
```

## 核心方法

### `search_from_analysis(analysis_result, **options)`

基于分析结果搜索相关二手商品的核心方法。

**参数：**
- `analysis_result`: 物品分析结果字典
- `max_results_per_platform`: 每个平台最大返回结果数（默认10个）
- `include_xianyu`: 是否包含闲鱼搜索（默认True）
- `include_aihuishou`: 是否包含爱回收搜索（默认True）

**返回：**
包含搜索结果、关键词、价格统计等信息的字典

## 使用示例

### 基本使用

```python
from app.agents.secondhand_search.agent import SecondhandSearchAgent

# 准备分析结果
analysis_result = {
    "category": "电子产品",
    "sub_category": "手机",
    "brand": "华为",
    "model": "P50 Pro",
    "condition": "9成新",
    "description": "华为P50 Pro 256GB 黑色，功能正常",
    "storage": "256GB",
    "color": "黑色"
}

# 搜索相关二手商品
async with SecondhandSearchAgent() as agent:
    result = await agent.search_from_analysis(
        analysis_result=analysis_result,
        max_results_per_platform=15
    )
    
    if result["success"]:
        search_result = result["result"]
        print(f"提取的关键词: {search_result['keywords']['keywords']}")
        print(f"搜索意图: {search_result['keywords']['search_intent']}")
        print(f"找到 {search_result['total_products']} 个商品")
        
        # 显示平台统计
        for platform, stats in search_result["platform_stats"].items():
            if stats["success"]:
                print(f"{platform}: {stats['product_count']}个商品, "
                      f"价格区间: {stats['price_stats']['price_range']}")
```

### 指定平台搜索

```python
async def search_specific_platforms(analysis_result):
    """仅搜索特定平台"""
    async with SecondhandSearchAgent() as agent:
        # 仅搜索闲鱼
        xianyu_result = await agent.search_from_analysis(
            analysis_result=analysis_result,
            include_xianyu=True,
            include_aihuishou=False
        )
        
        # 仅搜索爱回收
        aihuishou_result = await agent.search_from_analysis(
            analysis_result=analysis_result,
            include_xianyu=False,
            include_aihuishou=True
        )
        
        return xianyu_result, aihuishou_result
```

### 批量搜索

```python
async def batch_search(analysis_list):
    """批量搜索多个物品"""
    async with SecondhandSearchAgent() as agent:
        results = []
        for analysis in analysis_list:
            result = await agent.search_from_analysis(analysis)
            results.append(result)
        return results
```

## Function Calling机制

### 系统Prompt
```
你是一个专业的二手物品交易助手，专门帮助用户在二手平台（闲鱼、爱回收）上找到相关商品信息。

关键词提取原则：
- 品牌型号：如"iPhone 13"、"小米手机"、"华为笔记本"等
- 物品类型：如"手机"、"电脑"、"衣服"、"包包"等
- 物品状态：如"95新"、"9成新"、"全新"等（适用于闲鱼）
- 功能特征：如"32GB"、"256G"、"无线充电"等
- 材质颜色：如"黑色"、"白色"、"真皮"等

平台特性：
- 闲鱼：个人闲置交易，关注品牌、成色、型号
- 爱回收：专业回收估价，关注品牌、型号、回收价值
```

### Function定义
```json
{
    "name": "extract_secondhand_keywords",
    "description": "根据物品分析结果提取用于二手平台搜索的关键词",
    "parameters": {
        "type": "object",
        "properties": {
            "keywords": {
                "type": "array",
                "items": {"type": "string"},
                "description": "3-5个通用关键词"
            },
            "search_intent": {
                "type": "string",
                "description": "搜索意图说明"
            },
            "platform_suggestions": {
                "type": "object",
                "properties": {
                    "xianyu": {
                        "type": "array",
                        "description": "闲鱼平台特定关键词"
                    },
                    "aihuishou": {
                        "type": "array", 
                        "description": "爱回收平台特定关键词"
                    }
                }
            }
        },
        "required": ["keywords", "search_intent", "platform_suggestions"]
    }
}
```

## 备用机制

### 分类关键词映射
- **电子产品**: 
  - 基础: ["数码", "电子产品"]
  - 闲鱼: ["闲置数码", "个人闲置"]
  - 爱回收: ["数码回收", "电子设备回收"]

- **手机**:
  - 基础: ["手机", "智能手机"] 
  - 闲鱼: ["二手手机", "闲置手机", "个人转让"]
  - 爱回收: ["手机回收", "旧手机", "手机估价"]

### 品牌关键词映射
- **苹果**: ["Apple", "苹果", "iPhone", "iPad", "MacBook"]
- **华为**: ["华为", "Huawei", "Honor", "荣耀"]
- **小米**: ["小米", "Xiaomi", "Redmi", "红米"]

### 状态描述映射（闲鱼专用）
- **全新**: ["全新", "未拆封", "正品全新"]
- **95新**: ["95新", "极新", "轻微使用"]
- **9成新**: ["9成新", "成色很好"]

## 配置要求

### 环境变量
```bash
# 蓝心大模型配置
LANXIN_APP_ID=your_app_id
LANXIN_APP_KEY=your_app_key
LANXIN_API_BASE_URL=https://api.xxx.com/v1/chat/completions
LANXIN_TEXT_MODEL=your_text_model
```

## 依赖模块

- **提示词模块**: `app.prompts.secondhand_search_prompts`
- **闲鱼搜索服务**: `app.services.xianyu_service`
- **爱回收搜索服务**: `app.services.aihuishou_service`
- **数据模型**: `app.models.secondhand_search_models`
- **认证工具**: `app.utils.vivo_auth`
- **配置管理**: `app.core.config`
- **日志系统**: `app.core.logger`

## 性能特点

### 响应速度
- **关键词提取**: 通常在2-3秒内完成
- **平台搜索**: 2-4秒获取结果（并行执行）
- **总耗时**: 约4-7秒完成完整搜索

### 准确率
- **Function Calling成功率**: 85%+ (智能提取)
- **备用机制覆盖率**: 100% (保底服务)
- **搜索相关性**: 基于专业提示词优化

### 并发支持
- **异步设计**: 支持高并发请求
- **并行搜索**: 多平台同时搜索
- **资源管理**: 自动管理HTTP连接
- **错误恢复**: 智能的错误处理和重试机制

## 平台特色

### 闲鱼平台特点
- **个人交易**: C2C模式，价格更灵活
- **成色重要**: 商品状态对价格影响大
- **地域因素**: 同城交易更受欢迎
- **议价空间**: 通常可以议价

### 爱回收平台特点
- **专业回收**: B2C模式，价格相对标准
- **即时估价**: 提供标准化回收价格
- **全国服务**: 覆盖全国大部分地区
- **品类限制**: 主要回收电子产品、奢侈品

## 与其他模块协作

### 上游依赖
- **图片分析服务**: 提供物品识别结果
- **文字分析服务**: 提供文本解析结果
- **创意协调器**: 获取综合分析结果

### 下游输出
- **处置推荐Agent**: 参考市场价格制定处置策略
- **创意改造Agent**: 结合市场价值评估改造价值
- **前端展示**: 直接展示商品搜索结果和价格分析

## 错误处理

### 输入验证
- 检查分析结果格式和必需字段
- 验证参数范围和类型
- 处理空值和异常数据

### API容错
- Function Calling失败自动降级
- 平台搜索API异常处理
- 网络错误重试机制

### 结果处理
- 搜索结果格式验证
- 价格数据清洗和校验
- 统计信息计算容错

## 日志记录

### 操作日志
- 详细的搜索流程记录
- 关键词提取过程追踪
- 平台搜索结果统计

### 性能监控
- API调用耗时统计
- 搜索成功率监控
- 错误频率分析

### 业务指标
- 用户搜索行为分析
- 热门商品类别统计
- 价格趋势数据收集 