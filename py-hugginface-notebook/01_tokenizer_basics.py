"""
这个文件演示 Hugging Face Tokenizer 在 NLP 任务中的最基础用法。

学习重点：
1. 文本如何编码成 token id
2. token id 如何再解码回文本
3. 常见字段如 input_ids、attention_mask 是什么
4. 为什么长度控制在工程中很重要
"""

from transformers import AutoTokenizer


def main() -> None:
    # 这里选择一个较小、常见、容易理解的模型分词器做示例。
    # 注意：不同模型的 Tokenizer 规则不同，所以相同文本在不同模型下切分结果可能不一样。
    model_name = "bert-base-chinese"

    # 从 Hugging Face Hub 加载分词器。
    # 如果本地已经缓存过对应文件，这一步会优先使用缓存。
    tokenizer = AutoTokenizer.from_pretrained(model_name)

    # 准备一个简单的中文文本样例。
    text = "用户反馈支付成功，但是订单状态没有更新。"

    # 调用分词器把原始文本编码为模型可处理的输入。
    # return_tensors="pt" 表示直接返回 PyTorch Tensor，方便后续送入模型。
    # padding=False 表示这里不做补齐，因为当前只处理一条文本。
    # truncation=True 表示当文本过长时允许截断，避免超过模型可接受的最大长度。
    encoded = tokenizer(
        text,
        return_tensors="pt",
        padding=False,
        truncation=True,
        max_length=32,
    )

    print("原始文本：")
    print(text)
    print()

    # input_ids 是模型真正看到的 token 编号序列。
    print("input_ids：")
    print(encoded["input_ids"])
    print()

    # attention_mask 用来告诉模型哪些位置是有效 token。
    # 一般 1 表示有效位置，0 表示 padding 位置。
    print("attention_mask：")
    print(encoded["attention_mask"])
    print()

    # convert_ids_to_tokens 可以把 token id 转回“分词后的 token 片段”，
    # 便于观察 Tokenizer 实际是怎么切分文本的。
    tokens = tokenizer.convert_ids_to_tokens(encoded["input_ids"][0])
    print("切分后的 token：")
    print(tokens)
    print()

    # decode 会把 token id 序列重新解码成字符串。
    # skip_special_tokens=True 表示去掉 [CLS]、[SEP] 等特殊 token。
    decoded_text = tokenizer.decode(encoded["input_ids"][0], skip_special_tokens=True)
    print("解码后的文本：")
    print(decoded_text)
    print()

    # 统计 token 长度在工程里很重要：
    # 1. 可以判断输入会不会超模型上下文
    # 2. 可以估算训练与推理成本
    # 3. 可以辅助决定 max_length 应该设多大
    print("token 数量：", len(encoded["input_ids"][0]))


if __name__ == "__main__":
    main()
