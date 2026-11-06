from __future__ import annotations

from typing_extensions import TypedDict

from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph import END, START, StateGraph
from langgraph.types import Command, interrupt


# ApprovalState 定义整张图在执行过程中共享的状态结构。
# 这里本质上还是一个 dict，只是用 TypedDict 把字段约束写清楚。
class ApprovalState(TypedDict):
    # draft 表示当前待审批的回复草稿。
    draft: str
    # approved 表示人工审批结果。
    approved: bool
    # final_message 表示整个流程执行结束后输出的最终文案。
    final_message: str


def write_reply(state: ApprovalState) -> dict[str, str]:
    # 第一个节点：根据当前输入生成待审批草稿。
    # 这里为了教学简单，只是在原文前面加一个“客服草稿”前缀。
    #
    # 节点函数返回的是“状态增量”，而不是整个 state。
    # LangGraph 会把返回值合并回整份状态中。
    return {"draft": f"客服草稿：{state['draft']}"}


def require_approval(state: ApprovalState) -> dict[str, bool]:
    # 第二个节点：进入人工审批阶段。
    #
    # interrupt(...) 的作用是“中断图执行并等待外部输入”，不是普通函数调用。
    # 当执行到这里时，图会暂停，并把 {"draft": ...} 这份数据暴露给外部。
    # 外部系统或人工界面可以展示这份草稿，让人决定是否批准。
    approved = interrupt({"draft": state["draft"]})

    # 当稍后使用 Command(resume=...) 恢复执行时，
    # interrupt(...) 会接收到 resume 传回来的值。
    # 这里我们示例里传的是 True，所以 approved 最终会是 True。
    return {"approved": bool(approved)}


def finalize_reply(state: ApprovalState) -> dict[str, str]:
    # 第三个节点：读取审批结果，决定最终输出。
    # 这一步说明人工审批结果已经写回状态，后续节点可以像读取普通字段一样读取它。
    if state["approved"]:
        return {"final_message": f"已发送：{state['draft']}"}
    return {"final_message": "审批拒绝，等待人工修改。"}


def build_graph():
    # 声明一张围绕 ApprovalState 运行的状态图。
    graph_builder = StateGraph(ApprovalState)

    # 注册图中的三个业务节点。
    graph_builder.add_node("write_reply", write_reply)
    graph_builder.add_node("require_approval", require_approval)
    graph_builder.add_node("finalize_reply", finalize_reply)

    # 定义执行路径：
    # START -> write_reply -> require_approval -> finalize_reply -> END
    graph_builder.add_edge(START, "write_reply")
    graph_builder.add_edge("write_reply", "require_approval")
    graph_builder.add_edge("require_approval", "finalize_reply")
    graph_builder.add_edge("finalize_reply", END)

    # checkpointer 是 HITL 场景里的关键部件。
    # 图在 interrupt(...) 处暂停后，必须把当前执行状态保存下来，
    # 这样稍后才能基于同一个 thread_id 恢复执行。
    #
    # InMemorySaver() 只把状态放在内存里：
    # - 适合本地演示
    # - 进程重启后状态会丢失
    # - 生产环境通常要换成数据库或持久化存储
    return graph_builder.compile(checkpointer=InMemorySaver())


def main() -> None:
    # build_graph() 之后得到的是可执行 graph，而不再只是图定义。
    graph = build_graph()

    # thread_id 用来标识这一条流程实例。
    # 后续恢复时，LangGraph 会根据同一个 thread_id 找回上次中断的位置和状态。
    config = {"configurable": {"thread_id": "approval-demo"}}

    # 第一次 invoke：
    # 1. 传入初始状态
    # 2. 执行 write_reply 节点，生成客服草稿
    # 3. 进入 require_approval 节点
    # 4. 在 interrupt(...) 处暂停，等待人工输入
    interrupted = graph.invoke(
        {"draft": "请确认是否给用户补偿优惠券。", "approved": False, "final_message": ""},
        config=config,
    )

    # 这里打印出来的结果通常会包含 __interrupt__ 信息，
    # 表示流程当前不是“结束”，而是“中断等待人工处理”。
    print(interrupted)

    # 第二次 invoke：
    # Command(resume=True) 表示“恢复刚才中断的流程，并把 True 作为人工审批结果传回去”。
    #
    # 因为这里使用了相同的 thread_id，且前面配置了 checkpointer，
    # 所以图会从 require_approval 停下来的位置继续往后执行，
    # 而不是从头重新开始。
    resumed = graph.invoke(Command(resume=True), config=config)

    # 恢复后，流程会继续执行 finalize_reply，然后到 END 结束。
    print(resumed)


if __name__ == "__main__":
    # 加载 .env，让脚本在当前项目环境里读取配置更方便。
    # 虽然这个示例本身不依赖 API Key，但保留统一入口有助于示例风格一致。
    from dotenv import load_dotenv

    load_dotenv()
    main()
