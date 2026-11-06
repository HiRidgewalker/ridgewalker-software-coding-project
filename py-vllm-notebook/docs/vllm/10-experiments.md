# 参数实验记录

前置阅读：[05-core-engine-args.md](/home/hiyoungman/CodeProject/PythonProject/learning-vllm-notebook/docs/vllm/05-core-engine-args.md)

## 是什么

这篇文档用于记录你在当前机器上对 vLLM 启动参数的实际实验结果。它不是泛用模板，而是服务于当前仓库和当前模型。

## 工程中何时用

1. 你已经稳定跑通基线部署
2. 你准备提升上下文长度
3. 你想记录不同参数下的启动稳定性

## 核心 API / 用法

建议只做下面三组实验：

### 实验 1：保守基线

```bash
vllm serve models/Qwen/Qwen3.5-2B \
  --port 8000 \
  --tensor-parallel-size 1 \
  --language-model-only \
  --max-model-len 4096 \
  --gpu-memory-utilization 0.80 \
  --enforce-eager
```

### 实验 2：提升上下文

```bash
vllm serve models/Qwen/Qwen3.5-2B \
  --port 8000 \
  --tensor-parallel-size 1 \
  --language-model-only \
  --max-model-len 8192 \
  --gpu-memory-utilization 0.80 \
  --enforce-eager
```

### 实验 3：提升显存利用率

```bash
vllm serve models/Qwen/Qwen3.5-2B \
  --port 8000 \
  --tensor-parallel-size 1 \
  --language-model-only \
  --max-model-len 8192 \
  --gpu-memory-utilization 0.85 \
  --enforce-eager
```

建议记录表：

| 实验 | `max_model_len` | `gpu_memory_utilization` | 启动是否成功 | `/health` | `/v1/models` | 聊天请求 | 备注 |
|---|---:|---:|---|---|---|---|---|
| 1 | 4096 | 0.80 | | | | | |
| 2 | 8192 | 0.80 | | | | | |
| 3 | 8192 | 0.85 | | | | | |

## 代码讲解

实验的核心规则只有一个：

1. 每次只改一个主变量

当前仓库里，最值得记录的不是复杂性能指标，而是下面这些直接影响工程可用性的结果：

1. 能不能启动
2. 会不会稳定驻留
3. API 能不能正常返回

## 运行结果说明

每次实验完成后，至少执行下面三条验证：

```bash
curl --noproxy '*' -v http://127.0.0.1:8000/health
curl --noproxy '*' -s http://127.0.0.1:8000/v1/models | jq -r '.data[].id'
python scripts/openai_client_demo.py
```

## 工程最佳实践

✅ 推荐：先记录“是否成功”，再记录“性能如何”  
✅ 推荐：先扩上下文，再调显存占比  
❌ 避免：在服务都没稳定时就做复杂 benchmark  

## 与其他特性的关联

1. 这篇文档是 [05-core-engine-args.md](/home/hiyoungman/CodeProject/PythonProject/learning-vllm-notebook/docs/vllm/05-core-engine-args.md) 的落地记录
2. 如果实验失败，回看 [08-troubleshooting.md](/home/hiyoungman/CodeProject/PythonProject/learning-vllm-notebook/docs/vllm/08-troubleshooting.md)
