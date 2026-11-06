# learning-vllm-notebook

vLLM 用于把大语言模型高效部署成可调用的推理服务，本仓库聚焦本地部署 `Qwen/Qwen3.5-2B`。

## 与同类方案的核心差异

| 方案 | 结论 |
|---|---|
| vLLM | 优先用于高效推理服务和 OpenAI-compatible 接口暴露 |
| Transformers | 更适合模型研究、脚本实验、训练与推理一体化开发 |
| Ollama | 更适合本地快速体验，不适合作为本仓库的工程主线 |
| TGI | 也是服务化推理方案，但本仓库当前主线选 vLLM，不做双栈展开 |

## 适用场景

适合：

1. 你要在本机部署 Hugging Face 模型
2. 你要把模型暴露成 HTTP 服务
3. 你要用 OpenAI-compatible 方式访问本地模型
4. 你要学习 vLLM 的常用部署、调用和排障方法

不适合：

1. 你主要想研究模型训练或微调
2. 你只想做最轻量的本地聊天试玩
3. 你当前目标是多机集群级调度而不是单机落地

## 文档导航

1. [总览](/home/hiyoungman/CodeProject/PythonProject/learning-vllm-notebook/docs/vllm/01-overview.md)
   - 先看这篇，明确这个仓库的目标、范围和阅读顺序
2. [本地部署](/home/hiyoungman/CodeProject/PythonProject/learning-vllm-notebook/docs/vllm/02-local-deployment.md)
   - 最短可执行链路，先把服务跑起来
3. [离线推理](/home/hiyoungman/CodeProject/PythonProject/learning-vllm-notebook/docs/vllm/03-offline-inference.md)
   - 理解离线推理的角色和脚本用法
4. [在线服务](/home/hiyoungman/CodeProject/PythonProject/learning-vllm-notebook/docs/vllm/04-online-serving.md)
   - 理解 `vllm serve` 的启动和验证
5. [核心参数](/home/hiyoungman/CodeProject/PythonProject/learning-vllm-notebook/docs/vllm/05-core-engine-args.md)
   - 掌握最影响部署结果的参数
6. [OpenAI-Compatible API](/home/hiyoungman/CodeProject/PythonProject/learning-vllm-notebook/docs/vllm/06-openai-compatible-api.md)
   - 用 Python SDK 调本地服务
7. [常用特性](/home/hiyoungman/CodeProject/PythonProject/learning-vllm-notebook/docs/vllm/07-common-features.md)
   - 进入高频能力而不是泛看全量特性
8. [故障排查](/home/hiyoungman/CodeProject/PythonProject/learning-vllm-notebook/docs/vllm/08-troubleshooting.md)
   - 直接按报错查修复方法
9. [curl 和 jq 速查](/home/hiyoungman/CodeProject/PythonProject/learning-vllm-notebook/docs/vllm/09-curl-and-jq.md)
   - 所有命令速查统一放这里
10. [参数实验记录](/home/hiyoungman/CodeProject/PythonProject/learning-vllm-notebook/docs/vllm/10-experiments.md)
   - 记录本机参数实验结果

## 推荐学习顺序

先看：

1. [本地部署](/home/hiyoungman/CodeProject/PythonProject/learning-vllm-notebook/docs/vllm/02-local-deployment.md)
2. [在线服务](/home/hiyoungman/CodeProject/PythonProject/learning-vllm-notebook/docs/vllm/04-online-serving.md)
3. [OpenAI-Compatible API](/home/hiyoungman/CodeProject/PythonProject/learning-vllm-notebook/docs/vllm/06-openai-compatible-api.md)

再看：

1. [核心参数](/home/hiyoungman/CodeProject/PythonProject/learning-vllm-notebook/docs/vllm/05-core-engine-args.md)
2. [故障排查](/home/hiyoungman/CodeProject/PythonProject/learning-vllm-notebook/docs/vllm/08-troubleshooting.md)

最后看：

1. [常用特性](/home/hiyoungman/CodeProject/PythonProject/learning-vllm-notebook/docs/vllm/07-common-features.md)
2. [参数实验记录](/home/hiyoungman/CodeProject/PythonProject/learning-vllm-notebook/docs/vllm/10-experiments.md)

## 仓库脚本

1. [download_qwen_model.py](/home/hiyoungman/CodeProject/PythonProject/learning-vllm-notebook/scripts/download_qwen_model.py)
   - 下载模型到 `models/`
2. [offline_infer.py](/home/hiyoungman/CodeProject/PythonProject/learning-vllm-notebook/scripts/offline_infer.py)
   - 运行离线推理
3. [openai_client_demo.py](/home/hiyoungman/CodeProject/PythonProject/learning-vllm-notebook/scripts/openai_client_demo.py)
   - 调用本地 OpenAI-compatible 服务
