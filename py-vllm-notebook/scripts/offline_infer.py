from pathlib import Path

from vllm import LLM, SamplingParams


PROJECT_ROOT = Path(__file__).resolve().parent.parent
LOCAL_MODEL_PATH = PROJECT_ROOT / "models" / "Qwen" / "Qwen3.5-2B"


def main() -> None:
    prompts = [
        "请用三句话说明 vLLM 的核心作用。",
        "请解释为什么本地部署时不建议一开始把上下文长度设为 262144。",
    ]

    # 对 Qwen/Qwen3.5-2B，纯文本学习场景建议启用 language_model_only，
    # 并从较保守的上下文长度开始，降低首次实验的显存压力。
    llm = LLM(
        model=str(LOCAL_MODEL_PATH),
        max_model_len=4096,
        tensor_parallel_size=1,
        language_model_only=True,
        gpu_memory_utilization=0.80,
        enforce_eager=True,
    )

    sampling_params = SamplingParams(
        temperature=0.7,
        top_p=0.8,
        max_tokens=256,
    )

    outputs = llm.generate(prompts, sampling_params)
    for idx, output in enumerate(outputs, start=1):
        print(f"=== Prompt {idx} ===")
        print(output.prompt)
        print("--- Output ---")
        print(output.outputs[0].text.strip())
        print()


if __name__ == "__main__":
    main()
