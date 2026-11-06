"""
这个文件演示聊天模型在 Hugging Face 中更推荐的消息构造方式：
先使用 tokenizer.apply_chat_template，再调用 model.generate。

学习重点：
1. 为什么聊天模型不建议只靠手写字符串拼 prompt
2. apply_chat_template 的输入结构是什么
3. add_generation_prompt 在什么场景下有用
"""

import torch
from copy import deepcopy
from transformers import AutoModelForCausalLM, AutoTokenizer


def main() -> None:
    # 这里放一个聊天模型名称作为示例。
    # 如果本地没有对应模型，运行前请先下载或替换成自己可访问的聊天模型。
    model_name = "Qwen/Qwen2.5-0.5B-Instruct"

    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model = AutoModelForCausalLM.from_pretrained(
        model_name,
        torch_dtype=torch.float32,
    )
    model.eval()

    # 聊天模型常用的输入不是单个纯文本字符串，而是一组带角色的消息。
    # role 常见取值包括 system、user、assistant。
    messages = [
        {
            "role": "system",
            "content": "你是一个客服工单分类助手，请给出简洁判断。",
        },
        {
            "role": "user",
            "content": "用户说已经扣款，但是订单仍显示待支付，这条工单更像哪个问题类别？",
        },
    ]

    # apply_chat_template 会按照模型自带模板把消息列表整理成最终输入格式。
    # tokenize=True 表示直接输出 token 化结果，而不是纯字符串。
    # add_generation_prompt=True 表示在末尾补上“接下来该 assistant 回答”的提示结构。
    # return_dict=True 很重要，这样返回的是一个 BatchEncoding，
    # 里面会显式包含 input_ids、attention_mask 等字段。
    # 之后要把这些字段展开后传给 model.generate，而不是把整个对象当作单个张量传进去。
    model_inputs = tokenizer.apply_chat_template(
        messages,
        tokenize=True,
        add_generation_prompt=True,
        return_tensors="pt",
        return_dict=True,
    )

    # 这里记录输入长度，后面只截取“新生成部分”时会用到。
    input_length = model_inputs["input_ids"].shape[-1]

    # 某些聊天模型自带的 generation config 里会包含 temperature、top_p、top_k。
    # 当 do_sample=False 时，这些采样参数不会生效，并可能触发提示信息。
    # 这里复制一份 generation config，并把与采样相关的参数清空，避免误导。
    generation_config = deepcopy(model.generation_config)
    generation_config.do_sample = False
    generation_config.temperature = None
    generation_config.top_p = None
    generation_config.top_k = None

    with torch.no_grad():
        output_ids = model.generate(
            **model_inputs,
            max_new_tokens=64,
            generation_config=generation_config,
        )

    # 这里只截取“新生成部分”，避免把整段输入也一起打印得过长。
    new_tokens = output_ids[0][input_length:]
    response_text = tokenizer.decode(new_tokens, skip_special_tokens=True)
    all_generate_text = tokenizer.decode(output_ids[0], skip_special_tokens=True)

    print("模型回复：")
    print(response_text)

    print("完整模型输出：")
    print(all_generate_text)




if __name__ == "__main__":
    main()
