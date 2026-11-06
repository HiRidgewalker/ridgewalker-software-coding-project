import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from scripts.feature_demo_common import (
    build_chat_messages,
    build_offline_llm,
    build_online_client,
    build_parser,
    build_structured_output_schema,
    default_sampling_params,
    print_json,
)


def run_offline(max_tokens: int) -> None:
    llm = build_offline_llm()
    schema = build_structured_output_schema()
    messages = build_chat_messages(
        system_prompt="You are a JSON-only assistant. Always answer with valid JSON.",
        user_prompt=(
            "请输出一个 JSON 对象，总结 vLLM 的作用，并列出 3 个最重要的部署调参项。"
        ),
    )
    sampling_params = default_sampling_params(
        max_tokens=max_tokens,
        temperature=0.0,
        structured_json_schema=schema,
    )
    outputs = llm.chat(
        messages,
        sampling_params,
        use_tqdm=False,
        chat_template_kwargs={"enable_thinking": False},
    )

    print_json("Structured Output Schema", schema)
    print("=== Offline Structured Output ===")
    print(outputs[0].outputs[0].text.strip())


def run_online(model: str, base_url: str, api_key: str, max_tokens: int) -> None:
    client = build_online_client(base_url=base_url, api_key=api_key)
    schema = build_structured_output_schema()
    messages = build_chat_messages(
        system_prompt="You are a JSON-only assistant. Always answer with valid JSON.",
        user_prompt=(
            "请输出一个 JSON 对象，总结 vLLM 的作用，并列出 3 个最重要的部署调参项。"
        ),
    )
    response = client.chat.completions.create(
        model=model,
        messages=messages,
        temperature=0.0,
        max_tokens=max_tokens,
        response_format={"type": "json_object"},
        extra_body={
            "chat_template_kwargs": {"enable_thinking": False},
            "structured_outputs": {"json": schema},
        },
    )

    print_json("Structured Output Schema", schema)
    print("=== Online Structured Output ===")
    print(response.choices[0].message.content or "")


def main() -> None:
    parser = build_parser("Structured outputs demo for both offline and online vLLM.")
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
