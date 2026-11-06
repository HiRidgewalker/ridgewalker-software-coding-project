# Celery 路由、异步任务和定时任务执行流程总结

本文总结当前项目中 Celery 的几个关键点：

- `TASK_ROUTES` 到底控制什么。
- API 触发的异步任务如何发布和消费。
- `process_message_task` 为什么既用于发布，也用于 Worker 执行。
- Worker 调用任务函数时，`self` 和 `raw_payload` 分别是什么。
- 定时任务如何由 Celery Beat 发布到指定队列。

## 一、`TASK_ROUTES` 的作用

当前项目在 `src/client/celery_config.py` 中定义了任务路由：

```python
TASK_ROUTES = {
    "app.tasks.async.*": {
        "queue": ASYNC_QUEUE_NAME,
        "routing_key": ASYNC_ROUTING_KEY,
    },
    "app.tasks.scheduled.*": {
        "queue": SCHEDULED_QUEUE_NAME,
        "routing_key": SCHEDULED_ROUTING_KEY,
    },
}
```

它是“任务发布时的入队路由配置”，不是 Worker 的消费配置。

当代码调用 `apply_async()` 发布任务时，Celery 会根据任务名称匹配 `TASK_ROUTES`，决定消息应该进入哪个 RabbitMQ 队列，以及使用哪个 routing key。

例如当前异步任务名是：

```python
name="app.tasks.async.process_message"
```

它会匹配：

```python
"app.tasks.async.*"
```

因此消息会进入：

```text
queue: celery.async.queue
routing_key: celery.async
```

Worker 消费哪个队列，不由 `TASK_ROUTES` 决定，而由 Worker 启动参数决定：

```bash
uv run celery -A src.client.celery_config:celery_app worker \
  --queues=celery.async.queue \
  --loglevel=INFO
```

可以这样区分：

```text
TASK_ROUTES
  决定任务发布时进入哪个队列

worker --queues=...
  决定 Worker 监听和消费哪个队列

Task name
  决定 Worker 收到消息后执行哪个 Python Task 函数
```

## 二、API 触发的是异步任务，不是定时任务

当前 API 入口在 `src/controller/api.py`：

```python
@router.post(
    "/tasks/messages",
    response_model=TaskAcceptedResponse,
    status_code=status.HTTP_202_ACCEPTED,
    tags=["tasks"],
)
async def enqueue_message(payload: MessageTaskPayload) -> TaskAcceptedResponse:
    task_id = await asyncio.to_thread(publish_task, process_message_task, payload)
    return TaskAcceptedResponse(task_id=task_id)
```

`enqueue_message()` 是 API 触发的异步任务入口。

它不是定时任务入口。定时任务入口在：

```text
src/client/celery_config.py
```

你在 `enqueue_message()` 中没有看到 `routing_key`，是因为 API 代码没有手动指定队列和 routing key，而是把这件事交给 Celery 的 `TASK_ROUTES` 处理。

当前发布链路是：

```text
src/controller/api.py::enqueue_message()
  -> src/client/celery_publisher.py::publish_task()
  -> process_message_task.apply_async(...)
  -> Celery 根据 process_message_task.name 匹配 TASK_ROUTES
  -> RabbitMQ
  -> celery.async.queue
```

## 三、`process_message_task` 在发布和消费阶段的不同角色

当前异步任务定义在 `src/task/async_task.py`：

```python
@celery_app.task(
    bind=True,
    base=LoggedTask,
    name="app.tasks.async.process_message",
    autoretry_for=(RetryableTaskError,),
    retry_backoff=True,
    retry_backoff_max=600,
    retry_jitter=True,
    max_retries=5,
    acks_late=True,
)
def process_message_task(self: LoggedTask, raw_payload: dict[str, Any]) -> None:
    payload = MessageTaskPayload.model_validate(raw_payload)
    process_message(payload)
```

`process_message_task` 是同一个 Celery Task 定义，但在两个阶段的角色不同。

发布阶段，它在 API 进程中作为“任务发布句柄”使用：

```python
process_message_task.apply_async(...)
```

这一步不会执行函数体，只会向 RabbitMQ 发布一条消息。

消费阶段，它在 Worker 进程中作为“任务处理函数”使用：

```python
process_message_task(self, raw_payload)
```

这一步才会真正执行函数体：

```python
payload = MessageTaskPayload.model_validate(raw_payload)
process_message(payload)
```

完整关系是：

```text
API 进程
  -> 调用 process_message_task.apply_async(...)
  -> 发布消息到 RabbitMQ

Worker 进程
  -> 从 celery.async.queue 消费消息
  -> 根据 task name 找到 process_message_task
  -> 执行 process_message_task 函数体
```

因此，`process_message_task` 既是发布时使用的 Task 对象，也是 Worker 端最终执行的 Task 函数。

## 四、Worker 调用任务函数时注入了什么

任务函数签名是：

```python
def process_message_task(self: LoggedTask, raw_payload: dict[str, Any]) -> None:
```

### 1. `self` 是 Celery 注入的当前任务实例

因为任务定义里写了：

```python
bind=True
```

所以 Celery 执行任务时，会把当前 Task 实例作为第一个参数传入。

`self` 里主要是任务运行时上下文，例如：

```python
self.name
self.request.id
self.request.retries
self.request.delivery_info
self.request.args
self.request.kwargs
```

当前项目主要用它记录日志：

```python
logger.info(
    "任务开始：任务名称=%s，任务标识=%s",
    self.name,
    self.request.id,
)
```

其中：

- `self.name` 是任务名称，例如 `app.tasks.async.process_message`。
- `self.request.id` 是当前任务 ID，也就是 API 返回的 `task_id`。

### 2. `raw_payload` 是发布任务时传入的业务参数

API 收到请求：

```json
{
  "message": "hello celery"
}
```

FastAPI 先解析成 Pydantic 模型：

```python
MessageTaskPayload(message="hello celery")
```

然后 `publish_task()` 发布任务：

```python
task.apply_async(
    kwargs={"raw_payload": payload.model_dump(mode="json")},
)
```

RabbitMQ 消息中保存的 kwargs 类似：

```python
{
    "raw_payload": {
        "message": "hello celery"
    }
}
```

Worker 消费后，Celery 按 kwargs 名字调用任务函数：

```python
process_message_task(
    self=<当前 Celery Task 实例>,
    raw_payload={"message": "hello celery"},
)
```

所以：

```text
self
  是 Celery 任务运行上下文

raw_payload
  是业务入参
```

## 五、是否可以从 `self` 中取 payload

技术上可以。

因为发布任务时传了：

```python
kwargs={"raw_payload": {...}}
```

Worker 执行时，Celery 会把这些 kwargs 放到：

```python
self.request.kwargs
```

所以可以拿到：

```python
raw_payload = self.request.kwargs["raw_payload"]
```

但当前项目不建议这样写。

推荐保留显式参数：

```python
def process_message_task(self: LoggedTask, raw_payload: dict[str, Any]) -> None:
```

原因：

- 函数签名能直接说明任务需要哪些业务参数。
- 发布参数和消费参数一一对应。
- 测试时可以直接传 `kwargs={"raw_payload": ...}`。
- 不依赖 `self.request.kwargs` 这种运行时上下文细节。
- 后续维护者更容易理解任务入参契约。

更准确的职责划分是：

```text
self
  用于任务元信息：task_id、任务名、重试次数、投递信息等

raw_payload
  用于业务数据
```

## 六、定时任务如何发布到对应队列

定时任务不是由 API 发布，而是由 Celery Beat 发布。

当前项目的定时任务配置在 `src/client/celery_config.py`：

```python
BEAT_SCHEDULE = {
    "example-heartbeat-every-minute": {
        "task": "app.tasks.scheduled.heartbeat",
        "schedule": crontab(minute="*"),
        "options": {
            "queue": SCHEDULED_QUEUE_NAME,
            "routing_key": SCHEDULED_ROUTING_KEY,
        },
    },
}
```

这里的含义是：

- `task`：Beat 到时间后要发布哪个 Celery Task。
- `schedule`：什么时候触发。
- `options.queue`：发布到哪个队列。
- `options.routing_key`：使用哪个 routing key。

当前值对应：

```text
task: app.tasks.scheduled.heartbeat
queue: celery.scheduled.queue
routing_key: celery.scheduled
```

Celery Beat 每分钟做的事情可以理解为：

```python
celery_app.send_task(
    "app.tasks.scheduled.heartbeat",
    queue="celery.scheduled.queue",
    routing_key="celery.scheduled",
)
```

然后 RabbitMQ 把消息路由到：

```text
celery.scheduled.queue
```

监听该队列的 Worker 会消费并执行：

```python
@celery_app.task(
    bind=True,
    base=LoggedTask,
    name="app.tasks.scheduled.heartbeat",
    acks_late=True,
)
def heartbeat_task(self: LoggedTask) -> None:
    executed_at = datetime.now(timezone.utc)
    record_heartbeat(executed_at)
```

完整链路是：

```text
Celery Beat
  -> 读取 BEAT_SCHEDULE
  -> 到达 crontab 时间
  -> 发布 app.tasks.scheduled.heartbeat
  -> 使用 queue=celery.scheduled.queue
  -> 使用 routing_key=celery.scheduled
  -> RabbitMQ
  -> scheduled Worker 消费 celery.scheduled.queue
  -> Worker 执行 heartbeat_task
```

## 七、定时任务是否必须携带业务内容

不必须。

当前项目的心跳任务没有携带业务 payload。Beat 每次触发时只携带：

```text
要执行哪个 task
什么时候触发
投递到哪个 queue
使用哪个 routing_key
```

具体业务内容由 Task 函数体自己生成或查询：

```python
def heartbeat_task(self: LoggedTask) -> None:
    executed_at = datetime.now(timezone.utc)
    record_heartbeat(executed_at)
```

这种方式适合：

- 清理过期数据。
- 同步外部数据。
- 生成日报、月报。
- 扫描数据库中待处理记录。
- 根据当前时间窗口执行维护任务。

如果确实需要，Beat 也可以携带固定参数：

```python
BEAT_SCHEDULE = {
    "daily-report": {
        "task": "app.tasks.scheduled.generate_report",
        "schedule": crontab(hour=3, minute=0),
        "kwargs": {
            "raw_payload": {
                "report_type": "daily"
            }
        },
        "options": {
            "queue": SCHEDULED_QUEUE_NAME,
            "routing_key": SCHEDULED_ROUTING_KEY,
        },
    },
}
```

对应 Task 可以写成：

```python
@celery_app.task(
    bind=True,
    base=LoggedTask,
    name="app.tasks.scheduled.generate_report",
    acks_late=True,
)
def generate_report_task(self: LoggedTask, raw_payload: dict[str, object]) -> None:
    payload = GenerateReportPayload.model_validate(raw_payload)
    generate_report(payload)
```

但在多数定时任务场景下，更推荐：

```text
Beat 只负责按时间触发
Task 函数体根据当前时间、数据库状态或业务规则决定处理内容
```

这样调度配置更稳定，业务逻辑也更集中。

## 八、核心结论

1. `TASK_ROUTES` 是发布任务时的入队路由配置，不是 Worker 消费配置。
2. Worker 消费哪个队列由启动参数 `--queues=...` 决定。
3. `src/controller/api.py::enqueue_message()` 是 API 异步任务入口，不是定时任务入口。
4. API 发布任务时没有手写 routing key，是因为 Celery 根据 Task 名称自动匹配 `TASK_ROUTES`。
5. `process_message_task.apply_async(...)` 只是发布消息，不执行函数体。
6. Worker 消费到消息后，才真正执行 `process_message_task(...)` 函数体。
7. `self` 是 Celery 注入的任务上下文，`raw_payload` 是业务入参。
8. 可以从 `self.request.kwargs` 取 payload，但不建议这样做；显式参数更清晰。
9. 定时任务由 Celery Beat 根据 `BEAT_SCHEDULE` 发布。
10. 定时任务可以不携带业务 payload，具体处理内容由 Worker 的 Task 函数体实现。
