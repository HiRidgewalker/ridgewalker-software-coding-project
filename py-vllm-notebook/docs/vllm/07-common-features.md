# 常用特性

前置阅读：[06-openai-compatible-api.md](/home/hiyoungman/CodeProject/PythonProject/learning-vllm-notebook/docs/vllm/06-openai-compatible-api.md)

## 是什么

这篇文档只保留工程里最值得先掌握的 4 类能力，而不是把所有 vLLM 特性平均铺开。

## 工程中何时用

优先学习顺序：

1. Streaming
   先学它，因为这是最容易直接看到用户体验收益的能力。你一旦在聊天界面、命令行或 Web 服务里接入流式返回，就能立刻理解“首 token 延迟”和“整体完成时间”不是一回事。
2. Structured Outputs
   第二个学它，因为一旦模型输出要进入程序而不是只给人看，结构化输出就比自由文本更重要。学到这里，你应该能稳定拿到可解析 JSON，而不是靠字符串截取做脆弱处理。
3. Tool Calling
   第三个学它，因为它建立在前两步之上。你先要理解聊天接口怎么返回内容、程序怎么消费结果，之后再看模型如何提出工具调用请求，整体链路才不会乱。
4. Prefix Caching
   最后学它，因为它主要是性能优化，而不是功能入口。只有当你已经有稳定的长前缀、多轮对话或长文档问答场景时，这个特性才会真正带来吞吐和延迟收益。

对应的学习目标：

1. 学完 Streaming：你应能判断哪些请求适合实时返回，哪些批处理不该强行流式化
2. 学完 Structured Outputs：你应能把模型输出稳定交给数据库、接口或下游程序
3. 学完 Tool Calling：你应能区分“模型请求调用工具”和“服务端真正执行工具”这两个职责
4. 学完 Prefix Caching：你应能识别哪些请求真的共享前缀，哪些场景其实不会从缓存里获益

## 核心 API / 用法

### 1. Streaming

何时用：

1. 聊天界面
2. 终端实时输出
3. 用户希望尽快看到首 token

工程最佳实践：

✅ 推荐：做交互式应用时默认优先考虑  
❌ 避免：批处理任务里强行用流式返回

### 2. Structured Outputs

何时用：

1. 模型输出要给程序消费
2. 要写数据库、表单、下游接口
3. 要求稳定 JSON 结构

工程最佳实践：

✅ 推荐：接口化输出优先结构化  
❌ 避免：让下游程序去解析自由文本

### 3. Tool Calling

何时用：

1. 模型要调用搜索、天气、数据库、计算器等外部能力
2. 你在做 Agent 或工具增强应用

工程最佳实践：

✅ 推荐：把 Tool Calling 理解成“模型提出工具调用请求”  
❌ 避免：把 Tool Calling 理解成“模型自动执行一切”

### 4. Prefix Caching

何时用：

1. 多个请求共享长前缀
2. 长系统提示词
3. 多轮会话
4. 长文档反复提问

工程最佳实践：

✅ 推荐：长上下文重复前缀场景优先关注  
❌ 避免：短单轮请求里过度关注这项优化

## 代码讲解

当前仓库还没有把这些特性分别做成独立脚本，原因很简单：

1. 这个仓库当前第一目标是稳定部署
2. 先跑通基线比先堆高级能力更重要

你应该先形成下面这组工程判断：

1. 需要实时返回时用 Streaming
2. 需要程序消费时用 Structured Outputs
3. 需要外部能力时用 Tool Calling
4. 需要减少重复前缀计算时看 Prefix Caching

## 运行结果说明

这篇文档当前不对应固定脚本，而是给你建立“何时该引入哪类能力”的判断规则。等基线部署稳定后，再为这些能力补专门示例最有价值。

## 工程最佳实践

✅ 推荐：先部署成功，再学高级特性  
✅ 推荐：按业务场景选择特性，不要按“文档出现顺序”学  
❌ 避免：在最小部署还不稳定时就优先折腾高级能力  

## 与其他特性的关联

1. 这些能力都建立在 [06-openai-compatible-api.md](/home/hiyoungman/CodeProject/PythonProject/learning-vllm-notebook/docs/vllm/06-openai-compatible-api.md) 之上
2. 如果服务本身都没稳定，先回到 [08-troubleshooting.md](/home/hiyoungman/CodeProject/PythonProject/learning-vllm-notebook/docs/vllm/08-troubleshooting.md)
