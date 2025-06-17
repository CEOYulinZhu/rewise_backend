### **VIVO-BlueLM 大模型 completions API 文档**

#### **1. 接口概述**

本接口用于调用 VIVO BlueLM 大模型进行文本生成（completions）。它是一个同步接口，接收一次请求后，会一次性返回完整的模型生成结果。

| 项目 | 说明 |
| :--- | :--- |
| **接口地址** | `https://api-ai.vivo.com.cn/vivogpt/completions` |
| **请求方法** | `POST` |
| **内容类型** | `application/json` |

---

#### **2. 鉴权 (Authentication)**

所有请求都必须在请求头（Headers）中包含以下鉴权参数，以验证请求的合法性。

| 参数名称 | 类型 | 是否必须 | 说明 |
| :--- | :--- | :--- | :--- |
| `Content-Type` | string | 是 | 固定值为 `application/json`。 |
| `X-AI-GATEWAY-APP-ID` | string | 是 | 在AIGC官网为您的团队分配的 `app_id`。 |
| `X-AI-GATEWAY-TIMESTAMP` | string | 是 | 请求发出的Unix时间戳（以秒为单位），例如 `1677652686`。 |
| `X-AI-GATEWAY-NONCE` | string | 是 | 8位随机字符串，用于防止重放攻击。 |
| `X-AI-GATEWAY-SIGNED-HEADERS` | string | 是 | 参与签名的请求头列表，固定值为 `x-ai-gateway-app-id;x-ai-gateway-timestamp;x-ai-gateway-nonce`。 |
| `X-AI-GATEWAY-SIGNATURE` | string | 是 | 请求签名字符串。该签名是基于 `app_id`, `timestamp`, `nonce` 等参数，通过特定算法计算得出的摘要。详细计算方法请参考《鉴权方式文档》。 |

---

#### **3. 请求 (Request)**

##### **3.1 URL 参数**

| 参数 | 类型 | 是否必须 | URL Encode | 说明 |
| :--- | :--- | :--- | :--- | :--- |
| `requestId` | string | 是 | 是 | 标识单次请求的唯一ID，建议使用UUID生成。 |

##### **3.2 请求体 (Body)**

请求体为 JSON 格式，包含以下参数：

| 参数 | 类型 | 是否必须 | 默认值 | 说明 |
| :--- | :--- | :--- | :--- | :--- |
| `prompt` | string | 否 | 无 | 单轮问答场景。与 `messages` 参数二选一。 |
| `messages` | object[] | 否 | 无 | 多轮对话场景。与 `prompt` 参数二选一。详情见 **3.2.1 `messages` 对象结构**。 |
| `model` | string | 是 | 无 | 指定使用的模型。可选值：`vivo-BlueLM-TB-Pro` (输入+输出总长8k，输入限制7k)。 |
| `sessionId` | string | 是 | 无 | 会话ID，用于追踪一次完整的对话流程，建议使用UUID。当使用 `prompt` 时，会关联相同 `sessionId` 的历史消息。`messages` 方式不受 `sessionId` 影响。 |
| `systemPrompt` | string | 否 | 无 | 系统级人设（System Prompt）。用于定义模型的角色、行为和回复风格。 |
| `extra` | object | 否 | 无 | 模型高级超参数配置。详情见 **3.2.2 `extra` 对象结构**。 |

###### **3.2.1 `messages` 对象结构**

`messages` 是一个对象数组，用于构建多轮对话的上下文。

**对象成员:**

| 参数 | 类型 | 是否必须 | 说明 |
| :--- | :--- | :--- | :--- |
| `role` | string | 是 | 角色，可选值为 `user`, `assistant`, `system`, `function`。 |
| `content` | string | 是 | 消息的具体内容。 |

**使用规则:**

*   数组不能为空。单个成员表示单轮对话，多个成员表示多轮对话。
*   最后一个 `message` 成员应为当前用户的提问。
*   为保持对话轮次完整，数组的成员数量必须为奇数。
*   `role` 的顺序必须是 `user`, `assistant`, `user`, `assistant`, ... 交替出现。
*   所有 `content` 的总长度不能超过模型的最大限制（7k），否则将报错。

**`role` 详细说明:**

| 角色 | 说明 |
| :--- | :--- |
| `user` | 表示用户输入的内容。 |
| `assistant` | 表示模型的回复。 |
| `system` | 定义模型的全局行为或人设，通常放在 `messages` 数组的开头。 |
| `function` | 工具调用的返回结果，用于 Function Calling 场景。 |

###### **3.2.2 `extra` 对象结构 (模型超参数)**

`extra` 对象用于微调模型的生成行为。

| 参数 | 类型 | 范围 | 默认值 | 说明 |
| :--- | :--- | :--- | :--- | :--- |
| `temperature` | float | (0.0, 2.0] | 0.9 | 采样温度。值越大，输出越随机和有创意；值越小，输出越确定和稳定。不建议与 `top_p` 同时调整。 |
| `top_p` | float | (0.0, 1.0) | 0.7 | 核采样（Top-p）参数。模型仅在概率最高的 `top_p` 候选词中进行采样。例如，`0.7` 表示只考虑累积概率达到70%的词汇。不建议与 `temperature` 同时调整。 |
| `top_k` | integer | [1, ∞) | 50 | 在概率最高的 `k` 个词中进行采样。 |
| `max_new_tokens` | integer | [1, 8000] | 2048 | 指定模型生成的最大Token数量。 |
| `repetition_penalty` | float | > 0 | 1.02 | 重复惩罚系数。大于1.0会降低重复内容的出现概率，小于1.0则会鼓励重复。 |

---

#### **4. 响应 (Response)**

响应体为 JSON 格式。

##### **4.1 成功响应 (`code: 0`)**

**根对象结构:**

| 参数 | 类型 | 是否必须 | 说明 |
| :--- | :--- | :--- | :--- |
| `code` | number | 是 | 结果码，`0` 表示成功。 |
| `data` | object | 是 | 响应数据，结构见下表。 |
| `msg` | string | 是 | 附加信息，成功时通常为 `done.`。 |

**`data` 对象结构:**

| 参数 | 类型 | 是否必须 | 说明 |
| :--- | :--- | :--- | :--- |
| `content` | string | 是 | 模型生成的核心内容。 |
| `sessionId` | string | 是 | 与请求中一致的会话ID。 |
| `requestId` | string | 是 | 与请求中一致的请求ID。 |
| `provider` | string | 是 | 模型提供方，固定为 `vivo`。 |
| `model` | string | 是 | 使用的模型名称，例如 `vivo-BlueLM-TB-Pro`。 |

##### **4.2 错误响应 (`code != 0`)**

当请求发生错误时，`code` 为非零值，`msg` 字段会提供错误信息，`data` 对象通常为空 `{}`。

---

#### **5. 示例**

##### **示例 1: 正常成功响应**

```json
{
  "code": 0,
  "data": {
    "sessionId": "7b666a7aa0a811eeb5aad8bbc1c0d6bd",
    "requestId": "891483e6-3503-45db-808a-ab28672cc175",
    "content": "周海媚并没有去世，她依然活跃在演艺圈中。周海媚是中国香港影视女演员，出生于1966年，曾经在多部电视剧和电影中担任主演，如《倚天屠龙记》、《杨门女将之军令如山》等。",
    "provider": "vivo",
    "model": "vivo-BlueLM-TB-Pro"
  },
  "msg": "done."
}
```

##### **示例 2: 触发内容审核**

```json
{
  "code": 1007,
  "data": {},
  "msg": "抱歉，当前输入的内容我无法处理。如有需要，请尝试发送其他内容，我会尽力提供帮助。"
}
```

##### **示例 3: 其他通用错误（如权限过期）**

```json
{
  "code": 2001,
  "data": {},
  "msg": "permission expires"
}
```

---

#### **6. 错误码**

| Code | 错误信息 (msg) | 说明 |
| :--- | :--- | :--- |
| 1001 | `param ‘requestId’ can’t be empty` | 参数异常，通常是缺少必填参数或参数格式不正确。 |
| 1007 | `抱歉，xxx` | 输入或输出内容触发了平台的安全审核策略。 |
| 2001 | `permission expires` | 鉴权失败，通常是 `app_id` 无效或签名错误、过期。 |
| 2003 | `today usage limit` | 已达到当日的调用量上限。 |
| 30001 | `no model access permission` | 没有目标模型的访问权限。 |
| 30001 | `hit model rate limit` | 触发了模型的QPS（每秒请求数）限制，请降低请求频率。 |