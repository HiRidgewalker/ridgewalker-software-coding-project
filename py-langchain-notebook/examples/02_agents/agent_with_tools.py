from __future__ import annotations

from langchain.agents import create_agent
from langchain.tools import tool

from learning_langchain.models import build_chat_model
from learning_langchain.utils.env import missing_env_message


@tool
def get_exchange_rate(base: str, target: str) -> str:
    """Return a fake exchange rate for deterministic local learning."""
    rates = {
        ("USD", "CNY"): 7.18,
        ("CNY", "USD"): 0.139,
    }
    rate = rates.get((base.upper(), target.upper()))
    if rate is None:
        return f"unsupported currency pair: {base}/{target}"
    return f"1 {base.upper()} = {rate} {target.upper()}"


def main() -> None:
    try:
        model = build_chat_model()
    except ValueError:
        print(missing_env_message())
        return

    agent = create_agent(
        model=model,
        tools=[get_exchange_rate],
        system_prompt=(
            "You are a pragmatic finance assistant. Use tools for deterministic data."
        ),
    )
    result = agent.invoke(
        {
            "messages": [
                {
                    "role": "user",
                    "content": "把 100 美元换算成人民币，并说明你是否用了工具。",
                }
            ]
        }
    )
    print(result)
    print(f"\n {'-' * 100} \n")
    print(result["messages"][-1].content)


if __name__ == "__main__":
    from dotenv import load_dotenv

    load_dotenv()
    main()
