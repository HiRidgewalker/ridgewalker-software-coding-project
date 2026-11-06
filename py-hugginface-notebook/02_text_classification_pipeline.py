"""
这个文件演示如何用 pipeline 快速完成文本分类推理。

学习重点：
1. 什么情况下适合先用 pipeline 做验证
2. 文本分类任务如何快速跑通输入到输出
3. 为什么 pipeline 适合 Demo，但不一定适合复杂训练或复杂评测
"""

from transformers import pipeline


def main() -> None:
    # 这里使用情感分类模型作为最小可运行示例。
    # 在真实业务中，你可以换成自己训练好的分类模型，或者换成支持中文分类的模型。
    model_name = "distilbert-base-uncased-finetuned-sst-2-english"

    # 创建文本分类 pipeline。
    # task="text-classification" 指定任务类型。
    # model 参数指定要加载的模型。
    # tokenizer 参数如果不显式给出，通常会自动从同名仓库加载。
    classifier = pipeline(
        task="text-classification",
        model=model_name,
    )

    # 准备多条文本，演示批量推理。
    texts = [
        "I am very happy with the service.",
        "The package arrived late and the support was unhelpful.",
    ]

    # 直接把文本列表传给 pipeline，内部会自动做 tokenize、模型推理和结果整理。
    results = classifier(texts)

    print("文本分类结果：")
    for text, result in zip(texts, results):
        print("-" * 60)
        print("输入文本：", text)
        print("预测结果：", result)


if __name__ == "__main__":
    main()
