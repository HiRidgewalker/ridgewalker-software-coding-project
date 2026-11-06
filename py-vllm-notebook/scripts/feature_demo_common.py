import argparse
import json
import time
from pathlib import Path
from typing import Any

from openai import OpenAI


PROJECT_ROOT = Path(__file__).resolve().parent.parent
LOCAL_MODEL_PATH = PROJECT_ROOT / "models" / "Qwen" / "Qwen3.5-2B"
DEFAULT_MODEL_ID = "models/Qwen/Qwen3.5-2B"
DEFAULT_ONLINE_BASE_URL = "http://localhost:8000/v1"
DEFAULT_API_KEY = "EMPTY"


def build_parser(description: str) -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument(
        "--mode",
        choices=("offline", "online"),
        default="offline",
        help="offline 使用本地 vLLM Python API，online 使用 OpenAI-compatible HTTP API。",
    )
    parser.add_argument(
        "--model",
        default=DEFAULT_MODEL_ID,
        help="online 模式使用的模型 id，默认与本仓库文档保持一致。",
    )
    parser.add_argument(
        "--base-url",
        default=DEFAULT_ONLINE_BASE_URL,
        help="online 模式的 OpenAI-compatible 服务地址。",
    )
    parser.add_argument(
        "--api-key",
        default=DEFAULT_API_KEY,
        help="online 模式的 API key，本地 vLLM 一般用 EMPTY 即可。",
    )
    parser.add_argument(
        "--max-tokens",
        type=int,
        default=256,
        help="生成的最大 token 数。",
    )
    return parser


def build_offline_llm(*, enable_prefix_caching: bool = False) -> Any:
    from vllm import LLM

    return LLM(
        model=str(LOCAL_MODEL_PATH),
        max_model_len=4096,
        tensor_parallel_size=1,
        language_model_only=True,
        gpu_memory_utilization=0.80,
        enforce_eager=True,
        enable_prefix_caching=enable_prefix_caching,
    )


def build_online_client(base_url: str, api_key: str) -> OpenAI:
    return OpenAI(base_url=base_url, api_key=api_key)


def build_offline_async_engine(*, enable_prefix_caching: bool = False) -> Any:
    from vllm.engine.arg_utils import AsyncEngineArgs
    from vllm.engine.async_llm_engine import AsyncLLMEngine

    engine_args = AsyncEngineArgs(
        model=str(LOCAL_MODEL_PATH),
        max_model_len=4096,
        tensor_parallel_size=1,
        language_model_only=True,
        gpu_memory_utilization=0.80,
        enforce_eager=True,
        enable_prefix_caching=enable_prefix_caching,
        disable_log_stats=True,
    )
    return AsyncLLMEngine.from_engine_args(engine_args)


def build_chat_messages(
    *,
    system_prompt: str,
    user_prompt: str,
    shared_prefix: str | None = None,
) -> list[dict[str, str]]:
    user_content = user_prompt
    if shared_prefix:
        user_content = f"{shared_prefix}\n\n{user_prompt}"
    return [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_content},
    ]


def build_structured_output_schema() -> dict[str, Any]:
    return {
        "type": "object",
        "properties": {
            "summary": {
                "type": "string",
                "description": "用一句话总结 vLLM 的作用。",
            },
            "key_parameters": {
                "type": "array",
                "items": {"type": "string"},
                "description": "列出最重要的 3 个部署调参项。",
                "minItems": 3,
                "maxItems": 3,
            },
        },
        "required": ["summary", "key_parameters"],
        "additionalProperties": False,
    }


def build_weather_tool() -> dict[str, Any]:
    return {
        "type": "function",
        "function": {
            "name": "get_weather",
            "description": "查询某个城市当前的天气概况。",
            "parameters": {
                "type": "object",
                "properties": {
                    "city": {
                        "type": "string",
                        "description": "要查询天气的城市名称。",
                    },
                    "unit": {
                        "type": "string",
                        "enum": ["celsius", "fahrenheit"],
                        "description": "温度单位。",
                    },
                },
                "required": ["city"],
                "additionalProperties": False,
            },
        },
    }


def build_prefix_caching_prompts() -> tuple[str, str]:
    shared_prefix = (
        "vLLM 本地部署说明：\n"
        "1. 模型路径固定为 models/Qwen/Qwen3.5-2B。\n"
        "2. 单卡学习环境优先使用 tensor_parallel_size=1。\n"
        "3. 初次部署时 max_model_len 建议从 4096 起步。\n"
        "4. gpu_memory_utilization 可以先从 0.80 开始。\n"
        "5. OpenAI-compatible 服务默认监听 http://localhost:8000/v1。\n"
        "6. 排障顺序是先 health，再 models，再 chat。\n"
        "7. 如果你在做长提示词、多轮会话或长文档问答，前缀缓存才更有价值。\n"
    )
    first_prompt = (
        f"{shared_prefix}\n"
        "问题1：请基于上面的部署说明，总结最重要的两条上线前检查项。"
    )
    second_prompt = (
        f"{shared_prefix}\n"
        "问题2：请基于上面的部署说明，解释为什么新手不该一开始就把上下文长度设得很大。"
    )
    return first_prompt, second_prompt


def build_prefix_caching_messages() -> tuple[list[dict[str, str]], list[dict[str, str]]]:
    first_prompt, second_prompt = build_prefix_caching_prompts()
    system_prompt = "You are a concise assistant focused on vLLM deployment."
    return (
        build_chat_messages(system_prompt=system_prompt, user_prompt=first_prompt),
        build_chat_messages(system_prompt=system_prompt, user_prompt=second_prompt),
    )


def default_sampling_params(
    *,
    max_tokens: int,
    temperature: float = 0.7,
    structured_json_schema: dict[str, Any] | None = None,
    output_kind: str | None = None,
) -> Any:
    from vllm import SamplingParams
    from vllm.sampling_params import RequestOutputKind, StructuredOutputsParams

    kwargs: dict[str, Any] = {
        "temperature": temperature,
        "top_p": 0.8,
        "max_tokens": max_tokens,
    }
    if structured_json_schema is not None:
        kwargs["structured_outputs"] = StructuredOutputsParams(
            json=structured_json_schema
        )
    if output_kind == "delta":
        kwargs["output_kind"] = RequestOutputKind.DELTA
    return SamplingParams(**kwargs)


def print_json(title: str, payload: Any) -> None:
    print(f"=== {title} ===")
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    print()

def timed_call(fn: Any) -> tuple[Any, float]:
    start = time.perf_counter()
    result = fn()
    duration = time.perf_counter() - start
    return result, duration
