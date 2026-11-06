# curl 和 jq 速查

前置阅读：[04-online-serving.md](/home/hiyoungman/CodeProject/PythonProject/learning-vllm-notebook/docs/vllm/04-online-serving.md)

## 是什么

这篇文档只做命令速查。你需要验证本地 vLLM 服务、查看 JSON 结果、提取关键字段时，直接看这里。

## 工程中何时用

1. 你要确认服务是否活着
2. 你要查看模型列表
3. 你要直接发聊天请求
4. 你要从 JSON 响应里提取正文

## 核心 API / 用法

### 1. 健康检查

```bash
curl --noproxy '*' -v http://127.0.0.1:8000/health
```

常用参数说明：

1. `--noproxy '*'`：强制本次请求不走代理。⚠️ 本地调试时很常用，否则请求可能被系统代理劫持
2. `-v`：输出请求头、响应头、连接过程。排查 404、500、连接拒绝时优先打开
3. `-s`：静默模式，不显示进度条，适合把结果继续管道给 `jq`
4. `-H "Content-Type: application/json"`：显式声明请求体是 JSON。发送 POST JSON 时基本都要加
5. `-d '...'`：请求体内容。只要传了 `-d`，`curl` 默认就会使用 `POST`

### 2. 查看模型列表

```bash
curl --noproxy '*' -s http://127.0.0.1:8000/v1/models | jq
```

提取模型 id：

```bash
curl --noproxy '*' -s http://127.0.0.1:8000/v1/models | jq -r '.data[].id'
```

### 3. 最小聊天请求

```bash
curl --noproxy '*' -s http://127.0.0.1:8000/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "models/Qwen/Qwen3.5-2B",
    "messages": [
      {"role": "user", "content": "请用一句话介绍 vLLM。"}
    ],
    "max_tokens": 64
  }' | jq
```

只提取正文：

```bash
curl --noproxy '*' -s http://127.0.0.1:8000/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "models/Qwen/Qwen3.5-2B",
    "messages": [
      {"role": "user", "content": "请用一句话介绍 vLLM。"}
    ],
    "max_tokens": 64
  }' | jq -r '.choices[0].message.content'
```

### 4. 排障时的推荐写法

```bash
curl --noproxy '*' -v http://127.0.0.1:8000/v1/models
```

### 5. 流式输出

```bash
curl --noproxy '*' -N http://127.0.0.1:8000/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "models/Qwen/Qwen3.5-2B",
    "messages": [
      {"role": "user", "content": "请用三点说明 vLLM 的核心优势。"}
    ],
    "max_tokens": 128,
    "stream": true
  }'
```

说明：

1. `-N`：关闭输出缓冲，流式返回时立即打印每个数据块
2. `"stream": true`：要求服务端按增量结果持续返回，而不是等完整结果一次性返回
3. 成功时你会看到多行 `data: {...}`，最后以 `data: [DONE]` 结束

### 6. 最常用的 `jq` 写法

先准备一个完整 JSON 样例，后面的 `jq` 命令都基于这个结构：

```json
{
  "id": "chatcmpl-demo-001",
  "object": "chat.completion",
  "created": 1710000000,
  "model": "models/Qwen/Qwen3.5-2B",
  "choices": [
    {
      "index": 0,
      "message": {
        "role": "assistant",
        "content": "vLLM 是一个高吞吐、低延迟的大模型推理引擎。"
      },
      "finish_reason": "stop"
    }
  ],
  "usage": {
    "prompt_tokens": 18,
    "completion_tokens": 20,
    "total_tokens": 38
  }
}
```

你可以先把这个 JSON 保存成 `response.json`，然后直接跑下面这些命令。

格式化整个 JSON：

```bash
jq '.' response.json
```

输出结果会是格式化后的完整 JSON，便于你先看清字段结构。

提取字段：

```bash
jq '.usage' response.json
```

输出结果：

```json
{
  "prompt_tokens": 18,
  "completion_tokens": 20,
  "total_tokens": 38
}
```

提取数组字段：

```bash
jq -r '.choices[].finish_reason' response.json
```

输出结果：

```text
stop
```

提取聊天正文：

```bash
jq -r '.choices[0].message.content' response.json
```

输出结果：

```text
vLLM 是一个高吞吐、低延迟的大模型推理引擎。
```

如果你要处理 `/v1/models` 结果，可以看这个模型列表示例：

```json
{
  "object": "list",
  "data": [
    {
      "id": "models/Qwen/Qwen3.5-2B",
      "object": "model",
      "created": 1710000000,
      "owned_by": "vllm"
    },
    {
      "id": "models/Qwen/Qwen2.5-7B-Instruct",
      "object": "model",
      "created": 1710000001,
      "owned_by": "vllm"
    }
  ]
}
```

提取所有模型 id：

```bash
jq -r '.data[].id' models.json
```

输出结果：

```text
models/Qwen/Qwen3.5-2B
models/Qwen/Qwen2.5-7B-Instruct
```

## 代码讲解

这里只强调三组工程规则：

1. 本地调试默认加 `--noproxy '*'`
2. 排障阶段优先用 `curl -v`，不要一开始就只看 `jq`
3. `jq` 处理前先确认 JSON 结构，再写提取表达式

原因：

1. 代理是最常见的本地请求干扰项
2. `jq` 只适合在请求已经成功时做结果提取
3. JSON 路径写错时，你会误以为是接口没返回数据，实际上往往只是字段层级没看清

## 运行结果说明

1. `/health` 成功时应返回 `200 OK`
2. `/v1/models` 成功时应返回带 `data` 的 JSON
3. `chat/completions` 成功时应能提取出 `.choices[0].message.content`

## 工程最佳实践

✅ 推荐：排障时先 `curl -v`，确认 HTTP 层通了再接 `jq`  
✅ 推荐：客户端中的 `model` 值直接复制 `/v1/models` 返回值  
❌ 避免：本地服务调试时忘记绕过代理  
❌ 避免：只记聊天接口，不验证健康检查和模型列表  

## 与其他特性的关联

1. 本文档服务于 [04-online-serving.md](/home/hiyoungman/CodeProject/PythonProject/learning-vllm-notebook/docs/vllm/04-online-serving.md)
2. 如果命令失败，直接回看 [08-troubleshooting.md](/home/hiyoungman/CodeProject/PythonProject/learning-vllm-notebook/docs/vllm/08-troubleshooting.md)
