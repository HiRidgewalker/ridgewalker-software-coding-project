# 新增任务的固定流程

模板把变化限制在参数、业务函数、Task 包装和入口配置中。不要在业务函数里导入 Celery、
FastAPI、RabbitMQ 连接或 Supervisor 信息。

## 新增异步任务

1. 在 `src/model/task_model.py` 新增 Pydantic 参数模型，并设置 `extra="forbid"`。
2. 在 `src/service/` 新增普通业务函数。该函数应可直接进行单元测试，并保证幂等。
3. 在 `src/task/async_task.py` 新增 Task 薄包装：
   - 名称使用 `app.tasks.async.<task_name>`；
   - 参数统一命名为 `raw_payload`；
   - 先用 Pydantic 校验，再调用业务函数；
   - 仅对 `RetryableTaskError` 自动重试；
   - 使用 `LoggedTask` 和 `acks_late=True`。
4. FastAPI 路由调用 `publish_task(task, payload)`，异步路由使用
   `await asyncio.to_thread(...)`，避免 RabbitMQ 网络 I/O 阻塞事件循环。
5. 添加模型、业务函数、Task 和 API 测试。

复用 `app.tasks.async.*` 前缀时，路由会自动进入 `celery.async.queue`，不需要修改拓扑、
Celery imports 或 Supervisor。若新建 Task 模块，才需要把模块加入
`src/client/celery_config.py` 的 `TASK_IMPORTS`。

Task 的标准形状：

```python
@celery_app.task(
    bind=True,
    base=LoggedTask,
    name="app.tasks.async.generate_file",
    autoretry_for=(RetryableTaskError,),
    retry_backoff=True,
    retry_backoff_max=600,
    retry_jitter=True,
    max_retries=5,
    acks_late=True,
)
def generate_file_task(self: LoggedTask, raw_payload: dict[str, object]) -> None:
    payload = GenerateFilePayload.model_validate(raw_payload)
    generate_file(payload)
```

不要使用 `autoretry_for=(Exception,)`。参数错误、权限拒绝和程序缺陷都不应反复重试。
开启 `acks_late` 后任务可能重复执行，因此数据库写入、外部调用等必须用业务唯一键、唯一
约束或状态条件更新保证幂等。

## 新增定时任务

1. 在 `src/service/` 新增普通、幂等的业务函数。
2. 在 `src/task/scheduled_task.py` 新增薄包装，名称使用
   `app.tasks.scheduled.<task_name>`。
3. 在 `src/client/celery_config.py` 的 `BEAT_SCHEDULE` 中新增调度项，目标队列固定为
   `celery.scheduled.queue`，routing key 固定为 `celery.scheduled`。
4. 添加业务、Task 和调度配置测试，然后重启唯一的 Celery Beat。

Beat 只负责按时发布消息，任务由 scheduled Worker 执行。如果任务执行时间可能超过调度
间隔，应在业务层用数据库锁、唯一运行记录或时间窗口幂等键防止重叠。

## 新增独立队列

只有任务需要独立并发、资源或故障隔离时才新建队列：

1. 在 `src/client/celery_config.py` 添加队列常量、`Queue` 和任务路由。
2. 执行 `uv run python -m src.client.celery_topology` 声明新拓扑。
3. 在 `supervisor/programs/` 新增只监听该队列的 Worker 配置和独立日志。
4. 添加配置测试，并更新启动文档。

不要在 Task、业务函数或路由中直接声明 exchange/queue/binding，也不要通过
`apply_async(queue="临时队列")` 绕过集中配置。
