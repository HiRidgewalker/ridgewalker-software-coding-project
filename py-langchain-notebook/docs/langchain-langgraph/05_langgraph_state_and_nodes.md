# 05. LangGraph 的 State、Node、Edge

前置阅读：`01_environment_and_models.md`

## 1. 是什么

LangGraph 是以状态为中心的工作流运行时。你先定义状态，再定义节点如何读写状态，最后用边把执行路径连起来。

## 2. 工程中何时用

- 一个 agent 已经变成明确的多步骤业务流程
- 需要代码而不是 prompt 决定流程走向
- 需要为后续审批、恢复、重试打基础

## 3. 核心 API / 用法（带注释的完整示例）

```python
from typing_extensions import TypedDict

from langgraph.graph import END, START, StateGraph


class OrderState(TypedDict):
    user_input: str
    intent: str
    result: str


def classify_intent(state: OrderState) -> dict[str, str]:
    if "退款" in state["user_input"]:
        return {"intent": "refund"}
    return {"intent": "fallback"}


def run_business_logic(state: OrderState) -> dict[str, str]:
    mapping = {"refund": "进入退款流程", "fallback": "转人工客服"}
    return {"result": mapping[state["intent"]]}


graph_builder = StateGraph(OrderState)
graph_builder.add_node("classify_intent", classify_intent)
graph_builder.add_node("run_business_logic", run_business_logic)
graph_builder.add_edge(START, "classify_intent")
graph_builder.add_edge("classify_intent", "run_business_logic")
graph_builder.add_edge("run_business_logic", END)

graph = graph_builder.compile()
print(graph.invoke({"user_input": "我要退款", "intent": "", "result": ""}))
```

补充说明：

- `START` 和 `END` 是图里的两个特殊标记，不承载你的业务逻辑。
- `START` 表示执行入口，`END` 表示执行终点；它们主要用来描述“这张图从哪里开始，到哪里结束”。
- `add_node("classify_intent", classify_intent)` 表示把一个真正会执行 Python 逻辑的节点注册到图里。
- `add_edge(START, "classify_intent")` 表示图启动后先进入 `classify_intent`。
- `add_edge("classify_intent", "run_business_logic")` 表示前一个节点执行完后，继续流转到下一个节点。
- `add_edge("run_business_logic", END)` 表示最后一个节点执行完后，图结束并返回最终状态。
- 可以把它们理解成：`START / END` 定义起止点，`add_node` 定义图里有哪些处理步骤，`add_edge` 定义这些步骤之间怎么连、怎么走。
- `compile()` 的作用是把“节点 + 边 + 状态结构”编译成一个真正可执行的 graph 对象；在 `compile()` 之前，你手里拿到的还是图的定义过程，不是执行器。
- `invoke(initial_state)` 的作用是执行这张图。你传入的是初始状态，LangGraph 会按边定义的路径依次运行节点，并把每个节点返回的状态增量合并起来，最后返回完整的最终状态。

## 4. 工程最佳实践

✅ 推荐：先定义状态，再写节点。  
✅ 推荐：节点只输出最小状态增量。  
✅ 推荐：把模型决策节点和业务副作用节点拆开。  
❌ 避免：一个节点同时做分类、查库、写库、发通知。  
❌ 避免：状态字段无限增长，最后没人敢改。  

## 5. 与其他特性的关联

- `06_workflow_patterns.md` 会在这个基础上加条件路由与更复杂的边
- `07_persistence_and_human_in_the_loop.md` 会把图接上持久化和中断
