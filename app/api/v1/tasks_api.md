# 任务处理 WebSocket API 文档

## 概述

本文档描述了物品处置任务的 WebSocket 实时处理接口。该接口支持实时接收处理进度和结果，适用于需要实时反馈的前端应用。

## 接口信息

- **接口路径**: `/api/v1/tasks/ws/process`
- **协议**: WebSocket
- **认证**: 无需认证（根据实际需求可添加）

## 连接建立

### JavaScript 示例

```javascript
// 建立 WebSocket 连接
const ws = new WebSocket('ws://localhost:8000/api/v1/tasks/ws/process');

// 连接成功
ws.onopen = function(event) {
    console.log('WebSocket 连接已建立');
    
    // 发送处理请求
    const request = {
        text_description: "一台旧笔记本电脑，还能正常使用",
        image_url: "https://example.com/laptop.jpg",
        user_location: {
            lat: 39.9042,
            lon: 116.4074
        }
    };
    
    ws.send(JSON.stringify(request));
};

// 接收消息
ws.onmessage = function(event) {
    const data = JSON.parse(event.data);
    handleMessage(data);
};

// 连接关闭
ws.onclose = function(event) {
    console.log('WebSocket 连接已关闭');
};

// 连接错误
ws.onerror = function(error) {
    console.error('WebSocket 错误:', error);
};
```

## 请求格式

### 请求参数

连接建立后，客户端需要发送一个 JSON 格式的请求：

```json
{
    "text_description": "物品文字描述（可选）",
    "image_url": "物品图片URL（可选）",
    "user_location": {
        "lat": 39.9042,
        "lon": 116.4074
    }
}
```

### 参数说明

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| `text_description` | string | 否 | 物品的文字描述，如"一台旧笔记本电脑" |
| `image_url` | string | 否 | 物品图片的URL地址 |
| `user_location` | object | 否 | 用户地理位置信息 |
| `user_location.lat` | number | 否 | 纬度坐标 |
| `user_location.lon` | number | 否 | 经度坐标 |

**注意**: `text_description` 和 `image_url` 至少需要提供一个。

## 响应格式

### 步骤更新消息

系统会实时推送每个处理步骤的进度和结果，最终在 `result_integration` 步骤中返回完整的最终数据结构。

```json
{
    "type": "step_update",
    "step": "content_analysis",
    "title": "内容分析",
    "status": "running",
    "description": "正在分析物品图片和文字内容...",
    "result": {
        "category": "电子产品",
        "subcategory": "笔记本电脑",
        "condition": "良好",
        "estimated_value": 2000,
        "brand": "Apple",
        "model": "MacBook Pro"
    },
    "error": null,
    "metadata": {
        "analysis_source": "merged",
        "has_conflicts": false
    },
    "timestamp": "2024-01-15T10:30:00Z"
}
```

### 最终结果消息

当步骤为 `result_integration` 且状态为 `completed` 时，`result` 字段包含完整的最终数据：

```json
{
    "type": "step_update",
    "step": "result_integration",
    "title": "结果整合",
    "status": "completed",
    "description": "整合所有Agent的处理结果",
    "result": {
        "success": true,
        "source": "processing_master",
        "analysis_result": {
            "category": "电子产品",
            "subcategory": "笔记本电脑",
            "condition": "良好",
            "estimated_value": 2000,
            "brand": "Apple",
            "model": "MacBook Pro"
        },
        "disposal_solution": {
            "success": true,
            "recommendations": {
                "creative_renovation": { "recommendation_score": 0.8, "reason": "适合改造" },
                "secondhand_trading": { "recommendation_score": 0.9, "reason": "价值较高" },
                "recycling_donation": { "recommendation_score": 0.6, "reason": "环保选择" }
            }
        },
        "creative_solution": {
            "success": true,
            "renovation_plan": {
                "summary": {
                    "title": "笔记本电脑创意改造方案",
                    "difficulty": "中等"
                }
            },
            "videos": [
                {
                    "title": "旧笔记本改造教程",
                    "url": "https://example.com/video1"
                }
            ]
        },
        "recycling_solution": {
            "success": true,
            "location_recommendation": {
                "locations": [
                    {
                        "name": "电子产品回收点",
                        "address": "北京市朝阳区xxx",
                        "distance": 1.2
                    }
                ]
            }
        },
        "secondhand_solution": {
            "success": true,
            "search_result": {
                "platforms": {
                    "xianyu": [
                        {
                            "title": "MacBook Pro 二手",
                            "price": 8000,
                            "url": "https://example.com/item1"
                        }
                    ]
                }
            },
            "content_result": {
                "title": "MacBook Pro 转让",
                "description": "9成新MacBook Pro，功能完好..."
            }
        },
        "processing_metadata": {
            "processing_time_seconds": 15.2,
            "agents_executed": {
                "disposal_recommendation": true,
                "creative_coordination": true,
                "recycling_coordination": true,
                "secondhand_coordination": true,
                "total_successful": 4
            }
        }
    },
    "metadata": {
        "total_processing_time": 15.2,
        "successful_agents": 4,
        "primary_recommendation": "secondhand_trading"
    },
    "timestamp": "2024-01-15T10:35:00Z"
}
```

### 处理完成消息

```json
{
    "type": "process_complete",
    "message": "处理完成",
    "timestamp": "2024-01-15T10:35:00Z"
}
```

### 错误消息

```json
{
    "type": "error",
    "error": "处理失败: 图片格式不支持",
    "timestamp": "2024-01-15T10:32:00Z"
}
```

## 响应字段说明

### 通用字段

| 字段名 | 类型 | 说明 |
|--------|------|------|
| `type` | string | 消息类型：`step_update`、`process_complete`、`error` |
| `timestamp` | string | 消息时间戳（ISO 8601格式） |

### 步骤更新字段

| 字段名 | 类型 | 说明 |
|--------|------|------|
| `step` | string | 步骤标识符 |
| `title` | string | 步骤显示名称 |
| `status` | string | 步骤状态：`pending`、`running`、`completed`、`failed` |
| `description` | string | 步骤描述信息 |
| `result` | object | 步骤结果数据（可选） |
| `error` | string | 错误信息（可选） |
| `metadata` | object | 元数据信息（可选） |

## 处理步骤说明

系统会按顺序执行以下步骤：

1. **输入验证** (`input_validation`)
   - 验证输入数据的有效性
   - 检查图片路径和文字描述格式

2. **内容分析** (`content_analysis`)
   - 分析物品图片和/或文字内容
   - 生成标准化的物品信息（类别、状态、价值等）

3. **处置路径推荐** (`disposal_recommendation`)
   - 基于分析结果推荐三大处置路径
   - 评估各路径的可行性和推荐度

4. **创意改造协调** (`creative_coordination`)
   - 生成创意改造方案
   - 搜索相关DIY视频教程

5. **回收捐赠协调** (`recycling_coordination`)
   - 推荐附近回收点和回收平台
   - 提供环保回收方案

6. **二手交易协调** (`secondhand_coordination`)
   - 搜索二手平台价格信息
   - 生成交易文案和内容

7. **结果整合** (`result_integration`)
   - 整合所有Agent的处理结果
   - 返回完整的最终数据结构

## 完整前端示例

```html
<!DOCTYPE html>
<html>
<head>
    <title>物品处置助手</title>
    <style>
        .step { margin: 10px 0; padding: 10px; border: 1px solid #ccc; }
        .pending { background-color: #f0f0f0; }
        .running { background-color: #fff3cd; }
        .completed { background-color: #d4edda; }
        .failed { background-color: #f8d7da; }
        .final-result { 
            margin: 20px 0; 
            padding: 20px; 
            border: 2px solid #28a745; 
            background-color: #f8f9fa;
            border-radius: 5px;
        }
        .result-summary, .solutions, .processing-info { 
            margin: 15px 0; 
        }
        .solution-item { 
            margin: 10px 0; 
            padding: 10px; 
            background-color: #e9ecef; 
            border-radius: 3px;
        }
    </style>
</head>
<body>
    <h1>物品处置助手</h1>
    
    <div>
        <textarea id="description" placeholder="请描述您的物品..."></textarea>
        <input type="text" id="imageUrl" placeholder="图片URL（可选）">
        <button onclick="startProcess()">开始处理</button>
    </div>
    
    <div id="steps"></div>
    
    <script>
        let ws = null;
        const stepsContainer = document.getElementById('steps');
        
        function startProcess() {
            const description = document.getElementById('description').value;
            const imageUrl = document.getElementById('imageUrl').value;
            
            if (!description && !imageUrl) {
                alert('请至少提供物品描述或图片');
                return;
            }
            
            // 清空之前的步骤
            stepsContainer.innerHTML = '';
            
            // 建立WebSocket连接
            ws = new WebSocket('ws://localhost:8000/api/v1/tasks/ws/process');
            
            ws.onopen = function() {
                console.log('连接已建立');
                
                const request = {
                    text_description: description || null,
                    image_url: imageUrl || null,
                    user_location: {
                        lat: 39.9042,
                        lon: 116.4074
                    }
                };
                
                ws.send(JSON.stringify(request));
            };
            
            ws.onmessage = function(event) {
                const data = JSON.parse(event.data);
                handleMessage(data);
            };
            
            ws.onclose = function() {
                console.log('连接已关闭');
            };
            
            ws.onerror = function(error) {
                console.error('WebSocket错误:', error);
            };
        }
        
        function handleMessage(data) {
            switch(data.type) {
                case 'step_update':
                    updateStep(data);
                    // 检查是否为最终结果
                    if (data.step === 'result_integration' && data.status === 'completed') {
                        showFinalResult(data.result);
                    }
                    break;
                case 'process_complete':
                    console.log('处理完成');
                    break;
                case 'error':
                    showError(data.error);
                    break;
            }
        }
        
        function updateStep(stepData) {
            let stepDiv = document.getElementById('step-' + stepData.step);
            
            if (!stepDiv) {
                stepDiv = document.createElement('div');
                stepDiv.id = 'step-' + stepData.step;
                stepDiv.className = 'step';
                stepsContainer.appendChild(stepDiv);
            }
            
            stepDiv.className = 'step ' + stepData.status;
            stepDiv.innerHTML = `
                <h3>${stepData.title}</h3>
                <p>状态: ${stepData.status}</p>
                <p>${stepData.description}</p>
                ${stepData.result ? '<pre>' + JSON.stringify(stepData.result, null, 2) + '</pre>' : ''}
                ${stepData.error ? '<p style="color: red;">错误: ' + stepData.error + '</p>' : ''}
            `;
        }
        
        function showError(error) {
            const errorDiv = document.createElement('div');
            errorDiv.className = 'step failed';
            errorDiv.innerHTML = `<h3>处理失败</h3><p>${error}</p>`;
            stepsContainer.appendChild(errorDiv);
        }
        
        function showFinalResult(finalData) {
            // 创建最终结果展示区域
            const finalDiv = document.createElement('div');
            finalDiv.className = 'final-result';
            finalDiv.innerHTML = `
                <h2>🎉 处理完成！最终结果</h2>
                <div class="result-summary">
                    <h3>物品分析结果</h3>
                    <p><strong>类别：</strong>${finalData.analysis_result.category}</p>
                    <p><strong>子类别：</strong>${finalData.analysis_result.subcategory}</p>
                    <p><strong>状态：</strong>${finalData.analysis_result.condition}</p>
                    <p><strong>估值：</strong>￥${finalData.analysis_result.estimated_value}</p>
                </div>
                <div class="solutions">
                    <h3>处置方案</h3>
                    ${finalData.disposal_solution ? `
                        <div class="solution-item">
                            <h4>🔍 推荐方案</h4>
                            <p>主要推荐：${finalData.processing_metadata.primary_recommendation || '暂无'}</p>
                        </div>
                    ` : ''}
                    ${finalData.creative_solution && finalData.creative_solution.success ? `
                        <div class="solution-item">
                            <h4>🎨 创意改造</h4>
                            <p>方案：${finalData.creative_solution.renovation_plan?.summary?.title || '暂无'}</p>
                            <p>视频数量：${finalData.creative_solution.videos?.length || 0} 个</p>
                        </div>
                    ` : ''}
                    ${finalData.secondhand_solution && finalData.secondhand_solution.success ? `
                        <div class="solution-item">
                            <h4>💰 二手交易</h4>
                            <p>标题：${finalData.secondhand_solution.content_result?.title || '暂无'}</p>
                            <p>平台数量：${Object.keys(finalData.secondhand_solution.search_result?.platforms || {}).length} 个</p>
                        </div>
                    ` : ''}
                    ${finalData.recycling_solution && finalData.recycling_solution.success ? `
                        <div class="solution-item">
                            <h4>♻️ 回收捐赠</h4>
                            <p>回收点数量：${finalData.recycling_solution.location_recommendation?.locations?.length || 0} 个</p>
                        </div>
                    ` : ''}
                </div>
                <div class="processing-info">
                    <p><strong>处理时间：</strong>${finalData.processing_metadata.processing_time_seconds}秒</p>
                    <p><strong>成功Agent数：</strong>${finalData.processing_metadata.agents_executed.total_successful}/4</p>
                </div>
            `;
            stepsContainer.appendChild(finalDiv);
        }
    </script>
</body>
</html>
```

## 错误处理

### 常见错误类型

1. **JSON格式错误**
   ```json
   {
       "type": "error",
       "error": "JSON格式错误: Expecting property name enclosed in double quotes"
   }
   ```

2. **参数验证失败**
   ```json
   {
       "type": "error", 
       "error": "请求参数验证失败: text_description 和 image_url 至少需要提供一个"
   }
   ```

3. **处理失败**
   ```json
   {
       "type": "error",
       "error": "处理失败: 无法访问图片URL",
       "timestamp": "2024-01-15T10:32:00Z"
   }
   ```

### 错误处理建议

1. **连接错误**: 检查网络连接和服务器状态
2. **参数错误**: 验证请求参数格式和必填字段
3. **处理错误**: 根据错误信息调整输入或重试
4. **超时处理**: 设置合理的超时时间，避免长时间等待

## 最终数据结构说明

### 完整响应结构

最终在 `result_integration` 步骤中返回的完整数据结构包含：

1. **全局分析结果** (`analysis_result`)
   - 物品类别、状态、估值等核心信息
   - 避免在各个方案中重复

2. **四大处置方案**
   - `disposal_solution`: 处置路径推荐
   - `creative_solution`: 创意改造方案
   - `recycling_solution`: 回收捐赠方案  
   - `secondhand_solution`: 二手交易方案

3. **处理元数据** (`processing_metadata`)
   - 处理时间、Agent执行情况
   - 分析来源和冲突信息

### 数据获取建议

1. **实时进度**: 监听所有 `step_update` 消息显示处理进度
2. **最终结果**: 重点关注 `result_integration` 步骤的 `result` 字段
3. **错误处理**: 任何步骤都可能失败，需要妥善处理错误情况
4. **调试建议**: 如果最终结果为空，检查服务器日志中的错误信息

### 常见问题排查

**问题**: `result_integration` 步骤状态为 `completed` 但 `result` 字段为空

**可能原因**:
1. 数据转换过程中发生异常
2. 某个子Agent返回的数据格式不正确
3. JSON序列化失败

**排查步骤**:
1. 检查服务器日志中的错误信息
2. 确认所有子Agent都成功执行
3. 检查网络连接是否稳定
