# 07. 持久化与人工介入

前置阅读：`05_langgraph_state_and_nodes.md`、`06_workflow_patterns.md`

## 1. 是什么

持久化让图在进程重启后还能恢复，人工介入让图在关键节点暂停，等人审批后继续执行；这是生产级 agent 系统与 demo 的分水岭。

## 2. 工程中何时用

- 需要人工审核高风险动作
- 任务执行时间长，可能跨进程、跨部署恢复
- 需要让客服、运营、审核人员插入到流程里

## 3. 核心 API / 用法（带注释的完整示例）

```python
from typing_extensions import TypedDict

from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph import END, START, StateGraph
from langgraph.types import Command, interrupt


class ApprovalState(TypedDict):
    draft: str
    approved: bool
    final_message: str


def require_approval(state: ApprovalState) -> dict[str, bool]:
    # interrupt 会暂停图执行，把控制权交给外部系统或人工界面
    approved = interrupt({"draft": state["draft"]})
    return {"approved": bool(approved)}


graph_builder = StateGraph(ApprovalState)
graph_builder.add_node("require_approval", require_approval)
graph_builder.add_node(
    "finalize_reply",
    lambda state: {"final_message": "已发送" if state["approved"] else "已拒绝"},
)
graph_builder.add_edge(START, "require_approval")
graph_builder.add_edge("require_approval", "finalize_reply")
graph_builder.add_edge("finalize_reply", END)

graph = graph_builder.compile(checkpointer=InMemorySaver())

config = {"configurable": {"thread_id": "approval-demo"}}
first = graph.invoke(
    {"draft": "请确认是否给用户补偿优惠券。", "approved": False, "final_message": ""},
    config=config,
)
print(first["__interrupt__"])
final = graph.invoke(Command(resume=True), config=config)
print(final)
```

补充说明：围绕 `resume` 的三个关键点

- 执行到 `require_approval` 节点时，代码会在下面这一行暂停：

```python
approved = interrupt({"draft": state["draft"]})
```

- 这时图不会继续往下执行，而是等待外部稍后通过 `Command(resume=...)` 恢复。
- 当外部执行：

```python
graph.invoke(Command(resume=True), config=config)
```

可以把恢复语义近似理解成：

```python
approved = True
```

然后当前节点从这一行下面继续执行，并返回状态更新。
- `resume=...` 后面的值类型，不是 LangGraph 根据上一个节点返回值自动推断的，而是由当前这个中断点自己的代码契约决定的。
- 换句话说，`interrupt(...)` 期望人类返回什么类型的数据，应该由你自己的节点逻辑来定义和校验。
- 当前这个教学示例里写的是：

```python
return {"approved": bool(approved)}
```

所以只要传入的是 truthy 值，例如 `"是"`、`"approve"`、`123`，都会被转成 `True`。
- 这说明示例代码是为了演示 `interrupt -> resume -> 继续执行` 这条主链路而故意写得比较宽松，不适合直接照搬到严格审批场景。
- 如果你的审批语义要求人工输入必须是布尔值，就应该显式限制：

```python
approved = interrupt({"draft": state["draft"]})
if not isinstance(approved, bool):
    raise TypeError("resume value must be bool")
return {"approved": approved}
```

- 工程上要记住一句话：`Command(resume=值)` 里的这个值，会作为 `interrupt(...)` 表达式的返回值传回当前节点；至于这个值应该是什么类型，不由框架自动决定，而由你自己的工作流契约决定。

## 4. 工程最佳实践

✅ 推荐：所有人工审批都显式建模为状态转换。  
✅ 推荐：高风险动作前一定中断，不要让模型直接执行。  
✅ 推荐：线程 ID、审批输入、恢复动作统一记录。  
❌ 避免：审批通过与否只写在日志里，不回写状态。  
❌ 避免：把 HITL 当作异常兜底，而不是流程设计的一部分。  

## 5. 与其他特性的关联

- `04_short_term_memory_and_context.md` 的线程概念在这里变成可恢复执行单元
- `08_streaming_observability_and_testing.md` 会讲如何调试和验证这类流程
