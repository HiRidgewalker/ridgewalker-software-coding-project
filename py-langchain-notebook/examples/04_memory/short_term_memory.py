from __future__ import annotations

from langchain.agents import create_agent
from langgraph.checkpoint.memory import InMemorySaver

from learning_langchain.models import build_chat_model
from learning_langchain.utils.env import missing_env_message


def main() -> None:
    try:
        model = build_chat_model()
    except ValueError:
        print(missing_env_message())
        return

    agent = create_agent(
        model=model,
        tools=[],
        checkpointer=InMemorySaver(),
        system_prompt="你是一个会记住线程上下文的助手。",
    )

    config = {"configurable": {"thread_id": "demo-thread"}}
    agent.invoke(
        {"messages": [{"role": "user", "content": "我叫小李。"}]},
        config=config,
    )
    result = agent.invoke(
        {"messages": [{"role": "user", "content": "我刚才告诉过你我叫什么吗？"}]},
        config=config,
    )
    print(result["messages"][-1].content)


if __name__ == "__main__":
    from dotenv import load_dotenv
    load_dotenv()
    main()
