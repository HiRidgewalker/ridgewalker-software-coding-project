import asyncio
import sys
import uuid
from pathlib import Path
from typing import Any, AsyncIterator, Iterator

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from scripts.feature_demo_common import (
    build_offline_async_engine,
    build_online_client,
    build_parser,
    default_sampling_params,
)


def iter_online_text_chunks(stream: Any) -> Iterator[str]:
    for chunk in stream:
        delta = chunk.choices[0].delta.content or ""
        if delta:
            yield delta


async def iter_request_output_text_deltas(request_stream: Any) -> AsyncIterator[str]:
    async for request_output in request_stream:
        for output in request_output.outputs:
            text = output.text or ""
            if text:
                yield text


def build_offline_streaming_prompt() -> str:
    return (
        "你是一位专注于 vLLM 部署的简洁助手。\n\n"
        "请用三点说明 vLLM 本地部署时最重要的调参项。"
    )


async def stream_offline_text(max_tokens: int) -> AsyncIterator[str]:
    engine = build_offline_async_engine()
    sampling_params = default_sampling_params(
        max_tokens=max_tokens,
        temperature=0.7,
        output_kind="delta",
    )
    request_stream = engine.generate(
        build_offline_streaming_prompt(),
        sampling_params,
        request_id=f"streaming-demo-{uuid.uuid4()}",
    )
    try:
        async for chunk in iter_request_output_text_deltas(request_stream):
            yield chunk
    finally:
        engine.shutdown()


async def run_offline(max_tokens: int) -> None:
    print("=== Offline Streaming Demo ===")
    print("--- Stream ---")
    async for chunk in stream_offline_text(max_tokens):
        print(chunk, end="", flush=True)
    print()


def run_online(model: str, base_url: str, api_key: str, max_tokens: int) -> None:
    print("=== Online Streaming Demo ===")
    print("--- Stream ---")
    client = build_online_client(base_url=base_url, api_key=api_key)
    stream = client.chat.completions.create(
        model=model,
        messages=[
            {
                "role": "system",
                "content": "You are a concise assistant focused on vLLM deployment.",
            },
            {
                "role": "user",
                "content": "请用三点说明 vLLM 本地部署时最重要的调参项。",
            },
        ],
        temperature=0.7,
        max_tokens=max_tokens,
        stream=True,
        extra_body={"chat_template_kwargs": {"enable_thinking": False}},
    )

    for chunk in iter_online_text_chunks(stream):
        print(chunk, end="", flush=True)
    print()


def main() -> None:
    parser = build_parser("Streaming feature demo for both offline and online vLLM.")
    args = parser.parse_args()
    if args.mode == "offline":
        asyncio.run(run_offline(args.max_tokens))
        return
    run_online(
        model=args.model,
        base_url=args.base_url,
        api_key=args.api_key,
        max_tokens=args.max_tokens,
    )


if __name__ == "__main__":
    main()
