import json
import sys
from pathlib import Path


sys.path.insert(0, str(Path(__file__).resolve().parent.parent))


from scripts.feature_demo_common import (
    build_chat_messages,
    build_offline_llm,
    build_online_client,
    build_parser,
    build_weather_tool,
    default_sampling_params,
    print_json,
)


def run_offline(max_tokens: int) -> None:
    llm = build_offline_llm()
    tool = build_weather_tool()
    messages = build_chat_messages(
        system_prompt=(
            "You can request tool calls when external information is needed. "
            "Use the provided weather tool if the user asks about weather."
        ),
        user_prompt="帮我查询上海今天的天气，并说明是否适合安排室外部署演练。",
    )
    sampling_params = default_sampling_params(max_tokens=max_tokens, temperature=0.0)
    outputs = llm.chat(
        messages,
        sampling_params,
        use_tqdm=False,
        tools=[tool],
        chat_template_kwargs={"enable_thinking": False},
    )

    print_json("Tool Definition", tool)
    print("=== Offline Tool Calling Raw Response ===")
    print(outputs[0].outputs[0].text.strip())
    print()
    print("离线高层 API 会返回模型生成的工具调用内容，是否真正执行工具由你的应用代码决定。")


def run_online(model: str, base_url: str, api_key: str, max_tokens: int) -> None:
    client = build_online_client(base_url=base_url, api_key=api_key)
    tool = build_weather_tool()
    messages = build_chat_messages(
        system_prompt=(
            "You can request tool calls when external information is needed. "
            "Use the provided weather tool if the user asks about weather."
        ),
        user_prompt="帮我查询上海今天的天气，并说明是否适合安排室外部署演练。",
    )
    response = client.chat.completions.create(
        model=model,
        messages=messages,
        temperature=0.0,
        max_tokens=max_tokens,
        tools=[tool],
        tool_choice="auto",
        extra_body={"chat_template_kwargs": {"enable_thinking": False}},
    )
    message = response.choices[0].message

    print_json("Tool Definition", tool)
    print("=== Online Tool Calling Response ===")
    if message.tool_calls:
        for tool_call in message.tool_calls:
            print(
                json.dumps(
                    {
                        "id": tool_call.id,
                        "name": tool_call.function.name,
                        "arguments": tool_call.function.arguments,
                    },
                    ensure_ascii=False,
                    indent=2,
                )
            )
    else:
        print(message.content or "")


def main() -> None:
    parser = build_parser("Tool calling demo for both offline and online vLLM.")
    args = parser.parse_args()
    if args.mode == "offline":
        run_offline(args.max_tokens)
        return
    run_online(
        model=args.model,
        base_url=args.base_url,
        api_key=args.api_key,
        max_tokens=args.max_tokens,
    )


if __name__ == "__main__":
    main()
