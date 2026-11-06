# study-transformer-project

这个目录用于沉淀 Hugging Face `transformers` 在自然语言模型方向上的常用用法示例，并补充 `hf` CLI 的高频命令，方便后续做本地推理、数据准备、模型下载和训练前验证。

## 目录说明

- `TRANSFORMERS_NLP_GUIDE.md`：`transformers` 常用模块与 NLP 场景学习说明
- `01_tokenizer_basics.py`：Tokenizer 的基础编码与解码示例
- `02_text_classification_pipeline.py`：文本分类 `pipeline` 基础示例
- `03_causal_lm_generate.py`：因果语言模型的基础加载与生成示例
- `04_chat_template_generate.py`：聊天模板与多轮消息生成示例
- `05_trainer_sequence_classification.py`：基于 `Trainer` 的文本分类训练骨架

## 环境建议

建议至少安装：

```bash
pip install transformers datasets accelerate huggingface_hub torch
```

如果只是做推理与模型下载，通常至少需要：

```bash
pip install transformers huggingface_hub torch
```

## `hf` CLI 常用方法

当前 Hugging Face 官方 CLI 文档默认使用 `hf` 命令。部分环境里你也可能看到旧命令 `huggingface-cli`，但新文档和新示例通常优先使用 `hf`。

### 1. 登录与登出

```bash
hf auth login
hf auth whoami
hf auth logout
```

适用场景：

- 访问私有模型或数据集
- 上传文件到 Hub
- 在远程机器上验证当前账号

### 2. 下载整个模型仓库

```bash
hf download Qwen/Qwen2.5-0.5B-Instruct --local-dir ./models/Qwen2.5-0.5B-Instruct
```

适用场景：

- 把模型完整下载到本地目录
- 为离线推理或远程服务器部署准备模型文件

常见说明：

- `--local-dir` 用于指定下载到哪个目录
- 如果不加 `--local-dir`，CLI 通常会返回缓存路径

### 3. 只下载指定文件

```bash
hf download gpt2 config.json model.safetensors tokenizer.json
```

适用场景：

- 只拉取部分文件做检查
- 不想一次下载完整模型仓库

### 4. 下载数据集仓库文件

```bash
hf download datasets/imdb --repo-type dataset --local-dir ./datasets/imdb
```

适用场景：

- 下载公开数据集
- 学习数据结构或做本地缓存

### 5. 查看缓存

```bash
hf cache ls
```

适用场景：

- 查看本机已经缓存了哪些模型和数据
- 排查磁盘占用

### 6. 删除缓存

```bash
hf cache rm MODEL_ID
hf cache prune
```

适用场景：

- 删除指定缓存
- 清理已经不再使用的缓存

使用前建议先查看缓存内容，避免误删当前正在使用的模型。

### 7. 上传文件或目录到 Hub

```bash
hf upload my-username/my-model ./README.md README.md
hf upload-large-folder my-username/my-model ./outputs/my-model
```

适用场景：

- 上传模型卡、配置文件、适配器
- 上传较大的模型目录

### 8. 创建仓库

```bash
hf repo create my-model
hf repo create my-dataset --repo-type dataset
```

适用场景：

- 创建模型仓库
- 创建数据集仓库

### 9. 常用排查思路

如果下载失败，优先检查：

- 是否已经 `hf auth login`
- 模型仓库是否私有
- 本机网络是否可访问 Hugging Face
- 磁盘空间是否足够
- 模型名是否写错

## 推荐学习顺序

如果你是第一次系统学习 `transformers`，建议按下面顺序看本目录内容：

1. 先看 `01_tokenizer_basics.py`
2. 再看 `02_text_classification_pipeline.py`
3. 然后看 `03_causal_lm_generate.py`
4. 再看 `04_chat_template_generate.py`
5. 最后看 `05_trainer_sequence_classification.py`

## 使用提醒

- 文本分类任务优先先掌握 `Tokenizer`、`pipeline`、`AutoModelForSequenceClassification`
- 生成任务优先掌握 `AutoTokenizer`、`AutoModelForCausalLM`、`generate`
- 聊天模型建议优先理解 `apply_chat_template`
- 训练前先固定好验证集和测试集，避免后面结论失真

## Qwen2.5-3B-Instruct 显存计算示例

这一节用 `Qwen/Qwen2.5-3B-Instruct` 做一个“部署推理大概需要多少显存”的完整计算示例。这里重点不是只给出结论，而是把每一步为什么这样算讲清楚。

### 1. 先明确我们到底在算什么

当你问“一个模型部署运行需要多少显存”时，实际上至少包含三类东西：

- 模型权重本身占多少显存
- 推理过程中 KV Cache 占多少显存
- 框架运行余量、临时张量、显存碎片等额外开销

所以部署显存不是只看“模型有多少参数”就结束了。参数量只能先告诉你“模型权重本体大概多大”，但不能直接代表完整推理显存。

### 2. 官方关键信息

按 Hugging Face 官方模型卡和配置文件，`Qwen2.5-3B-Instruct` 的关键信息包括：

- 参数量：`3.09B`
- 非 Embedding 参数量：`2.77B`
- 层数：`36`
- `hidden_size = 2048`
- `num_attention_heads = 16`
- `num_key_value_heads = 2`
- 上下文长度：`32768`

参考资料：

- https://huggingface.co/Qwen/Qwen2.5-3B-Instruct
- https://huggingface.co/Qwen/Qwen2.5-3B-Instruct/blob/main/config.json

### 3. 第一步：计算模型权重本身需要多少显存

### 3.1 为什么可以这样算

模型参数量的意思是：模型里一共有多少个需要存储的权重数值。

例如：

- 如果一个模型有 `3.09B` 参数
- 每个参数用 `2 Byte` 存储

那模型权重总大小就近似等于：

```text
参数量 × 每个参数占用字节数
```

这是因为权重本质上就是一大堆数字，每个数字需要按某种精度存储。

### 3.2 常见精度对应多少字节

- `FP32`：每个参数 `4 Byte`
- `FP16`：每个参数 `2 Byte`
- `BF16`：每个参数 `2 Byte`
- `INT8`：每个参数 `1 Byte`
- `INT4`：每个参数 `0.5 Byte`

### 3.3 用 Qwen2.5-3B-Instruct 计算

模型参数量：

```text
3.09B = 3.09 × 10^9
```

如果用 `BF16/FP16` 部署：

```text
显存 = 3.09 × 10^9 × 2 Byte
     = 6.18 × 10^9 Byte
     ≈ 5.76 GiB
```

如果用 `INT8` 部署：

```text
显存 = 3.09 × 10^9 × 1 Byte
     = 3.09 × 10^9 Byte
     ≈ 2.88 GiB
```

如果用 `INT4` 部署：

```text
显存 = 3.09 × 10^9 × 0.5 Byte
     = 1.545 × 10^9 Byte
     ≈ 1.44 GiB
```

### 3.4 这里为什么还没有算 KV Cache

因为“参数量”统计的是模型的可学习权重，也就是模型文件里保存的那些参数。

KV Cache 不是模型训练出来保存在 checkpoint 里的静态权重，而是模型在推理过程中，针对“当前这一次输入”动态生成并缓存的中间结果。

可以这样区分：

- 参数量：模型自带的长期静态内容
- KV Cache：推理时临时生成、随输入长度变化的动态内容

所以参数量里不包含 KV Cache，这是两个不同层面的东西。

### 4. 第二步：为什么还要单独计算 KV Cache

对于自回归大语言模型，生成第 N 个 token 时，需要回看前面已经算过的 Key 和 Value。为了避免每生成一个 token 都把前文全部重新算一遍，推理框架通常会把之前每一层的 K、V 存下来，这就是 KV Cache。

这部分显存具有几个特点：

- 它在推理时才出现
- 它会随着上下文长度增长
- 它与 batch size 有关
- 它不是模型参数文件的一部分

因此，如果只算模型权重，不算 KV Cache，就会低估真实部署显存。

### 5. 第三步：计算 KV Cache 需要多少显存

### 5.1 先算每个 attention head 的维度

注意力头维度通常是：

```text
head_dim = hidden_size / num_attention_heads
```

代入配置：

```text
head_dim = 2048 / 16 = 128
```

### 5.2 为什么 KV Cache 用 `num_key_value_heads`

Qwen2.5-3B-Instruct 使用的是 GQA 结构。也就是说：

- Query 头数是 `16`
- 但真正存储 K 和 V 的头数只有 `2`

因此，在算 KV Cache 时，要用的是：

```text
num_key_value_heads = 2
```

而不是 `num_attention_heads = 16`。

### 5.3 每层、每个 token 要缓存多少元素

对每一层、每一个 token 来说，需要缓存：

- 一份 Key
- 一份 Value

所以每层每 token 的缓存元素数为：

```text
2 × num_key_value_heads × head_dim
```

代入配置：

```text
2 × 2 × 128 = 512
```

这里第一个 `2` 表示 K 和 V 两份。

### 5.4 全部层数合起来

模型一共有 `36` 层，因此每个 token 在全模型中需要缓存的总元素数为：

```text
512 × 36 = 18432
```

### 5.5 这些元素各占多少字节

如果按 `BF16/FP16` 推理，每个元素通常按 `2 Byte` 存储。

因此，每个 token 的 KV Cache 大小约为：

```text
18432 × 2 Byte = 36864 Byte
≈ 36 KiB
```

### 5.6 按上下文长度继续算

如果上下文长度是 `8K = 8192 token`：

```text
8192 × 36864 Byte
= 301,989,888 Byte
≈ 288 MiB
≈ 0.28 GiB
```

如果上下文长度是 `32K = 32768 token`：

```text
32768 × 36864 Byte
= 1,207,959,552 Byte
≈ 1.125 GiB
```

### 5.7 为什么 KV Cache 和上下文长度相关

因为上下文越长，历史 token 越多，需要缓存的 K 和 V 就越多。

这也是为什么：

- 长上下文模型不一定参数更多
- 但长上下文推理时显存仍然可能更高

因为增大的不一定是模型权重，而可能是推理过程中的缓存开销。

### 6. 第四步：把权重显存和 KV Cache 显存合起来

如果按 `BF16/FP16` 部署：

#### 6.1 8K 上下文

模型权重：

```text
≈ 5.76 GiB
```

KV Cache：

```text
≈ 0.28 GiB
```

合计：

```text
5.76 + 0.28 = 6.04 GiB
```

#### 6.2 32K 上下文

模型权重：

```text
≈ 5.76 GiB
```

KV Cache：

```text
≈ 1.13 GiB
```

合计：

```text
5.76 + 1.13 = 6.89 GiB
```

### 7. 第五步：为什么最终部署显存还要再加余量

虽然上面已经算出了“权重 + KV Cache”，但这还不是最终可部署显存。

因为真实部署时还会有：

- 框架本身的运行开销
- CUDA Runtime 开销
- 中间临时张量
- 显存碎片
- 服务框架额外占用，例如 `transformers`、`vLLM`、TGI

所以工程上不能把“理论最小值”直接当成“可稳定运行值”。

更稳妥的做法是：

- 在理论值上额外预留 `1~2 GiB` 甚至更多余量

### 8. 最终结论

对于 `Qwen2.5-3B-Instruct`，如果是单卡推理部署，可以先这样判断：

- `BF16/FP16` + `8K` 上下文：理论核心占用约 `6.04 GiB`，建议至少 `8GB` 显存，稳妥一些是 `10GB`
- `BF16/FP16` + `32K` 上下文：理论核心占用约 `6.89 GiB`，建议至少 `10GB` 显存，稳妥一些是 `12GB`
- `INT8` 量化：通常 `6GB` 左右有机会运行，稳妥建议 `8GB`
- `INT4` 量化：通常 `4GB` 级别就有机会运行，稳妥建议 `6GB`

### 9. 一句话理解“为什么参数量里不包含 KV Cache”

因为：

- 参数量描述的是模型本身有多少静态权重
- KV Cache 描述的是模型推理时为当前输入临时保存了多少中间结果

前者属于“模型文件大小”的范畴，后者属于“运行时显存开销”的范畴，所以必须分开计算。

## 常用量化与精度参数说明

这一节补充部署和推理时最常见的精度与量化概念。很多人在看模型部署文档时，经常会看到 `FP16`、`BF16`、`INT8`、`INT4` 这些词。它们本质上是在描述：模型里的数值用什么格式存储和计算。

一个最直接的影响是：

- 精度越高，通常占用显存越多
- 精度越低，通常占用显存越少

但这不是单纯的“越低越好”，因为更低精度通常也会带来一定的精度损失、兼容性问题，或者推理速度不一定线性提升。

### 1. FP32

`FP32` 是 32 位浮点数，也叫单精度浮点数。

特点：

- 每个参数通常占 `4 Byte`
- 数值表达范围和精度都比较高
- 显存占用最大

适用场景：

- 训练中的高精度计算
- 调试数值稳定性问题
- 一些必须优先保证数值精度的场景

在大模型部署里，`FP32` 通常不是首选，因为显存占用太高。

### 2. FP16

`FP16` 是 16 位浮点数，也叫半精度浮点数。

特点：

- 每个参数通常占 `2 Byte`
- 显存占用约为 `FP32` 的一半
- 在很多 GPU 场景里是常见的推理精度

适用场景：

- 大模型推理
- 混合精度训练
- 对显存较敏感、但又希望保持较好精度的场景

局限：

- 数值范围比 `FP32` 小
- 某些场景下更容易出现溢出或下溢

### 3. BF16

`BF16` 是 Brain Floating Point 16。

特点：

- 每个参数通常占 `2 Byte`
- 显存占用与 `FP16` 接近
- 指数范围更接近 `FP32`，数值稳定性通常比 `FP16` 更好

适用场景：

- 现代 GPU 上的大模型训练和推理
- 希望兼顾显存与稳定性的场景

工程上常见经验是：

- 如果硬件支持 `BF16`，很多时候会优先考虑 `BF16`
- 如果硬件或框架支持不理想，则退回 `FP16`

### 4. INT8

`INT8` 是 8 位整数表示。

特点：

- 每个参数通常占 `1 Byte`
- 权重显存约为 `FP16/BF16` 的一半
- 常用于量化推理

适用场景：

- 显存更紧张的部署环境
- 希望在较小精度损失下减少显存占用

需要注意：

- 量化后不只是“存储变小”这么简单，实际推理效果还和量化算法、校准方法、硬件支持有关
- 并不是所有模型都能在 `INT8` 下保持非常稳定的一致效果

### 5. INT4

`INT4` 是 4 位整数表示。

特点：

- 每个参数通常占 `0.5 Byte`
- 显存占用进一步下降
- 是大模型低显存部署里非常常见的一类方案

适用场景：

- 单卡显存比较紧张
- 希望在消费级 GPU 上部署更大的模型

需要注意：

- 精度损失风险通常高于 `INT8`
- 不同量化方法差异会更明显
- 实际效果很依赖模型结构、量化工具和任务类型

### 6. 为什么这些参数会影响显存

原因很直接：模型参数本质上是数字数组，而不同精度格式用来表示同一个数字时，占用的字节数不同。

例如同一个 `3.09B` 参数模型：

- `FP32`：`3.09B × 4 Byte`
- `FP16/BF16`：`3.09B × 2 Byte`
- `INT8`：`3.09B × 1 Byte`
- `INT4`：`3.09B × 0.5 Byte`

所以精度选择会直接影响模型权重显存。

### 7. 为什么量化后不代表所有显存都同比例下降

这是一个很重要的点。很多初学者会误以为：

- 模型从 `FP16` 变成 `INT4`
- 那部署总显存就一定刚好变成四分之一

实际并不能这样简单推断。原因是部署总显存除了模型权重，还包括：

- KV Cache
- 临时激活值
- 框架运行开销
- 显存碎片

其中：

- 权重量化后会明显下降
- 但 KV Cache 不一定会按同样比例下降
- 框架额外开销也不会按权重比例缩小

所以量化会显著降低显存，但总显存下降通常不会和“权重字节数缩小比例”完全一样。

### 8. 常见量化相关术语

除了 `FP16`、`INT8`、`INT4` 这些精度描述外，部署文档里还经常会看到一些量化方案名，例如：

- `GPTQ`
- `AWQ`
- `GGUF`
- `bitsandbytes 8bit/4bit`

这些词通常不是单纯表示“几位数”，而是在表示：

- 用什么量化算法
- 用什么存储格式
- 配套什么推理框架

也就是说：

- `INT4` 更像是在说“量化后的位宽”
- `AWQ`、`GPTQ` 更像是在说“采用哪种量化方法”

### 9. 工程上怎么选

可以先按这个简单思路判断：

- 显存充足，优先 `BF16` 或 `FP16`
- 显存一般，希望兼顾效果与体积，可以优先考虑 `INT8`
- 显存紧张，尤其是消费级 GPU 部署较大模型时，可以考虑 `INT4`

如果是学习阶段，建议优先建立下面这层认知：

- `FP16/BF16` 更接近原始模型精度
- `INT8/INT4` 更偏向部署优化手段
- 量化不是“免费压缩”，而是用一部分精度和兼容性复杂度换更低显存

## 不同 Tokenizer 的特殊词是否一样

不一样。不同模型使用的 Tokenizer，特殊 token 往往会不同。这种不同不只是“名字不同”，还可能体现在用途、数量以及是否存在某个特殊 token 上。

### 1. 为什么会不同

因为不同模型的设计目标不一样，例如：

- `BERT` 属于编码器模型，更强调句子表示和分类任务
- `GPT` 一类模型属于自回归生成模型，更强调逐 token 生成
- 聊天模型还会额外引入角色结构，例如 `system`、`user`、`assistant`

所以它们在训练时需要的输入结构不同，Tokenizer 里配套的特殊 token 也就会不同。

### 2. 常见差异有哪些

常见差异主要有：

- 特殊 token 的名字不同
- 特殊 token 的作用不同
- 某些模型根本没有某些特殊 token
- 同一类作用的特殊 token，字符串表示也可能不同

### 3. 常见例子

`BERT` 类模型常见的特殊 token 有：

- `[CLS]`
- `[SEP]`
- `[PAD]`
- `[MASK]`
- `[UNK]`

这些 token 主要用于：

- 句子开始位置
- 句子分隔
- 补齐长度
- 掩码训练
- 未知词处理

`GPT2` 一类模型通常更关注生成，因此常见情况是：

- 可能没有 `pad_token`
- 更常见 `eos_token`
- 不一定有 `[CLS]`、`[SEP]`

聊天模型中还可能看到：

- `<|system|>`
- `<|user|>`
- `<|assistant|>`
- `<bos>`
- `<eos>`

这类特殊 token 更像是在表达“消息结构”或“对话角色”。

### 4. 使用时不要默认混用

不能假设：

- 所有模型都有 `[CLS]`
- 所有模型都有 `[SEP]`
- 所有模型都支持同一种 prompt 模板

如果把一种模型的模板结构直接照搬到另一种模型，效果可能会明显变差，甚至出现格式错误。

### 5. 怎么查看当前 tokenizer 的特殊 token

最稳妥的方式是直接查看 tokenizer 自己的定义，例如：

```python
from transformers import AutoTokenizer

tokenizer = AutoTokenizer.from_pretrained("bert-base-chinese")

print("special_tokens_map =", tokenizer.special_tokens_map)
print("all_special_tokens =", tokenizer.all_special_tokens)
print("all_special_ids =", tokenizer.all_special_ids)
```

### 6. 一句话总结

不同 Tokenizer 的特殊词通常不一样，因为它们服务的模型结构、训练目标和输入格式本来就不同。实际使用时，应以当前模型自己的 Tokenizer 定义为准，不要想当然地把不同模型的特殊 token 和模板混用。
