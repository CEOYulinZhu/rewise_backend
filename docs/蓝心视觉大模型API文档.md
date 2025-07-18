# **多模态模型 API 文档 - 同步接口**

## 1. 接口概述

本接口为多模态模型的同步调用接口，支持**图片理解**、**文本创作**、**文本提取**等多种能力。

**接口特性**:
*   **同步调用**: 客户端发起请求后，将等待服务端处理完成并一次性返回最终结果。

---

## 2. 接口信息

*   **请求方法**: `POST`
*   **请求-URL**: `[请在此处填写具体的接口URL]`
*   **接口协议**: `HTTPS`

---

## 3. 鉴权方式

所有请求都需要通过请求头（Headers）中的签名信息进行鉴权。

| 参数名称                    | 类型   | 是否必须 | 说明                                                                      |
| --------------------------- | ------ | :------- | ------------------------------------------------------------------------- |
| `Content-Type`              | string | 是       | 固定值为 `application/json`。                                              |
| `X-AI-GATEWAY-APP-ID`       | string | 是       | AIGC 官网分配的 `app_id` (见官网右上角个人资料-参赛平台-应用赛道参赛资源)。 |
| `X-AI-GATEWAY-TIMESTAMP`    | string | 是       | 请求时的 Unix 时间戳（以秒为单位）。                                        |
| `X-AI-GATEWAY-NONCE`        | string | 是       | 8 位随机字符串，用于防止重放攻击。                                          |
| `X-AI-GATEWAY-SIGNED-HEADERS` | string | 是       | 固定值为 `"x-ai-gateway-app-id;x-ai-gateway-timestamp;x-ai-gateway-nonce"`。 |
| `X-AI-GATEWAY-SIGNATURE`    | string | 是       | 请求签名字符串。具体计算方式请参考 **《鉴权方式文档》** 中的签名计算部分。      |

---

## 4. 请求参数

### 4.1 URL 参数

| 参数名称    | 类型   | 是否必须 | 是否需 URL-Encode | 说明                                       |
| ----------- | ------ | :------- | :---------------- | ------------------------------------------ |
| `requestId` | string | 是       | 是                | 本次请求的唯一标识 ID，建议使用 UUID 生成。 |

### 4.2 Body 参数

请求 Body 为 JSON 格式。

| 参数名称  | 类型     | 是否必须 | 默认值 | 说明                                                                                                                                                                                                    |
| --------- | -------- | :------- | :----- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `prompt`  | string   | 否       | 无     | 单轮问答内容。`prompt` 和 `messages` 必须提供其中一个。                                                                                                                                                   |
| `messages`| object[] | 否       | 无     | 多轮对话上下文。`prompt` 和 `messages` 必须提供其中一个。<br> **注意**: <br> 1. `messages` 成员不能为空，1个成员表示单轮对话，多个成员表示多轮对话。<br> 2. 最后一个 `message` 为当前请求，前面的为历史对话。<br> 3. 所有 `content` 的总长度不能超过模型限制。 |
| `model`   | string   | 是       | 无     | 指定要使用的模型，可选值如下：<br> - `BlueLM-Vision-prd` (图片理解、文本创作、文本提取，上下文4096)<br> - `vivo-BlueLM-V-2.0` (文本提取，输入+输出 2048 token)                       |
| `sessionId`| string   | 是       | 无     | 会话 ID，建议使用 UUID。当使用 `prompt` 时，系统会依据此 ID 关联历史消息。`messages` 方式不受 `sessionId` 影响。                                                                                              |
| `extra`   | map      | 否       | 无     | 用于传递模型专属的超参数，详见下方 **4.3 模型超参数 (`extra`) 详解**。                                                                                                                                      |

#### `messages` 成员结构

| 参数      | 类型   | 是否必须 | 说明       |
| --------- | ------ | :------- | ---------- |
| `role`    | string | 是       | 角色，固定为 `user`。 |
| `content` | string | 是       | 对话内容。 |

### 4.3 模型超参数 (`extra`) 详解

#### 针对模型: `vivo-BlueLM-V-2.0`

| 参数               | 类型         | 取值范围                  | 建议值 | 说明                                                                                                                                                           |
| ------------------ | ------------ | ------------------------- | :----- | -------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `temperature`      | float        | `(0.0, 2.0)`              | 0.9    | 采样温度，控制输出的随机性。值越大，输出越随机、越具创造性；值越小，输出越稳定、越确定。不建议与 `top_p` 同时调整。                                        |
| `top_p`            | float        | `(0.0, 1.0)`              | 0.7    | 核取样。模型仅从概率质量最高的 `top_p` 候选集中选择 token。例如，`0.1` 表示仅考虑前 10% 的候选。不建议与 `temperature` 同时调整。                                 |
| `top_k`            | integer      | `[0, ∞)`                  | 50     | 在概率最高的 `k` 个 token 中进行采样。                                                                                                                         |
| `max_tokens`       | integer      | `(0, 8000]`               | 2048   | 生成内容的最大 token 长度。                                                                                                                                    |
| `repetition_penalty` | float        | `> 0` (通常不超过 2.0)    | 1.02   | 重复惩罚。`1.0` 表示不惩罚。值越大，模型生成重复内容の可能性越低。                                                                                                 |
| `stop`             | list[string] | -                         | -      | 一个或多个字符串列表，当模型生成到这些字符串时会立即停止，且生成结果不包含这些停止词。                                                                             |
| `ignore_eos`       | boolean      | `true` / `false`          | -      | 是否忽略 `eos` (end-of-sequence) 标记。                                                                                                                        |
| `skip_special_tokens`| boolean      | `true` / `false`          | -      | 是否在解码阶段跳过特殊 token。                                                                                                                                 |

---

## 5. 响应结果

### 5.1 响应 Body 结构

| 参数    | 类型   | 是否必须 | 说明                                       |
| ------- | ------ | :------- | ------------------------------------------ |
| `code`  | number | 是       | 结果码。`0` 表示成功，其它值表示失败。详见 **6. 错误码**。 |
| `msg`   | string | 是       | 对结果码的文本描述，例如 "done." 或具体的错误信息。 |
| `data`  | object | 否       | `code` 为 `0` 时返回的业务数据。详见下方 **5.2 data 对象结构**。 |

### 5.2 `data` 对象结构

| 参数      | 类型   | 是否必须 | 说明                 |
| --------- | ------ | :------- | -------------------- |
| `content` | string | 是       | 大模型生成的内容。   |
| `sessionId`| string | 是       | 与请求一致的会话 ID。 |
| `requestId`| string | 是       | 与请求一致的请求 ID。 |
| `provider`| string | 是       | 模型提供方，例如 `vivo`。 |
| `model`   | string | 是       | 本次使用的模型名称。 |
| `usage`   | object | 是       | Token 使用量等信息。 |

### 5.3 响应示例

#### 示例 1: 正常响应

```json
{
    "code": 0,
    "msg": "done.",
    "data": {
        "sessionId": "736952dd-a438-4835-a237-8cae6bbff94d",
        "requestId": "ce7ff5d0-39c1-4db7-84e3-103bb03d32a3",
        "content": "这是一张抽象背景的图片，主要以灰色、黑色和红色为主色调。图片中有渐变模糊效果，从左到右呈现出渐变的颜色过渡，从灰色到黑色，中间带有红色的渐变。整体看起来像是一张模糊的照片或者艺术效果的图片。",
        "reasoningContent": null,
        "image": null,
        "functionCall": null,
        "toolCall": null,
        "toolCalls": null,
        "contentList": null,
        "searchInfo": null,
        "usage": {
            "promptTokens": 819,
            "completionTokens": 53,
            "totalTokens": 872,
            "duration": null,
            "imageCost": null,
            "inputImages": null,
            "costLevel": null
        },
        "provider": "vivo",
        "clearHistory": null,
        "searchExtra": null,
        "model": "vivo-BlueLM-V-2.0",
        "finishReason": "stop",
        "score": 0.0
    }
}
```

#### 示例 2: 触发内容审核

```json
{
    "code": 1007,
    "msg": "抱歉，当前输入的内容我无法处理。如有需要，请尝试发送其他内容，我会尽力提供帮助。",
    "data": {}
}
```

#### 示例 3: 其他错误 (如权限过期)

```json
{
    "code": 2001,
    "msg": "permission expires",
    "data": {}
}
```

---

## 6. 错误码

| Code  | 错误信息 (msg)                              | 说明                                                           |
| ----- | ------------------------------------------- | -------------------------------------------------------------- |
| 1001  | `param ‘requestId’ can’t be empty` 等       | **参数异常**。通常是缺少必填参数或参数格式错误。                   |
| 1007  | `抱歉，xxx`                                 | **内容审核**。输入或输出内容触发了平台的安全审核机制。           |
| 2001  | `permission expires`                        | **权限错误**。权限已过期，请检查您的鉴权信息。                 |
| 30001 | `no model access permission`                | **权限错误**。没有目标模型的访问权限，请联系平台管理员。         |
| 30001 | `hit model rate limit`                      | **频率限制**。触发了模型的 QPS (每秒请求数) 限流，请降低请求频率。 |
| 2003  | `today usage limit`                         | **用量限制**。已达到单日调用量上限，请次日再试。                 |