# 在线服务

前置阅读：[02-local-deployment.md](/home/hiyoungman/CodeProject/PythonProject/learning-vllm-notebook/docs/vllm/02-local-deployment.md)

## 是什么

在线服务就是使用 `vllm serve` 启动一个常驻进程，对外提供 HTTP API。只要这个进程还在运行，其他程序就可以持续访问它。

## 工程中何时用

1. 你要让 Python、前端、后端服务持续调用模型
2. 你要复用 OpenAI-compatible 接口
3. 你要把模型当成一个稳定服务，而不是一次性脚本

## 核心 API / 用法

启动命令：

```bash
vllm serve models/Qwen/Qwen3.5-2B \
  --host 0.0.0.0 \
  --port 8000 \
  --tensor-parallel-size 1 \
  --language-model-only \
  --max-model-len 4096 \
  --gpu-memory-utilization 0.80 \
  --enforce-eager
```

健康检查：

```bash
curl --noproxy '*' -v http://127.0.0.1:8000/health
```

模型列表：

```bash
curl --noproxy '*' -v http://127.0.0.1:8000/v1/models
```

最小聊天请求：

```bash
curl --noproxy '*' -s http://127.0.0.1:8000/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "models/Qwen/Qwen3.5-2B",
    "messages": [
      {"role": "user", "content": "你好"}
    ],
    "temperature": 0.0,
    "max_tokens": 16
  }'
```

⚠️ 本机若配置了代理，测试本地服务时要显式加 `--noproxy '*'`。  
⚠️ 如果你已经看到 shell 提示符返回，说明服务已经停了，不要再继续测接口。
⚠️ 当前环境下要显式添加 `--host 0.0.0.0`，否则即使日志显示服务已启动，后续访问仍可能被拒绝。

## 代码讲解

在线服务和离线推理的区别只有两点最关键：

1. 离线推理是脚本直接用模型对象
2. 在线服务是其他程序通过 HTTP API 用模型

你要关注的不是所有日志，而是两个状态：

1. 服务是否持续驻留
2. 本地端口 `8000` 是否真的可访问

## 运行结果说明

启动成功时：

1. 日志里会出现 `Application startup complete.`
2. `/health` 返回 `200 OK`
3. `/v1/models` 返回 JSON

聊天请求成功时，返回 JSON 中至少有：

```json
{
  "choices": [
    {
      "message": {
        "content": "..."
      }
    }
  ]
}
```

## 工程最佳实践

✅ 推荐：启动成功后先测 `/health` 再测 `/v1/models`  
✅ 推荐：本地调试时统一使用 `127.0.0.1:8000`  
✅ 推荐：先确认端口监听，再确认生成结果  
❌ 避免：用代理去访问本地服务  
❌ 避免：只看日志，不做 HTTP 层验证  

## 与其他特性的关联

1. 在线服务是 [06-openai-compatible-api.md](/home/hiyoungman/CodeProject/PythonProject/learning-vllm-notebook/docs/vllm/06-openai-compatible-api.md) 的前置
2. 参数含义见 [05-core-engine-args.md](/home/hiyoungman/CodeProject/PythonProject/learning-vllm-notebook/docs/vllm/05-core-engine-args.md)
