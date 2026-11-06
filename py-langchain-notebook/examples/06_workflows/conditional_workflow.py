from __future__ import annotations

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


def auto_reply(_: ReviewState) -> dict[str, str]:
    return {"output": "自动回复：已收到，我们会尽快处理。"}


def escalate(_: ReviewState) -> dict[str, str]:
    return {"output": "进入人工升级流程。"}


def choose_next(state: ReviewState) -> str:
    return state["route"]


def build_graph():
    graph_builder = StateGraph(ReviewState)
    graph_builder.add_node("route_message", route_message)
    graph_builder.add_node("auto_reply", auto_reply)
    graph_builder.add_node("escalate", escalate)
    graph_builder.add_edge(START, "route_message")
    graph_builder.add_conditional_edges(
        "route_message",
        choose_next,
        {
            "auto_reply": "auto_reply",
            "escalate": "escalate",
        },
    )
    graph_builder.add_edge("auto_reply", END)
    graph_builder.add_edge("escalate", END)
    return graph_builder.compile()


def main() -> None:
    graph = build_graph()
    result = graph.invoke(
        {"message": "我要投诉你们的退款速度", "route": "escalate", "output": ""}
    )
    print(result)


if __name__ == "__main__":
    from  dotenv import load_dotenv
    load_dotenv()
    main()
