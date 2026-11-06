# 本地部署

## 是什么

这篇文档只做一件事：把 `Qwen/Qwen3.5-2B` 在当前仓库里稳定跑起来，并验证本地服务已经可访问。

## 工程中何时用

下面几种情况，直接按这篇文档执行：

1. 第一次在这台机器上部署 vLLM
2. 你想确认模型和环境是否能正常运行
3. 你要给后续 API 调用、参数调优、特性学习建立基线

## 核心 API / 用法

### 1. 创建环境并安装依赖

```bash
uv venv --python 3.12 --seed
source .venv/bin/activate

# Qwen3.5 建议直接使用 nightly wheel。
uv pip install vllm --torch-backend=auto --extra-index-url https://wheels.vllm.ai/nightly
uv pip install -U openai
uv pip install "huggingface_hub>=0.34,<1.0"
```

说明：

1. `uv venv --python 3.12 --seed` 创建 Python 3.12 虚拟环境
2. `vllm` 使用 nightly wheel，是为了对齐 `Qwen/Qwen3.5-2B` 的支持
3. `huggingface_hub` 固定 `<1.0`，避免和当前 `transformers` 依赖约束冲突

### 2. 下载模型到本地目录

```bash
python scripts/download_qwen_model.py --model-name Qwen/Qwen3.5-2B
```

执行完成后，模型目录应该是：

```bash
models/Qwen/Qwen3.5-2B
```

验证：

```bash
ls models/Qwen/Qwen3.5-2B
```

### 3. 启动最保守可用服务

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

参数说明：

1. `models/Qwen/Qwen3.5-2B` 使用本地模型目录，而不是在线拉取
2. `--host 0.0.0.0` 显式监听所有地址。在当前环境中，不加这个参数会出现服务看似启动但后续访问被拒绝的问题
3. `--tensor-parallel-size 1` 对单卡机器是正确起点
4. `--language-model-only` 避免加载当前项目不需要的多模态部分
5. `--max-model-len 4096` 先用保守上下文，降低 8GB 显存启动风险
6. `--gpu-memory-utilization 0.80` 先保守，优先追求稳定启动
7. `--enforce-eager` 在当前 WSL2 环境下更稳，适合作为第一版基线

⚠️ 这个命令启动后不要关闭终端。  
⚠️ 新测试命令必须在另一个终端执行。
⚠️ 当前环境下请保留 `--host 0.0.0.0`，否则后续 `curl`/SDK 访问可能直接被拒绝。

## 代码讲解

这里的关键不是“代码技巧”，而是部署顺序：

1. 先创建干净环境
2. 再下载模型到本地固定目录
3. 再用最保守参数启动服务
4. 最后再用 HTTP 请求验证

这样做的原因是，部署失败时你能快速知道问题在哪一层：

1. 依赖层
2. 模型文件层
3. 服务启动层
4. API 请求层

## 运行结果说明

服务启动成功后，日志里应至少满足下面两点：

1. 出现 `Starting vLLM server on http://0.0.0.0:8000`
2. 出现 `Application startup complete.`

然后在另一个终端执行：

```bash
curl --noproxy '*' http://127.0.0.1:8000/health -v
curl --noproxy '*' http://127.0.0.1:8000/v1/models -v
```

成功标准：

1. `/health` 返回 `HTTP/1.1 200 OK`
2. `/v1/models` 返回 JSON
3. JSON 中能看到 `models/Qwen/Qwen3.5-2B`

## 工程最佳实践

✅ 推荐：把启动基线固定在 `4096 + 0.80 + --enforce-eager`  
✅ 推荐：先验证 `/health`，再验证 `/v1/models`  
✅ 推荐：本地学习时使用目录加载模型  
❌ 避免：直接用 `262144` 上下文启动  
❌ 避免：启动命令和测试命令混在同一个终端执行  

## 与其他特性的关联

1. 这篇文档是 [03-offline-inference.md](/home/hiyoungman/CodeProject/PythonProject/learning-vllm-notebook/docs/vllm/03-offline-inference.md) 和 [04-online-serving.md](/home/hiyoungman/CodeProject/PythonProject/learning-vllm-notebook/docs/vllm/04-online-serving.md) 的前置
2. 成功跑通后，再看 [05-core-engine-args.md](/home/hiyoungman/CodeProject/PythonProject/learning-vllm-notebook/docs/vllm/05-core-engine-args.md)
