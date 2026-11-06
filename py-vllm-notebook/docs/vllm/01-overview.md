# vLLM 总览

## 是什么

vLLM 是一个面向大语言模型推理和服务部署的框架，重点解决两个问题：

1. 把模型高效跑起来
2. 以稳定的 HTTP API 方式对外提供服务

对这个仓库来说，vLLM 的价值不是“研究推理底层”，而是尽快把本地模型部署成一个可验证、可调用、可调参的服务。

## 工程中何时用

下面这些场景，vLLM 是直接可用的方案：

1. 你要把 Hugging Face 上的模型部署成本地 HTTP 服务
2. 你要兼容 OpenAI 风格的客户端调用方式
3. 你要验证模型在单机单卡上的可运行性
4. 你要做推理参数调优，例如上下文长度和显存利用率
5. 你要给上层应用提供统一模型网关

下面这些场景，不是这个仓库的当前重点：

1. 多机分布式集群调度
2. 深度内核优化
3. 自训练或微调流程

## 本仓库的目标

本项目只聚焦一条主线：

1. 使用 Hugging Face 模型 `Qwen/Qwen3.5-2B`
2. 将模型下载到本地 `models/Qwen/Qwen3.5-2B`
3. 用 vLLM 跑通离线推理
4. 用 `vllm serve` 跑通在线服务
5. 用 OpenAI-compatible API 调用本地服务
6. 能排查常见环境和启动问题

## 文档依赖关系

按下面顺序阅读，不要跳：

1. [02-local-deployment.md](/home/hiyoungman/CodeProject/PythonProject/learning-vllm-notebook/docs/vllm/02-local-deployment.md)
   - 先把服务跑起来
2. [03-offline-inference.md](/home/hiyoungman/CodeProject/PythonProject/learning-vllm-notebook/docs/vllm/03-offline-inference.md)
   - 再理解离线推理怎么工作
3. [04-online-serving.md](/home/hiyoungman/CodeProject/PythonProject/learning-vllm-notebook/docs/vllm/04-online-serving.md)
   - 再理解在线服务怎么验证
4. [05-core-engine-args.md](/home/hiyoungman/CodeProject/PythonProject/learning-vllm-notebook/docs/vllm/05-core-engine-args.md)
   - 再掌握最常改的参数
5. [06-openai-compatible-api.md](/home/hiyoungman/CodeProject/PythonProject/learning-vllm-notebook/docs/vllm/06-openai-compatible-api.md)
   - 再用 Python SDK 调本地服务
6. [07-common-features.md](/home/hiyoungman/CodeProject/PythonProject/learning-vllm-notebook/docs/vllm/07-common-features.md)
   - 最后进入高频能力

需要查命令时，直接看：

1. [09-curl-and-jq.md](/home/hiyoungman/CodeProject/PythonProject/learning-vllm-notebook/docs/vllm/09-curl-and-jq.md)
2. [08-troubleshooting.md](/home/hiyoungman/CodeProject/PythonProject/learning-vllm-notebook/docs/vllm/08-troubleshooting.md)

## 工程最佳实践

✅ 推荐：先跑通最保守配置，再逐步放大 `max_model_len` 和显存利用率  
✅ 推荐：优先把模型下载到本地目录，再通过目录方式启动  
✅ 推荐：把“服务是否活着”和“模型是否能生成”拆成两个独立验证步骤  
❌ 避免：一开始就按模型卡最大上下文上线  
❌ 避免：一启动失败就同时改多个参数  

## 与其他模块的关联

1. 本文档是入口，后续所有文档都默认你已经知道本仓库的模型路径和目标主线
2. `02-local-deployment.md` 是后续所有文档的前置阅读
