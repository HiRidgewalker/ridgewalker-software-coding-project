from __future__ import annotations

from typing_extensions import TypedDict

from langgraph.graph import END, START, StateGraph


# TypedDict 用来声明整个图运行过程中的共享状态结构。
# LangGraph 的核心思想是：节点读取状态，再返回“状态增量”去更新状态。
class OrderState(TypedDict):
    # 用户输入的原始文本，例如“我要申请退款”
    user_input: str
    # 对用户意图的归一化结果，由 classify_intent 节点写入
    intent: str
    # 最终给出的处理结果，由 run_business_logic 节点写入
    result: str


def classify_intent(state: OrderState) -> dict[str, str]:
    # 第一个节点：负责从原始输入中提取一个简单意图。
    # 这里故意不用模型，而是用确定性规则，便于理解 LangGraph 最基础的工作方式。
    text = state["user_input"].lower()

    # 节点函数不需要返回整个 state，只需要返回它想更新的字段。
    # LangGraph 会把这里的返回值合并进当前状态。
    if "退款" in text:
        return {"intent": "refund"}
    if "查询" in text:
        return {"intent": "query_order"}

    # 如果没有匹配到已知关键词，就走兜底意图。
    return {"intent": "fallback"}


def run_business_logic(state: OrderState) -> dict[str, str]:
    # 第二个节点：根据上一个节点已经写入 state 的 intent，
    # 决定当前请求应该进入哪条业务处理路径。
    mapping = {
        "refund": "进入退款流程",
        "query_order": "进入订单查询流程",
        "fallback": "转人工客服",
    }

    # 这里读取的是 classify_intent 节点已经产出的 state["intent"]。
    return {"result": mapping[state["intent"]]}


def build_graph():
    # StateGraph(OrderState) 表示：
    # 这张图里的所有节点都围绕 OrderState 这份状态来工作。
    graph_builder = StateGraph(OrderState)

    # add_node(节点名, 节点函数)
    # 节点名是图里的标识，节点函数是真正执行逻辑的 Python 函数。
    graph_builder.add_node("classify_intent", classify_intent)
    graph_builder.add_node("run_business_logic", run_business_logic)

    # START 是图的统一起点。
    # 这条边表示：图一开始先执行 classify_intent。
    graph_builder.add_edge(START, "classify_intent")

    # 这条边表示：classify_intent 完成后，继续执行 run_business_logic。
    graph_builder.add_edge("classify_intent", "run_business_logic")

    # END 是图的统一终点。
    # run_business_logic 执行完后，图结束并返回最终状态。
    graph_builder.add_edge("run_business_logic", END)

    # compile() 会把“节点 + 边”的定义编译成一个真正可执行的 graph 对象。
    return graph_builder.compile()


def main() -> None:
    # 先构建图。
    graph = build_graph()

    # invoke() 传入的是这张图的初始状态。
    # 这里必须把 OrderState 需要的字段都提供出来。
    # 即使 intent 和 result 还没算出来，也先给一个初始空值。
    result = graph.invoke({"user_input": "我要申请退款", "intent": "", "result": ""})

    # 最终返回的是整份状态，而不只是某一个节点的输出。
    # 所以这里会看到 user_input、intent、result 三个字段都在结果里。
    print(result)


if __name__ == "__main__":
    # 作为脚本直接运行时，执行这张最小示例图。
    main()
