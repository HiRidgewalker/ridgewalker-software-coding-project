# 核心参数

前置阅读：[02-local-deployment.md](/home/hiyoungman/CodeProject/PythonProject/learning-vllm-notebook/docs/vllm/02-local-deployment.md)

## 是什么

这篇文档只讲当前项目最常改、最影响部署结果的 4 个参数。你不需要先学全量 engine args，只需要先掌握这些高频参数。

## 工程中何时用

1. 服务启动失败
2. 显存不足
3. 想提高上下文长度
4. 想建立单卡部署基线

## 核心 API / 用法

### 1. `--max-model-len`

作用：控制允许的最大上下文长度。

基线：

```bash
--max-model-len 4096
```

什么时候改：

1. 启动稳定后再加到 `8192`
2. 只有显存还足够时再往上提

⚠️ 对 `Qwen/Qwen3.5-2B`，不要把模型卡的 `262144` 当成当前仓库默认值。

### 2. `--gpu-memory-utilization`

作用：限制 vLLM 可用的 GPU 显存占比。

基线：

```bash
--gpu-memory-utilization 0.80
```

什么时候改：

1. 启动稳定后再试 `0.85`
2. 机器资源紧时维持 `0.80`

⚠️ 一开始就设太高，会让排障成本明显上升。

### 3. `--tensor-parallel-size`

作用：控制张量并行大小。

基线：

```bash
--tensor-parallel-size 1
```

工程结论：

1. 单卡环境固定用 `1`
2. 当前仓库不展开多卡并行

### 4. `--language-model-only`

作用：对当前模型启用纯文本模式。

基线：

```bash
--language-model-only
```

工程结论：

1. 当前仓库只做文本服务，默认开启
2. 对 `Qwen/Qwen3.5-2B` 这是正确的省资源选择

## 代码讲解

当前项目的保守启动基线：

```bash
vllm serve models/Qwen/Qwen3.5-2B \
  --port 8000 \
  --tensor-parallel-size 1 \
  --language-model-only \
  --max-model-len 4096 \
  --gpu-memory-utilization 0.80 \
  --enforce-eager
```

如何理解这组组合：

1. `4096` 先解决“能启动”
2. `0.80` 先解决“别太激进”
3. `1` 对单卡是唯一正确起点
4. `language_model_only` 先裁掉不需要的负担

## 运行结果说明

调这些参数时只看四件事：

1. 服务能不能启动
2. 服务会不会立刻退出
3. `/v1/models` 能不能正常返回
4. `chat/completions` 能不能正常生成

## 工程最佳实践

✅ 推荐：每次只改一个主参数  
✅ 推荐：优先调整 `max_model_len`，其次才是显存利用率  
✅ 推荐：单卡基线固定 `tensor_parallel_size=1`  
❌ 避免：一次同时改上下文、显存占比、并行度  
❌ 避免：把模型卡最大上下文直接照搬到本地学习环境  

## 与其他特性的关联

1. 这些参数直接影响 [04-online-serving.md](/home/hiyoungman/CodeProject/PythonProject/learning-vllm-notebook/docs/vllm/04-online-serving.md) 的启动成功率
2. 具体实验记录见 [10-experiments.md](/home/hiyoungman/CodeProject/PythonProject/learning-vllm-notebook/docs/vllm/10-experiments.md)
