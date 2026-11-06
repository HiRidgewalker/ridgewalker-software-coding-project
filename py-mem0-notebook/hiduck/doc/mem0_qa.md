# Mem0 Cloud 核心问答

> 适用于 Mem0 Cloud v3。Mem0 是长期记忆层，不是完整聊天记录系统。

## 1. 是否需要把所有对话交给 Mem0？

Mem0 只能处理应用主动传给 `client.add()` 的内容。常规流程是：

1. 收到用户问题后，调用 `client.search()` 检索相关记忆。
2. 将记忆与当前会话上下文一起交给 Agent。
3. Agent 回答后，将有记忆价值的本轮对话交给 `client.add()`。

默认 `infer=True` 时，Mem0 会从对话中提取长期有效的事实、偏好、目标、计划、决定和事件，不会原样保存每句话。没有记忆价值的普通问答可能不产生记忆。

`infer=False` 会跳过提炼并保存原文，但不应因此把 Mem0 当作聊天记录库。需要完整回放、审计或按时间查找原始问题时，应使用业务数据库保存聊天记录。

## 2. Mem0 如何提炼记忆？

Mem0 Cloud v3 使用单次 LLM 调用执行 `ADD-only` 提炼：

1. 接收新对话并查找相关旧记忆，辅助理解和避免重复。
2. 从新对话中提取互相独立、值得长期保存的事实。
3. 对结果去重、生成向量，并补充时间、分类、元数据和实体关联。
4. 将每个事实作为独立记忆保存。

例如，对话中同时出现“项目使用 FastAPI”“数据库使用 PostgreSQL”“依赖由 uv 管理”，通常会拆成三条记忆，而不是生成一段宽泛的会话摘要。

v3 只新增记忆，不自动覆盖或删除旧记忆。事实发生变化时，新旧状态可以同时保留，由时间和相关性检索决定优先返回哪一条。网上常见的 `ADD/UPDATE/DELETE` 判定流程属于旧版机制。

## 3. Mem0 能否回答“昨天问过什么”？

Mem0 Cloud v3 默认支持时间推理，可以理解“昨天”“上周”“当前”和“截至某个日期”等表达。

- `created_at` 表示记忆在 Mem0 中的创建时间。
- `updated_at` 表示记忆的最后更新时间。
- `timestamp` 可在补录历史内容时指定真实发生时间。
- `reference_date` 可为检索中的相对时间表达指定参照时间。

Mem0 只能召回已经被提炼并保存的记忆，不能保证还原某个时间段的全部问题。`history()` 记录的是单条记忆的变化历史，也不是完整聊天历史。

## 4. 同一用户的不同项目如何隔离？

各作用域的职责如下：

| 字段 | 适用范围 |
| --- | --- |
| `user_id` | 持久用户或账号 |
| `agent_id` | 不同 Agent 或 Agent 角色 |
| `app_id` | 不同应用、产品或产品入口 |
| `run_id` | 短期会话、任务或聊天线程 |
| `metadata` | 业务项目、团队和业务分类 |

同一用户处理多个代码项目时，建议保持稳定的 `user_id`，并用 `metadata.business_project_id` 标识业务项目：

```python
client.add(
    messages=messages,
    user_id="alice",
    metadata={"business_project_id": "order-service"},
)

memories = client.search(
    query="当前项目的技术栈和注意事项是什么？",
    filters={
        "AND": [
            {"user_id": "alice"},
            {"metadata": {"business_project_id": "order-service"}},
        ]
    },
)
```

如果一个业务项目本身就是独立应用，也可以映射为 `app_id`。`run_id` 只适合短期会话，不应充当长期项目标识。

过滤条件决定隔离边界：

- 同时过滤 `user_id` 和业务项目时，只检索该项目的记忆。
- 只过滤 `user_id` 时，该用户同一作用域内的不同项目记忆可能共同参与检索。
- `metadata` 和 `categories` 只是标签，只有加入 `filters` 后才形成检索约束。
- 用户全局偏好与项目级记忆需要共同使用时，应分别检索后由应用合并，不要通过省略项目过滤来实现。

管理员还可以在同一 Organization 下创建多个 Mem0 Cloud Project。不同 Cloud Project 的记忆、配置和成员权限相互隔离，即使使用相同的 `user_id` 也不会串库。普通业务项目优先使用 `metadata`；只有客户、团队、环境或权限必须独立时，才拆分 Cloud Project。

## 5. 调用方是否需要选择检索算法？

不需要。调用方只需调用 `client.search()`；Mem0 Cloud v3 会在服务端组合语义向量、BM25 关键词和实体匹配，并融合得分后返回结果。调用方不能也无需选择稠密向量、稀疏向量或底层索引。

调用方仍须明确业务检索范围：

- `filters`：指定用户、项目、时间和分类等硬约束，至少包含一个实体标识。
- `top_k`：控制返回数量，默认是 `10`。
- `threshold`：控制最低相关性，v3 默认是 `0.1`。
- `rerank`：是否启用托管重排，启用后会增加延迟。

`client.search()` 用于相关性检索；`client.get_all()` 只按条件列出记忆，不执行语义排序。Mem0 返回多条独立记忆，由应用决定如何放入 Agent 上下文并综合回答。

`filters` 不只有四个实体标识：

- `user_id`、`agent_id`、`app_id`、`run_id` 是实体作用域。
- `created_at`、`updated_at`、`timestamp`、`categories`、`keywords`、`memory_ids` 是 Mem0 系统字段。
- 业务项目、环境、渠道、文档编号等自定义字段放入 `metadata`。

## 6. 流式回答如何写入记忆？

不要按 token 或 chunk 调用 `add()`。服务端应一边向客户端转发文本增量，一边累积完整回答；流正常结束后，再将本轮 `user + assistant` 消息一次性提交给 Mem0。

流被取消或生成失败时，通常不要把残缺回答当作完整事实写入。只保存用户可见文本，不保存隐藏推理、SSE 控制事件或工具调用增量。Cloud v3 的提炼是异步的，刚提交的记忆可能无法立即检索，因此连续对话仍应保留当前会话上下文。

## 7. 是否支持图片、文档和语音？

Mem0 Cloud 原生支持图片和文档：图片可通过 URL 或 Base64 提交，文档支持 MDX、TXT 和 PDF。Mem0 会提取其中的文字和关键信息，再形成标准文本记忆。

语音通常先由 ASR 或语音模型转写，再把转写文本和 Agent 的完整文本回答交给 Mem0。原始图片、音频和文档仍应保存在对象存储中，Mem0 只保存提炼出的语义及必要的文件地址元数据。

## 8. Mem0 有哪些记忆类型？

“记忆类型”需要按三个维度理解：

- 生命周期包括当前对话、会话、用户长期记忆和组织共享记忆。
- 内容包括事实记忆、情景记忆和语义关系记忆；工作记忆属于临时上下文。
- API 作用域包括 `user_id`、`agent_id`、`app_id` 和 `run_id`，它们负责归属和隔离，不是内容类型。

Mem0 Cloud 默认不会为每条记忆提供固定的 `factual`、`episodic` 或 `semantic` 类型字段。业务需要严格区分时，应自行写入 `metadata.memory_type` 并在检索时过滤。

## 9. 是否支持中文？

支持。Mem0 Cloud 可以接收中文对话、提炼中文记忆并使用中文查询。建议在 Project 级开启 `multilingual=True`，让记忆沿用输入语言；中文记忆使用中文查询通常最稳定。

该配置不会自动翻译或重新提炼已有记忆，存量内容需要根据实际效果决定是否重新导入。

## 10. `custom_instructions` 和 `custom_categories` 有什么作用？

两者都是 Project 级的写入配置，对该 Project 下后续所有用户生效，通常只在初始化或管理配置变更时调用：

- `custom_instructions` 是提炼阶段的软规则，告诉 LLM 应提取或忽略什么。
- `custom_categories` 会替换默认分类目录，Mem0 从中为新记忆自动选择标签。

它们不是检索条件。检索时的硬隔离仍由 `client.search(filters=...)` 决定。提炼规则与分类目录应保持一致，例如要求提取 `progress` 时，也应提供对应的 `progress` 分类。

## 接入原则

1. 使用稳定的 `user_id`，不要把用户与项目拼成新的用户标识。
2. 每次写入和检索都携带一致的项目作用域。
3. 不依赖语义相似度实现用户或项目隔离，隔离必须使用 `filters`。
4. Mem0 保存长期记忆，业务数据库保存完整聊天记录。
5. 流式回答完成后一次性写入，禁止按 chunk 提炼记忆。
6. 调用方决定“查谁、查哪个项目、查什么”，Mem0 决定“如何检索和排序”。

## 官方资料

- [Add Memories](https://docs.mem0.ai/api-reference/memory/add-memories)
- [Search Memories](https://docs.mem0.ai/api-reference/memory/search-memories)
- [Temporal Reasoning](https://docs.mem0.ai/platform/features/temporal-reasoning)
- [Entity-Scoped Memory](https://docs.mem0.ai/platform/features/entity-scoped-memory)
- [Organizations & Projects](https://docs.mem0.ai/api-reference/organizations-projects)
- [Multimodal Support](https://docs.mem0.ai/platform/features/multimodal-support)
- [Memory Types](https://docs.mem0.ai/core-concepts/memory-types)
- [Custom Instructions](https://docs.mem0.ai/platform/features/custom-instructions)
- [Custom Categories](https://docs.mem0.ai/platform/features/custom-categories)
