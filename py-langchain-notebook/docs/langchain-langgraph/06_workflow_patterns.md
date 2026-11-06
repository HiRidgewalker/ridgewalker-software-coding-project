# 06. 工作流模式

前置阅读：`05_langgraph_state_and_nodes.md`

## 1. 是什么

工作流模式是把 LangGraph 的基础图能力组织成常见工程套路，例如条件路由、并行分支、循环重试，以及 agent 与 workflow 混合。

## 2. 工程中何时用

- 需要按意图把请求分流到不同处理链路
- 需要对同一输入做多个独立检查
- 需要失败重试或多轮迭代完善结果

## 3. 核心 API / 用法（带注释的完整示例）

```python
from typing_extensions import Literal, TypedDict

from langgraph.graph import END, START, StateGraph


class ReviewState(TypedDict):
    message: str
    route: Literal["auto_reply", "escalate"]
    output: str


def route_message(state: ReviewState) -> dict[str, str]:
    if "投诉" in state["message"] or "退款" in state["message"]:
        return {"route": "escalate"}
    return {"route": "auto_reply"}


def choose_next(state: ReviewState) -> str:
    return state["route"]


graph_builder = StateGraph(ReviewState)
graph_builder.add_node("route_message", route_message)
graph_builder.add_node("auto_reply", lambda _: {"output": "自动回复"})
graph_builder.add_node("escalate", lambda _: {"output": "人工升级"})
graph_builder.add_edge(START, "route_message")
graph_builder.add_conditional_edges(
    "route_message",
    choose_next,
    {"auto_reply": "auto_reply", "escalate": "escalate"},
)
graph_builder.add_edge("auto_reply", END)
graph_builder.add_edge("escalate", END)
```

## 4. 工程最佳实践

✅ 推荐：路由条件尽量稳定、可解释、可测试。  
✅ 推荐：把路由判断结果写进状态，方便调试和追踪。  
✅ 推荐：先用代码路由，再决定是否把某一步交给模型。  
❌ 避免：把复杂分支只藏在 prompt 里，导致行为不可预测。  
❌ 避免：为了“智能”把简单流程搞成黑盒 agent。  

## 5. 与其他特性的关联

- 可以和 `02_langchain_agents.md` 结合，在某个节点内部调用 agent
- 与 `07_persistence_and_human_in_the_loop.md` 联用时最适合做审批流
