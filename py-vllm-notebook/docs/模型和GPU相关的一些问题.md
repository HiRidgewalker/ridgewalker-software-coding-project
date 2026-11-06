# 场景问题：一张 GPU 能否同时跑多个模型？

问题：

我有一张 `24G` 显存的 GPU，例如 `RTX 5090`。现在我有两个模型，例如 `Qwen2.5-7B` 和 `Qwen3.5-7B`。假设这两个模型单独运行时都可以正常推理，而且从静态估算上看，两者推理显存相加小于 `24G`。那么在同一时间，这两个模型是否可以同时在这一张 GPU 上运行？如果可以，`vLLM` 应该怎么启动多实例单卡服务？

答案：

可以。

同一张 GPU 在同一时间并不是只能跑一个模型。只要资源允许，一张卡可以同时驻留多个模型实例，多个模型也可以同时接收请求并执行推理。

但要注意，工程上要把“可以同时跑”与“可以稳定跑”区分开：

1. GPU 不是天然只允许一个模型独占
2. 多个模型可以同时加载到同一张 GPU
3. 多个模型也可以同时发起推理
4. 真正限制你的不是“能不能”，而是显存、算力、KV Cache、上下文长度和并发负载

也就是说：

1. 同一张显卡可以同时跑多个模型
2. 不是同一时刻只能跑一个模型
3. 但如果资源不够，结果会变成延迟变高、吞吐下降、甚至 OOM

对 `vLLM` 来说，最常见的做法不是“一个进程同时管理多个完全不同的模型”，而是：

1. 为每个模型各启动一个 `vLLM` 实例
2. 让这多个实例都绑定到同一张 GPU
3. 通过不同端口分别提供服务

## vLLM 多实例单卡启动示例

假设两套模型都放在本地，并且都使用同一张 `GPU 0`。

### 实例 1：Qwen2.5-7B

```bash
CUDA_VISIBLE_DEVICES=0 vllm serve /path/to/Qwen2.5-7B \
  --host 0.0.0.0 \
  --port 8000 \
  --tensor-parallel-size 1 \
  --gpu-memory-utilization 0.35 \
  --max-model-len 4096
```

### 实例 2：Qwen3.5-7B

```bash
CUDA_VISIBLE_DEVICES=0 vllm serve /path/to/Qwen3.5-7B \
  --host 0.0.0.0 \
  --port 8001 \
  --tensor-parallel-size 1 \
  --gpu-memory-utilization 0.35 \
  --max-model-len 4096
```

说明：

1. 两个实例都绑定 `CUDA_VISIBLE_DEVICES=0`，表示都使用同一张卡
2. 两个实例必须使用不同端口，例如 `8000` 和 `8001`
3. `--tensor-parallel-size 1` 表示每个模型都是单卡实例
4. `--gpu-memory-utilization` 不能贪大，否则两个实例会互相抢显存
5. `--max-model-len` 建议先保守设置，避免 KV Cache 把显存顶满

## 这个场景下的工程判断

如果你要让两个模型共用一张卡，正确判断顺序应该是：

1. 先确认两个实例空载时能否同时启动
2. 再确认各自短请求下是否稳定
3. 再确认长上下文、长输出、并发请求时是否 still 稳定
4. 最后再决定是否继续提高 `gpu-memory-utilization` 或 `max-model-len`

不要只看“模型能启动”。

因为在 `vLLM` 里，真正容易把显存推高的，往往不是模型权重本身，而是：

1. KV Cache
2. 上下文长度
3. 输出长度
4. 并发请求数

## 最终结论

结论可以直接记成一句话：

同一张 GPU 可以同时跑多个模型，`vLLM` 也可以通过“多实例单卡”的方式实现；但是否稳定，取决于显存预算、KV Cache、上下文长度和并发负载，而不是只看模型能否加载成功。

---

# 场景问题：单模型没跑满显存，应该怎么处理？

问题：

如果一张 GPU 上已经跑了一个模型，而且这个模型运行时没有把显存占满，应该怎么处理？

答案：

先不要默认“显存必须占满”。

显存没跑满本身不是问题。你应该先判断自己想把这部分余量换成什么能力，而不是机械地追求把显存塞满。

最常见的几种处理方向如下：

## 1. 如果当前服务已经稳定，先别急着调

显存没满，不代表系统就浪费了资源。

因为真实瓶颈可能根本不在显存，而在：

1. GPU 算力
2. 请求量太少
3. batch 不够
4. CPU / I/O / 调度开销

所以第一判断是：

显存没满不等于必须优化，也不等于一定能通过调参换来收益。

## 2. 如果你想支持更长上下文

优先考虑调大：

1. `max_model_len`

因为更长上下文最直接消耗的是 KV Cache，而显存余量最容易在这里转化为能力。

建议：

1. 从保守值开始逐步增加
2. 不要一下把上下文长度拉得特别大

## 3. 如果你想提高吞吐或并发

可以考虑：

1. 适度提高 `gpu-memory-utilization`
2. 提高并发请求数量
3. 使用 batch / continuous batching

这类方式的本质是：让同一个模型在同一时间处理更多请求，把空闲显存和算力转化为吞吐。

## 4. 如果你想在同一张卡上放更大的模型

那么这部分余量就可以直接用来换模型规模。

例如：

1. 换成更大的模型
2. 保持模型不变，但适度放宽上下文长度和输出长度

## 5. 如果你想在同一张卡上再跑一个模型

也可以。

如果一个模型明显占不满显存，那么一个现实可行的选择就是：

1. 再启动一个模型实例
2. 或再启动一个不同模型的服务实例
3. 通过不同端口分别提供服务

但这时候不要只看空载显存，要看双模型同时接请求时的动态峰值。

## 最终结论

如果单模型没跑满显存，正确的问题不是“怎么把显存塞满”，而是：

我想把这部分余量换成长上下文、更高并发、更大模型，还是第二个模型？

---

# 场景问题：vLLM 在线部署下，静态 batch 和动态 batch 怎么做？

问题：

同一个大模型在在线部署场景下，是否可以同时推理多个 prompt？如果可以，`vLLM` 的静态 batch 和动态 batch 分别怎么做？

答案：

可以。

同一个模型在同一时间可以处理多个 prompt。这正是 batch 和 continuous batching 的意义，也是提高 GPU 利用率和吞吐的常见方式。

在 `vLLM` 在线部署场景下，可以分成两类：

1. 静态 batch：一次请求里直接带多个 prompt
2. 动态 batch：多个请求并发发到服务端，由 `vLLM` 自动合批调度

## 先启动在线服务

```bash
vllm serve models/Qwen/Qwen3.5-2B \
  --host 0.0.0.0 \
  --port 8000 \
  --tensor-parallel-size 1 \
  --gpu-memory-utilization 0.80 \
  --max-model-len 4096
```

## 1. 静态 batch 示例

一次请求里直接传多个 prompt：

```bash
curl --noproxy '*' -s http://127.0.0.1:8000/v1/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "models/Qwen/Qwen3.5-2B",
    "prompt": [
      "请用一句话解释 vLLM 的作用。",
      "请说明 gpu-memory-utilization 参数的含义。",
      "请说明 tensor-parallel-size=1 代表什么。"
    ],
    "max_tokens": 64,
    "temperature": 0.7
  }' | jq
```

这类方式的特点是：

1. 客户端提前准备好多条 prompt
2. 一次 HTTP 请求直接提交给服务端
3. 更适合批处理风格任务

## 2. 动态 batch 示例

动态 batch 不是一个请求带多个 prompt，而是多个请求几乎同时发到服务端，由 `vLLM` 自动做 continuous batching。

下面是 Python 并发请求示例：

```python
import asyncio
from openai import AsyncOpenAI

client = AsyncOpenAI(
    base_url="http://127.0.0.1:8000/v1",
    api_key="EMPTY",
)

PROMPTS = [
    "请用一句话说明 vLLM 的核心作用。",
    "请说明 max_model_len 为什么会影响显存。",
    "请说明 tensor-parallel-size=1 的含义。",
    "请说明 prefix caching 适合什么场景。",
]

async def ask(prompt: str) -> None:
    response = await client.chat.completions.create(
        model="models/Qwen/Qwen3.5-2B",
        messages=[
            {"role": "system", "content": "You are a concise assistant."},
            {"role": "user", "content": prompt},
        ],
        max_tokens=64,
        temperature=0.7,
    )
    print(f"=== Prompt ===\n{prompt}")
    print(f"=== Answer ===\n{response.choices[0].message.content}\n")

async def main() -> None:
    await asyncio.gather(*(ask(prompt) for prompt in PROMPTS))

if __name__ == "__main__":
    asyncio.run(main())
```

这类方式的特点是：

1. 每个请求彼此独立
2. 服务端自动聚合调度
3. 更贴近真实在线服务场景

## 静态 batch 和动态 batch 的区别

静态 batch：

1. 一次请求里带多个 prompt
2. 更适合脚本批处理

动态 batch：

1. 多个请求分别发送
2. 服务端自动合批
3. 更适合在线服务

## 最终结论

同一个模型在同一时间可以处理多个 prompt。

在 `vLLM` 在线部署里：

1. 静态 batch 更像客户端主动组批
2. 动态 batch 更像服务端自动做 continuous batching
3. 真正更有代表性的在线服务能力通常是动态 batch

---

# 场景问题：`vllm bench serve` 怎么用？如何同时观察显存占用？

问题：

我已经用 `vllm serve` 启动了在线服务。现在我想测试推理性能，重点关注：

1. 首 token 延迟 `TTFT`
2. 平均 token 延迟 `TPOT`
3. 总延迟 `E2EL`
4. 推理过程中显存变化

这种情况下，`vllm bench serve` 应该怎么用？同时又该如何监控显存？

答案：

`vllm bench serve` 是 `vLLM` 自带的在线服务压测工具，用来对已经启动的服务发请求，并统计在线推理性能指标。

它最适合做的事情是：

1. 压测 `/v1/completions` 或 `/v1/chat/completions`
2. 统计 `TTFT`
3. 统计 `TPOT`
4. 统计 `ITL`
5. 统计 `E2EL`

但它本身不是 GPU 监控工具。

所以更实用的组合是：

1. 用 `vllm bench serve` 看推理性能指标
2. 用 `nvidia-smi` 实时看显存占用

## 1. 先启动在线服务

```bash
vllm serve models/Qwen/Qwen3.5-2B \
  --host 0.0.0.0 \
  --port 8000 \
  --tensor-parallel-size 1 \
  --gpu-memory-utilization 0.80 \
  --max-model-len 4096
```

## 2. 最简单的 `vllm bench serve` 示例

如果你要压测 OpenAI-compatible 聊天接口，可以这样跑：

```bash
vllm bench serve \
  --backend openai-chat \
  --base-url http://127.0.0.1:8000 \
  --endpoint /v1/chat/completions \
  --model models/Qwen/Qwen3.5-2B \
  --dataset-name random \
  --num-prompts 100 \
  --input-len 128 \
  --output-len 64
```

这条命令的作用是：

1. `--backend openai-chat`：压测聊天接口
2. `--base-url`：指向本地 `vLLM` 服务
3. `--endpoint /v1/chat/completions`：指定接口路径
4. `--model`：指定模型 id
5. `--dataset-name random`：使用随机请求集
6. `--num-prompts 100`：发出 100 个请求
7. `--input-len 128`：输入长度约 128 token
8. `--output-len 64`：输出长度约 64 token

## 3. 更适合性能分析的示例

如果你希望显式观察常见延迟指标，并保存结果，建议这样跑：

```bash
vllm bench serve \
  --backend openai-chat \
  --base-url http://127.0.0.1:8000 \
  --endpoint /v1/chat/completions \
  --model models/Qwen/Qwen3.5-2B \
  --dataset-name random \
  --num-prompts 100 \
  --input-len 128 \
  --output-len 64 \
  --percentile-metrics ttft,tpot,itl,e2el \
  --metric-percentiles 50,95,99 \
  --save-result \
  --save-detailed
```

这条命令会：

1. 输出 `TTFT / TPOT / ITL / E2EL`
2. 给出 `P50 / P95 / P99`
3. 保存 benchmark 结果
4. 保存更详细的请求级信息

## 4. 如果模型会输出 `<think>`，如何避免干扰 benchmark

如果你测的是 Qwen 之类的聊天模型，建议显式关闭 thinking 输出：

```bash
vllm bench serve \
  --backend openai-chat \
  --base-url http://127.0.0.1:8000 \
  --endpoint /v1/chat/completions \
  --model models/Qwen/Qwen3.5-2B \
  --dataset-name random \
  --num-prompts 100 \
  --input-len 128 \
  --output-len 64 \
  --extra-body '{"chat_template_kwargs":{"enable_thinking":false}}' \
  --percentile-metrics ttft,tpot,itl,e2el \
  --metric-percentiles 50,95,99 \
  --save-result \
  --save-detailed
```

这样更容易看到真实生成性能，而不会被 `<think>` 片段污染结果。

## 5. 显存检测策略

`vllm bench serve` 负责测请求性能，不负责给你实时 GPU 显存曲线。

所以显存检测要单独做。

最直接的策略是：

### 策略 A：边压测边开一个终端看 `nvidia-smi`

```bash
watch -n 0.5 nvidia-smi
```

这适合：

1. 本地学习
2. 快速观察显存变化
3. 看多个 `vLLM` 实例是否在抢显存

重点看：

1. 显存占用是否接近上限
2. benchmark 过程中是否出现明显峰值
3. 是否有多个进程同时占用同一张 GPU

### 策略 B：基线、压测中、压测后三次对比

你也可以更朴素地做三次采样：

1. 服务刚启动后看一次 `nvidia-smi`
2. benchmark 运行中看一次
3. benchmark 结束后再看一次

这种方式虽然不够连续，但足够回答：

1. 空载显存是多少
2. 压测时峰值大概能到哪里
3. benchmark 结束后显存是否回落正常

### 策略 C：长期监控用 `DCGM Exporter`

如果你不是做一次性实验，而是想长期看：

1. GPU 显存
2. GPU 利用率
3. 功耗
4. 温度

那更适合的方案是：

1. `DCGM Exporter`
2. `Prometheus`
3. `Grafana`

这套更偏生产监控，不是最轻量的本地实验方案。

## 6. 最实用的组合

对当前仓库最实用的方式就是：

一个终端启动服务：

```bash
vllm serve models/Qwen/Qwen3.5-2B \
  --host 0.0.0.0 \
  --port 8000 \
  --tensor-parallel-size 1 \
  --gpu-memory-utilization 0.80 \
  --max-model-len 4096
```

第二个终端跑 benchmark：

```bash
vllm bench serve \
  --backend openai-chat \
  --base-url http://127.0.0.1:8000 \
  --endpoint /v1/chat/completions \
  --model models/Qwen/Qwen3.5-2B \
  --dataset-name random \
  --num-prompts 50 \
  --input-len 128 \
  --output-len 64 \
  --extra-body '{"chat_template_kwargs":{"enable_thinking":false}}' \
  --percentile-metrics ttft,tpot,itl,e2el \
  --metric-percentiles 50,95,99 \
  --save-result \
  --save-detailed
```

第三个终端实时看显存：

```bash
watch -n 0.5 nvidia-smi
```

## 最终结论

`vllm bench serve` 最适合看：

1. `TTFT`
2. `TPOT`
3. `ITL`
4. `E2EL`

而显存监控最直接的策略是：

1. benchmark 跑起来
2. 同时开 `watch -n 0.5 nvidia-smi`
3. 结合 benchmark 输出和显存变化一起判断服务是否稳定

---

# 场景问题：单卡放不下大模型时，vLLM 如何做多卡部署？

问题：

如果一个大模型单卡已经放不下了，`vLLM` 应该如何做多卡部署？请分别讨论两种情况：

1. 多张卡的显存规格一样
2. 多张卡的显存规格不一样

答案：

当单卡放不下模型时，`vLLM` 的主流做法是多卡部署。

工程上可以直接记住这个判断：

1. 同规格多卡：优先 `tensor parallel`
2. 异构显存多卡：优先保守评估，更适合考虑 `pipeline parallel`

## 1. 多卡显存规格一样

这是最标准、最推荐的场景。

### 结论

优先使用：

1. `tensor parallel`

因为这种情况下模型切分最均匀，部署方式也最直接。

### 示例 1：两张同规格 GPU 部署一个单卡放不下的模型

```bash
CUDA_VISIBLE_DEVICES=0,1 vllm serve /path/to/model \
  --host 0.0.0.0 \
  --port 8000 \
  --tensor-parallel-size 2 \
  --gpu-memory-utilization 0.85 \
  --max-model-len 4096
```

说明：

1. `CUDA_VISIBLE_DEVICES=0,1` 表示使用两张卡
2. `--tensor-parallel-size 2` 表示模型切到两张 GPU
3. `--gpu-memory-utilization 0.85` 表示每张卡给 vLLM 的显存预算
4. `--max-model-len 4096` 先用保守上下文，避免 KV Cache 过大

### 示例 2：四张同规格 GPU 部署更大的模型

```bash
CUDA_VISIBLE_DEVICES=0,1,2,3 vllm serve /path/to/model \
  --host 0.0.0.0 \
  --port 8000 \
  --tensor-parallel-size 4 \
  --gpu-memory-utilization 0.85 \
  --max-model-len 4096
```

这类方式适合：

1. 同一台机器
2. GPU 型号和显存规格一致
3. 你要的是最直接的单机多卡部署方式

## 2. 多卡显存规格不一样

这个场景要谨慎很多。

### 结论

不要默认异构显存 GPU 适合直接做：

1. `tensor parallel`

因为在这类方案下，常见问题是：

1. 小显存卡先爆掉
2. 负载不均衡
3. 整体可用上限被最小显存卡限制

### 更保守的工程建议

优先考虑：

1. `pipeline parallel`
2. 按最小显存卡做预算
3. `gpu-memory-utilization` 设得更保守
4. `max-model-len` 先压低

### 示例 3：两张显存不一样的 GPU，先尝试 pipeline parallel

假设：

1. `GPU 0` 是 48G
2. `GPU 1` 是 24G

更保守的启动方式：

```bash
CUDA_VISIBLE_DEVICES=0,1 vllm serve /path/to/model \
  --host 0.0.0.0 \
  --port 8000 \
  --tensor-parallel-size 1 \
  --pipeline-parallel-size 2 \
  --gpu-memory-utilization 0.75 \
  --max-model-len 4096
```

说明：

1. `--tensor-parallel-size 1` 表示不做张量切分
2. `--pipeline-parallel-size 2` 表示按层把模型拆到两张卡
3. `--gpu-memory-utilization 0.75` 先保守，避免小卡先 OOM
4. `--max-model-len 4096` 降低 KV Cache 压力

### 示例 4：四张异构显存 GPU，更保守的单机多卡尝试

假设：

1. `GPU 0`、`GPU 1` 是 48G
2. `GPU 2`、`GPU 3` 是 24G

可以先这样尝试：

```bash
CUDA_VISIBLE_DEVICES=0,1,2,3 vllm serve /path/to/model \
  --host 0.0.0.0 \
  --port 8000 \
  --tensor-parallel-size 1 \
  --pipeline-parallel-size 4 \
  --gpu-memory-utilization 0.70 \
  --max-model-len 4096
```

这类场景下你要默认：

1. 整体稳定性受最小显存卡限制
2. 不能按“总显存简单相加”去理解
3. 真正能不能跑稳，要靠实测

## 3. 同规格和异构显存的根本区别

同规格显卡：

1. 更适合 `tensor parallel`
2. 切分更均匀
3. 更容易预测结果

异构显卡：

1. 不适合默认按标准 `tensor parallel` 理解
2. 更容易被小显存卡限制
3. 更适合保守尝试 `pipeline parallel`

## 4. 多卡部署时的最实用排查顺序

不管同构还是异构，都按这个顺序排：

1. 先确认所有目标 GPU 都可见
2. 再确认模型是否单卡确实放不下
3. 再决定是 `tensor parallel` 还是 `pipeline parallel`
4. 先用保守的 `gpu-memory-utilization`
5. 先用保守的 `max-model-len`
6. 服务启动成功后，再做请求压测

## 5. 最终结论

可以直接记成一句话：

当单卡放不下大模型时，`vLLM` 的标准多卡主路线是：

1. 同规格显卡优先 `tensor parallel`
2. 显存规格不一样时，不要默认直接做 `tensor parallel`，更适合保守尝试 `pipeline parallel`
