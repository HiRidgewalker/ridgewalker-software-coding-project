# OpenAI-Compatible API

前置阅读：[04-online-serving.md](/home/hiyoungman/CodeProject/PythonProject/learning-vllm-notebook/docs/vllm/04-online-serving.md)

## 是什么

vLLM 提供 OpenAI-compatible HTTP 接口。对这个仓库来说，这意味着你可以直接用 OpenAI Python SDK 去调用本地 vLLM 服务，而不需要自己重新设计一套客户端协议。

## 工程中何时用

1. 你已经有 OpenAI SDK 调用代码，希望切到本地模型
2. 你要给后端服务、脚本、Agent 应用接入本地模型
3. 你要统一本地模型和云模型的调用方式

## 核心 API / 用法

本仓库现成脚本是 [openai_client_demo.py](/home/hiyoungman/CodeProject/PythonProject/learning-vllm-notebook/scripts/openai_client_demo.py)。

```python
from openai import OpenAI


LOCAL_MODEL_ID = "models/Qwen/Qwen3.5-2B"


def main() -> None:
    client = OpenAI(
        base_url="http://localhost:8000/v1",
        api_key="EMPTY",
    )

    models = client.models.list()
    print("=== Available Models ===")
    for model in models.data:
        print(model.id)
    print()

    response = client.chat.completions.create(
        model=LOCAL_MODEL_ID,
        messages=[
            {
                "role": "system",
                "content": "You are a concise assistant focused on vLLM deployment.",
            },
            {
                "role": "user",
                "content": "请用三点说明 vLLM 本地部署时最重要的调参项。",
            },
        ],
        temperature=0.7,
        max_tokens=256,
    )

    print("=== Chat Response ===")
    print(response.choices[0].message.content)
```

运行命令：

```bash
python scripts/openai_client_demo.py
```

## 代码讲解

1. `base_url="http://localhost:8000/v1"` 指向本地 vLLM 服务
2. `api_key="EMPTY"` 只是为了满足 SDK 参数要求，不代表在调用 OpenAI 云服务
3. `client.models.list()` 用于确认服务暴露了哪些模型
4. `client.chat.completions.create(...)` 是最常用的请求入口
5. `model` 字段要和 `/v1/models` 返回的模型 id 对齐

⚠️ 不要想当然地把模型名写成 `Qwen/Qwen3.5-2B`，当前仓库服务返回的是 `models/Qwen/Qwen3.5-2B`。  
⚠️ 如果这里报连接错误，优先检查服务进程是否还活着。

## 运行结果说明

成功时应看到两段输出：

1. `=== Available Models ===`
2. `=== Chat Response ===`

第一段验证服务和模型注册正常，第二段验证聊天接口可用。

## 工程最佳实践

✅ 推荐：先 `models.list()`，再发聊天请求  
✅ 推荐：客户端里的 `model` 值以 `/v1/models` 返回结果为准  
✅ 推荐：把本地地址固定为 `http://localhost:8000/v1`  
❌ 避免：直接复用云端模型 id，不核对本地服务返回值  
❌ 避免：客户端失败时只看 SDK 报错，不回头检查服务端状态  

## 与其他特性的关联

1. `curl` 调用见 [09-curl-and-jq.md](/home/hiyoungman/CodeProject/PythonProject/learning-vllm-notebook/docs/vllm/09-curl-and-jq.md)
2. 结构化输出、工具调用等上层能力都建立在这个接口之上
