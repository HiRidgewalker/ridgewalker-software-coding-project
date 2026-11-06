"""
这个文件演示如何使用 Hugging Face Trainer 搭建一个文本分类训练骨架。

学习重点：
1. 训练数据需要如何预处理
2. Trainer 需要哪些核心对象
3. compute_metrics 应该怎么接
4. 为什么训练集、验证集、测试集必须分开

说明：
这个示例是教学骨架，不是针对当前仓库数据的最终训练脚本。
真正接入业务数据时，你需要替换数据集读取逻辑、标签映射和评估指标。
"""

from datasets import Dataset
from transformers import (
    AutoModelForSequenceClassification,
    AutoTokenizer,
    DataCollatorWithPadding,
    Trainer,
    TrainingArguments,
)


def build_demo_dataset() -> Dataset:
    # 这里构造一个很小的演示数据集，目的是说明 Trainer 的基本接线方式。
    # label 字段是分类标签，0 和 1 只是最小示例。
    data = {
        "text": [
            "支付成功但是订单状态没有更新",
            "想申请退款，商品还没有发货",
            "账号登录异常，验证码无法接收",
            "物流太慢了，已经等待很多天",
        ],
        "label": [0, 1, 0, 1],
    }
    return Dataset.from_dict(data)


def main() -> None:
    model_name = "bert-base-chinese"

    tokenizer = AutoTokenizer.from_pretrained(model_name)

    # 加载序列分类模型。
    # num_labels=2 表示这里做一个二分类示例。
    model = AutoModelForSequenceClassification.from_pretrained(
        model_name,
        num_labels=2,
    )

    dataset = build_demo_dataset()

    # 预处理函数的任务是把原始文本字段转成模型输入字段。
    def preprocess_function(batch):
        return tokenizer(
            batch["text"],
            truncation=True,
            max_length=128,
        )

    tokenized_dataset = dataset.map(preprocess_function, batched=True)

    # 这里为了让示例最简，直接把前 2 条作为训练集，后 2 条作为验证集。
    # 在真实项目中，必须使用更合理、严格的数据切分方式。
    train_dataset = tokenized_dataset.select([0, 1])
    eval_dataset = tokenized_dataset.select([2, 3])

    # DataCollatorWithPadding 会在一个 batch 内自动按最长样本进行补齐，
    # 这样就不需要手工把所有文本都 pad 到统一固定长度。
    data_collator = DataCollatorWithPadding(tokenizer=tokenizer)

    # compute_metrics 用于把模型输出转成更容易理解的评估指标。
    # 这里为了减少额外依赖，示例里只手工计算 accuracy。
    def compute_metrics(eval_pred):
        logits, labels = eval_pred

        # logits 是模型输出的未归一化分数。
        # 对二分类或多分类任务，通常取最大值对应的类别作为预测结果。
        predictions = logits.argmax(axis=-1)
        accuracy = (predictions == labels).mean().item()
        return {"accuracy": accuracy}

    # TrainingArguments 定义 Trainer 在训练和评估阶段的行为。
    # 这里的每个参数都在控制“训练过程怎么跑”，而不是控制模型结构本身。
    training_args = TrainingArguments(
        # output_dir 指定训练过程中产物的默认输出目录。
        # 常见产物包括：
        # 1. checkpoint
        # 2. 日志状态
        # 3. 训练参数快照
        # 这个示例里虽然 save_strategy="no" 不保存 checkpoint，
        # 但 Trainer 仍然需要一个输出目录作为运行时工作目录。
        output_dir="./tmp_trainer_output",

        # per_device_train_batch_size 表示“每张设备卡上的训练 batch size”。
        # 如果你只有 1 张 GPU，那么这里的值基本就等于单步训练时实际喂给模型的样本数。
        # 如果你有多张 GPU，总训练 batch size 还会继续乘上 GPU 数量，
        # 以及是否使用 gradient accumulation。
        # 这个值越大，通常训练吞吐越高，但显存占用也会越高。
        per_device_train_batch_size=2,

        # per_device_eval_batch_size 表示“每张设备卡上的评估 batch size”。
        # 它只影响验证/评估阶段，不影响训练阶段。
        # 评估时通常不需要反向传播，因此在很多场景下，
        # 这个值可以设置得比训练 batch size 更大。
        per_device_eval_batch_size=2,

        # num_train_epochs 表示完整遍历训练集多少轮。
        # 例如这里设为 1，表示把训练集完整跑 1 次就结束。
        # 如果训练集很小，epoch 太多可能导致过拟合；
        # 如果训练集较大，通常需要结合验证集指标来决定训练轮数。
        num_train_epochs=1,

        # logging_steps 表示每训练多少个 step 记录一次日志。
        # step 可以理解为“完成一次参数更新”。
        # 这里设为 1，表示每一步都打印日志，便于教学观察。
        # 在真实训练中，如果数据很多，这个值通常不会设这么小，
        # 否则日志会非常频繁。
        logging_steps=1,

        # eval_strategy 控制“什么时候运行验证集评估”。
        # 这里设为 "epoch"，表示每跑完一整轮训练集，就在验证集上评估一次。
        # 常见取值还包括：
        # 1. "no"：不自动评估
        # 2. "steps"：每隔固定训练步数评估一次
        # 对初学者来说，"epoch" 是最容易理解的方式。
        eval_strategy="epoch",

        # save_strategy 控制“什么时候保存 checkpoint”。
        # 这里设为 "no"，表示训练过程中不自动保存任何 checkpoint。
        # 这样做是为了让教学示例更简单，避免在仓库里生成额外文件。
        # 在真实项目中，常见做法是：
        # 1. 按 epoch 保存
        # 2. 按 steps 保存
        # 3. 配合 save_total_limit 控制最多保留多少份 checkpoint
        save_strategy="no",

        # report_to 控制把训练日志上报到哪些外部实验跟踪平台。
        # 这里设为 "none"，表示不把日志发送到 WandB、TensorBoard、
        # MLflow 等外部系统，只在本地 Trainer 流程里使用。
        # 这样更适合最小教学示例，避免额外依赖和环境配置。
        report_to="none",
    )

    # Trainer 是 Hugging Face 提供的标准训练封装。
    # 你可以把它理解成一个“训练流程调度器”：
    # 它接收模型、训练参数、数据集和评估函数，然后负责把这些部件串起来。
    trainer = Trainer(
        # model 是要训练或评估的模型对象。
        # 这里传入的是 AutoModelForSequenceClassification 加载出来的文本分类模型。
        # Trainer 会在训练阶段调用这个模型做前向传播、计算 loss，
        # 并在评估阶段用它产出 logits。
        model=model,

        # args 是前面定义好的 TrainingArguments。
        # 它决定训练流程中的很多关键行为，例如：
        # 1. 输出目录
        # 2. batch size
        # 3. 训练轮数
        # 4. 日志记录频率
        # 5. 是否保存 checkpoint
        # 也就是说，model 决定“学什么结构”，args 决定“怎么训练它”。
        args=training_args,

        # train_dataset 是训练集。
        # Trainer 会在 trainer.train() 时使用这部分数据更新模型参数。
        # 它要求数据集中至少能提供模型前向传播所需的字段，
        # 例如 input_ids、attention_mask、labels。
        # 在这个示例里，原始 text 已经先通过 tokenizer 转成了模型可用字段。
        train_dataset=train_dataset,

        # eval_dataset 是验证集或评估集。
        # 当调用 trainer.evaluate()，或者训练过程中触发自动评估时，
        # Trainer 会使用这部分数据来计算指标。
        # 它不参与参数更新，只用于观察模型效果。
        eval_dataset=eval_dataset,

        # processing_class 在新版本 transformers 中用于传入预处理对象。
        # 对文本任务来说，这里通常传 tokenizer。
        # 它的作用和旧版本 Trainer 里的 tokenizer 参数类似，主要用于：
        # 1. 配合 data collator 处理批数据
        # 2. 在保存或恢复训练相关资源时，保留分词器信息
        # 对文本任务来说，把 tokenizer 一起传入通常是推荐做法，
        # 因为它和模型输入格式直接相关。
        processing_class=tokenizer,

        # data_collator 负责把“若干单条样本”拼成一个 batch。
        # 它会在 DataLoader 取数据时被调用。
        # 这里使用 DataCollatorWithPadding，作用是：
        # 1. 自动把一个 batch 内的样本补齐到同样长度
        # 2. 避免你手工提前把所有样本 pad 到固定最大长度
        # 这样通常更节省显存，也更适合长度不一致的文本数据。
        data_collator=data_collator,

        # compute_metrics 是评估指标函数。
        # Trainer 在评估阶段拿到模型输出后，会把结果传给这个函数，
        # 再把函数返回的指标字典记录或打印出来。
        # 这里我们只返回 accuracy，
        # 真实项目里通常会返回更多指标，例如 Macro F1、Precision、Recall。
        compute_metrics=compute_metrics,
    )

    # 启动训练。
    trainer.train()

    # 在验证集上做一次评估，输出 accuracy 等指标。
    metrics = trainer.evaluate()
    print(metrics)


if __name__ == "__main__":
    main()
