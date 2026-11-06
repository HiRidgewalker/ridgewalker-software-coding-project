# 离线推理

前置阅读：[02-local-deployment.md](/home/hiyoungman/CodeProject/PythonProject/learning-vllm-notebook/docs/vllm/02-local-deployment.md)

## 是什么

离线推理就是在 Python 脚本里直接创建 `LLM(...)` 对象，加载模型后立刻生成结果。它不启动 HTTP 服务，更适合本地验证、批量生成和最小功能检查。

## 工程中何时用

1. 你要先确认模型本身能不能加载
2. 你要排除“服务层问题”和“模型层问题”
3. 你要做批量 prompt 测试
4. 你要快速验证采样参数

## 核心 API / 用法

本仓库现成脚本是 [offline_infer.py](/home/hiyoungman/CodeProject/PythonProject/learning-vllm-notebook/scripts/offline_infer.py)。

```python
from pathlib import Path

from vllm import LLM, SamplingParams


PROJECT_ROOT = Path(__file__).resolve().parent.parent
LOCAL_MODEL_PATH = PROJECT_ROOT / "models" / "Qwen" / "Qwen3.5-2B"


def main() -> None:
    prompts = [
        "请用三句话说明 vLLM 的核心作用。",
        "请解释为什么本地部署时不建议一开始把上下文长度设为 262144。",
    ]

    # 直接从本地目录加载模型。
    llm = LLM(
        model=str(LOCAL_MODEL_PATH),
        max_model_len=4096,
        tensor_parallel_size=1,
        language_model_only=True,
        gpu_memory_utilization=0.80,
        enforce_eager=True,
    )

    # 控制生成行为，而不是控制模型加载。
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
```

运行命令：

```bash
python scripts/offline_infer.py
```

## 代码讲解

1. `LOCAL_MODEL_PATH` 固定指向本地模型目录
2. `LLM(...)` 负责加载模型
3. `max_model_len=4096` 先用保守上下文长度，避免当前 8GB 显存环境在离线推理时直接失败
4. `gpu_memory_utilization=0.80` 避免走默认 `0.9`，降低显存申请压力
5. `enforce_eager=True` 与当前在线服务基线保持一致，在 WSL2 下更稳
6. `SamplingParams(...)` 负责控制生成方式
7. `llm.generate(prompts, sampling_params)` 对一组输入批量生成
8. 输出对象里 `output.outputs[0].text` 才是最终文本

## 运行结果说明

成功时应看到两组输出，每组都包含：

1. `=== Prompt 1 ===` 或 `=== Prompt 2 ===`
2. 原始 prompt
3. 模型返回文本

如果这里成功、而在线服务失败，优先判断问题在服务层而不是模型层。

如果这里失败，并且报错里出现：

```text
Free memory on device cuda:0 ... is less than desired GPU memory utilization
```

说明问题是显存余量不够，而不是脚本逻辑错误。当前仓库已经把离线脚本默认改成保守参数基线；如果仍然失败，先检查是否有其他 GPU 进程占用显存。

## 工程最佳实践

✅ 推荐：先用离线推理确认模型能加载，再去排查服务问题  
✅ 推荐：把离线推理当成最小功能检查  
❌ 避免：在线服务一失败就怀疑模型文件损坏  
❌ 避免：离线推理和在线服务共用同一轮排障结论  

## 与其他特性的关联

1. 离线推理是在线服务之前的验证步骤
2. 调参时可以先用离线推理快速感受生成变化，再回到服务模式
