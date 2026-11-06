# LangChain 与 LangGraph 工程化学习索引

LangChain 用来快速拼装模型、工具和 agent 应用，LangGraph 用来把 agent 升级成可持久化、可中断、可恢复的状态工作流。

## 与同类技术的核心差异

| 技术 | 定位 | 最适合做什么 | 不适合做什么 | 直接结论 |
| --- | --- | --- | --- | --- |
| LangChain | LLM 应用框架 | 快速搭建带工具、结构化输出、短期记忆的 AI 服务 | 复杂流程控制和恢复机制 | 先做可用 agent，优先用它 |
| LangGraph | 状态工作流与运行时 | 持久化、审批、分支、循环、长任务恢复 | 单轮问答或轻量聊天机器人 | 追求可靠 agent 系统时必须上 |
| OpenAI SDK | 模型调用 SDK | 最轻量地直接调用模型 | 想要现成的 agent、memory、workflow 抽象 | 只调模型时够用，做系统太薄 |
| LlamaIndex | 检索与知识库框架 | 文档摄取、索引、RAG 查询 | 通用 agent 编排 | 做知识库很强，不是主流程编排首选 |
| CrewAI / AutoGen | 多角色协作抽象 | 快速拼多 agent demo | 强约束状态管理和恢复 | 演示快，生产可控性不如 LangGraph |

## 适用场景 vs 不适用场景

### 适用场景

- 需要接入 OpenAI 或 OpenAI-compatible 模型并快速上线
- 需要 tool calling、结构化输出、线程级上下文
- 需要审批、恢复执行、长会话、多分支工作流
- 需要把“聊天”升级成“受控业务流程”

### 不适用场景

- 只有一次性 prompt 调用，没有工具和流程需求
- 纯检索系统，不需要 agent 编排
- 业务流程都还没定型，只想验证一个最小想法

## 子文档索引

- [01_environment_and_models.md](./01_environment_and_models.md)
  环境准备、依赖、模型接入和 OpenAI-compatible 配置。
- [02_langchain_agents.md](./02_langchain_agents.md)
  `create_agent` 的主线能力、何时该停留在 LangChain。
- [03_tools_and_structured_output.md](./03_tools_and_structured_output.md)
  工具定义、结构化输出和生产里最常见的输入输出约束。
- [04_short_term_memory_and_context.md](./04_short_term_memory_and_context.md)
  线程级记忆、上下文管理、避免消息无限膨胀。
- [05_langgraph_state_and_nodes.md](./05_langgraph_state_and_nodes.md)
  State、Node、Edge、Compile 的核心抽象。
- [06_workflow_patterns.md](./06_workflow_patterns.md)
  条件路由、并行、循环、Agent + Workflow 混合模式。
- [07_persistence_and_human_in_the_loop.md](./07_persistence_and_human_in_the_loop.md)
  持久化、线程、人工审批、中断恢复。
- [08_streaming_observability_and_testing.md](./08_streaming_observability_and_testing.md)
  流式输出、调试、观测、测试和学习型项目的验证方法。

## 学习路径建议

1. 先看 `01_environment_and_models.md`
2. 再看 `02_langchain_agents.md`
3. 然后看 `03_tools_and_structured_output.md`
4. 接着看 `04_short_term_memory_and_context.md`
5. 完成 LangChain 主线后，进入 `05_langgraph_state_and_nodes.md`
6. 再看 `06_workflow_patterns.md`
7. 最后看 `07_persistence_and_human_in_the_loop.md` 与 `08_streaming_observability_and_testing.md`

如果你的目标是先做一个能工作的 agent 服务，读到 `04` 就可以开始写业务。
如果你的目标是做可靠的生产级 agent 系统，`05` 到 `08` 必须一起掌握。
