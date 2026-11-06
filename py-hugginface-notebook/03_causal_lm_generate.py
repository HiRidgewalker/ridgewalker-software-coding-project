"""
这个文件演示如何加载因果语言模型并进行基础生成。

学习重点：
1. AutoTokenizer 与 AutoModelForCausalLM 的基本配合
2. generate 的核心调用方式
3. temperature、top_p、max_new_tokens 等参数会如何影响输出
"""

import torch
from transformers import AutoModelForCausalLM, AutoTokenizer


def main() -> None:
    # 为了示例简洁，这里使用一个体积较小的生成模型。
    # 在真实项目里，你可以替换为 Qwen、Llama 等更适合指令跟随的模型。
    model_name = "gpt2"

    # 加载分词器。
    tokenizer = AutoTokenizer.from_pretrained(model_name)

    # GPT2 默认没有 pad_token，因此这里通常把 eos_token 作为 pad_token 使用，
    # 这样可以减少批处理时因缺失 pad_token 导致的报错。
    tokenizer.pad_token = tokenizer.eos_token

    # 加载因果语言模型。
    # torch_dtype=torch.float32 这里写得保守一些，保证 CPU 环境更容易理解。
    # 如果在 GPU 环境中，可以按显存情况改成 float16 或 bfloat16。
    model = AutoModelForCausalLM.from_pretrained(
        model_name,
        torch_dtype=torch.float32,
    )

    # 设置推理模式，关闭 dropout 等训练态行为。
    model.eval()

    prompt = "Customer support summary: the user paid successfully but the order status is still pending."

    # 先把 prompt 编码成模型需要的输入。
    inputs = tokenizer(prompt, return_tensors="pt")

    # 在不计算梯度的上下文里做生成推理。
    # do_sample=True 表示使用采样，而不是纯贪心解码。
    # temperature 越低，输出越稳定；越高，输出越发散。
    # top_p 用于限制采样候选范围。
    # max_new_tokens 控制最多再生成多少个新 token。
    with torch.no_grad():
        output_ids = model.generate(
            **inputs,
            do_sample=True,
            temperature=0.7,
            top_p=0.9,
            max_new_tokens=60,
            pad_token_id=tokenizer.eos_token_id,
        )

    # 把模型输出重新解码成可读文本。
    generated_text = tokenizer.decode(output_ids[0], skip_special_tokens=True)

    print("原始提示词：")
    print(prompt)
    print()
    print("生成结果：")
    print(generated_text)


if __name__ == "__main__":
    main()
