import sys
from pathlib import Path


sys.path.insert(0, str(Path(__file__).resolve().parent.parent))


from scripts.feature_demo_common import (
    build_offline_llm,
    build_online_client,
    build_parser,
    build_prefix_caching_messages,
    build_prefix_caching_prompts,
    default_sampling_params,
    timed_call,
)


def run_offline(max_tokens: int) -> None:
    llm = build_offline_llm(enable_prefix_caching=True)
    first_prompt, second_prompt = build_prefix_caching_prompts()
    sampling_params = default_sampling_params(max_tokens=max_tokens, temperature=0.2)

    first_result, first_duration = timed_call(
        lambda: llm.generate(first_prompt, sampling_params, use_tqdm=False)
    )
    second_result, second_duration = timed_call(
        lambda: llm.generate(second_prompt, sampling_params, use_tqdm=False)
    )

    first_output = first_result[0]
    second_output = second_result[0]
    print("=== Offline Prefix Caching Demo ===")
    print(f"first_duration_seconds={first_duration:.2f}")
    print(f"first_cached_tokens={first_output.num_cached_tokens}")
    print(f"second_duration_seconds={second_duration:.2f}")
    print(f"second_cached_tokens={second_output.num_cached_tokens}")
    print("--- Second Response ---")
    print(second_output.outputs[0].text.strip())


def run_online(model: str, base_url: str, api_key: str, max_tokens: int) -> None:
    client = build_online_client(base_url=base_url, api_key=api_key)
    first_messages, second_messages = build_prefix_caching_messages()

    first_response, first_duration = timed_call(
        lambda: client.chat.completions.create(
            model=model,
            messages=first_messages,
            temperature=0.2,
            max_tokens=max_tokens,
            extra_body={"chat_template_kwargs": {"enable_thinking": False}},
        )
    )
    second_response, second_duration = timed_call(
        lambda: client.chat.completions.create(
            model=model,
            messages=second_messages,
            temperature=0.2,
            max_tokens=max_tokens,
            extra_body={"chat_template_kwargs": {"enable_thinking": False}},
        )
    )

    print("=== Online Prefix Caching Demo ===")
    print(f"first_duration_seconds={first_duration:.2f}")
    print(f"second_duration_seconds={second_duration:.2f}")
    print("在线 OpenAI-compatible 接口通常不直接返回 cached token 数，可先对比相同长前缀下两次请求耗时。")
    print("--- Second Response ---")
    print(second_response.choices[0].message.content or "")


def main() -> None:
    parser = build_parser("Prefix caching demo for both offline and online vLLM.")
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
