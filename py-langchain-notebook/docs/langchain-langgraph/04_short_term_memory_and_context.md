# 04. 短期记忆与上下文管理

前置阅读：`02_langchain_agents.md`

## 1. 是什么

短期记忆解决“同一个线程里多轮对话怎么保留上下文”的问题，上下文管理解决“消息越来越长后怎么控制成本和噪声”的问题。

## 2. 工程中何时用

- 客服、Copilot、内部助手需要记住当前会话
- 同一线程要跨多轮继续执行同一任务
- 对话轮次一多，token 成本和噪声开始失控

## 3. 核心 API / 用法（带注释的完整示例）

```python
from langchain.agents import create_agent
from langgraph.checkpoint.memory import InMemorySaver

from learning_langchain.models import build_chat_model


agent = create_agent(
    model=build_chat_model(),
    tools=[],
    # checkpointer 让同一 thread_id 下的状态可复用
    checkpointer=InMemorySaver(),
    system_prompt="你是一个会记住当前线程上下文的助手。",
)

config = {"configurable": {"thread_id": "demo-thread"}}

agent.invoke({"messages": [{"role": "user", "content": "我叫小李。"}]}, config=config)
result = agent.invoke(
    {"messages": [{"role": "user", "content": "我刚才告诉过你我叫什么吗？"}]},
    config=config,
)
print(result["messages"][-1].content)
```

## 4. 工程最佳实践

✅ 推荐：所有会话都显式传 `thread_id`。  
✅ 推荐：把“短期记忆”理解为线程状态，而不是长期知识库。  
✅ 推荐：在进入长流程前就设计好消息裁剪策略。  
❌ 避免：把所有历史消息无限追加。  
❌ 避免：把用户画像、业务主数据直接塞进消息历史里。  

## 5. 与其他特性的关联

- `07_persistence_and_human_in_the_loop.md` 会把内存 checkpointer 升级成持久化方案
- `08_streaming_observability_and_testing.md` 会讲如何观察线程状态变化
