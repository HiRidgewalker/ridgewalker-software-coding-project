# Hugging Face Transformers 在 NLP 方向的常用用法

这份说明面向当前仓库的学习目标，重点放在自然语言处理和大语言模型方向，帮助你理解 `transformers` 里最常用的模块应该怎么配合使用。

## 1. 最常见的模块分层

从工程角度看，`transformers` 在 NLP 任务里可以大致按下面方式理解：

- `AutoTokenizer`：负责文本和 token id 之间的转换
- `AutoModel`：返回基础隐藏状态，适合做特征抽取
- `AutoModelForSequenceClassification`：用于文本分类
- `AutoModelForTokenClassification`：用于序列标注，如 NER
- `AutoModelForCausalLM`：用于自回归生成，如聊天、续写、问答
- `pipeline`：高层封装，适合快速验证
- `Trainer`：标准训练骨架，适合快速搭建训练流程

## 2. 面向 NLP 的典型使用场景

### 2.1 文本分类

常用组合：

- `AutoTokenizer`
- `AutoModelForSequenceClassification`
- `pipeline("text-classification")`

适用任务：

- 情感分类
- 工单分类
- 主题分类
- 意图识别

### 2.2 文本生成

常用组合：

- `AutoTokenizer`
- `AutoModelForCausalLM`
- `model.generate(...)`

适用任务：

- 指令跟随
- 问答
- 摘要
- 改写
- 聊天

### 2.3 聊天模型

常用组合：

- `AutoTokenizer`
- `AutoModelForCausalLM`
- `tokenizer.apply_chat_template(...)`
- `model.generate(...)`

如果模型本身是聊天指令模型，优先使用其 chat template，而不是手写 prompt 拼接，因为模板格式通常会直接影响输出质量。

## 3. 常用开发路径

建议先按下面的工程路径学习：

1. 用 `pipeline` 做快速验证
2. 用 `AutoTokenizer` + `AutoModel...` 进入显式调用
3. 用 `generate` 掌握采样参数
4. 用 `datasets` + `Trainer` 搭训练骨架
5. 再接入 LoRA、QLoRA、评测和部署

## 4. 模块选择经验

### 4.1 什么时候优先用 `pipeline`

适合：

- 快速验证模型能不能跑
- 快速看输出格式
- 做很小规模 Demo

不适合：

- 需要精细控制输入输出
- 需要自定义批处理
- 需要训练
- 需要复杂评测

### 4.2 什么时候直接用 `AutoModel...`

适合：

- 需要自己控制 tokenization
- 需要自定义 `generate`
- 需要接训练逻辑
- 需要和业务代码深度集成

## 5. 针对当前项目的建议

当前仓库是“客服工单文本分类”的学习项目，因此建议优先掌握：

- `AutoTokenizer`
- `AutoModelForSequenceClassification`
- `pipeline("text-classification")`
- `Trainer`

如果后续要进入开源指令模型推理和 QLoRA，再重点补充：

- `AutoModelForCausalLM`
- `generate`
- `apply_chat_template`
- `BitsAndBytesConfig`
- `device_map="auto"`

## 6. 示例代码阅读建议

本目录里的 `.py` 文件按“先基础、再生成、再训练”的顺序组织。建议不要只看 API 名字，而是重点看每一步的输入输出是什么，以及注释里说明的“为什么这么写”。
