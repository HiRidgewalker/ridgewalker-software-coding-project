# 当前项目如何搭配 Celery 使用

本文说明当前 FastAPI + Celery + RabbitMQ 项目的实际使用方式。目标是让后续开发者知道：

- 本项目里 Celery 承担什么职责。
- 本地如何启动完整消息流。
- API 如何发布异步任务。
- Celery Beat 如何发布定时任务。
- 新增任务时应该改哪些文件，以及哪些做法需要避免。

## 一、整体定位

当前项目已经接入 Celery，不需要重新设计消息队列结构。

Celery 在本项目中只负责“任务发布、任务路由、Worker 执行和定时调度”。业务逻辑仍然放在普通 Python 函数中，不直接依赖 Celery、FastAPI、RabbitMQ 或 Supervisor。

核心链路如下：

```text
FastAPI 路由
  -> src/client/celery_publisher.py
  -> src/task/async_task.py 中的 Celery Task
  -> RabbitMQ
  -> Celery Worker
  -> src/service/ 中的普通业务函数
```

定时任务链路如下：

```text
Celery Beat
  -> RabbitMQ
  -> celery.scheduled.queue
  -> Celery scheduled Worker
  -> src/task/scheduled_task.py
  -> src/service/ 中的普通业务函数
```

本项目目前没有配置 Celery result backend。API 返回的 `task_id` 主要用于日志关联，不用于通过 `AsyncResult` 查询任务状态。

## 二、Celery 相关文件职责

| 文件 | 职责 |
| --- | --- |
| `src/client/celery_config.py` | 集中加载环境配置，创建唯一的 `celery_app`，并定义队列、路由、任务导入和 Beat 计划。 |
| `src/client/celery_topology.py` | 主动声明 RabbitMQ 中需要的 exchange、queue 和 binding。 |
| `src/client/celery_publisher.py` | FastAPI 侧统一发布异步任务。 |
| `src/task/base_task.py` | 提供带日志钩子的 Celery Task 基类。 |
| `src/task/async_task.py` | 存放 API 发布的异步任务包装。 |
| `src/task/scheduled_task.py` | 存放 Beat 触发的定时任务包装。 |
| `src/service/` | 存放不依赖 Celery 的业务函数。 |
| `supervisor/programs/*.conf` | 用 Supervisor 守护 FastAPI、Worker 和 Beat 进程。 |

## 三、当前队列设计

当前项目只定义了两个业务队列和一个 direct exchange。

| 名称 | 用途 |
| --- | --- |
| `celery.tasks.direct` | Celery 任务使用的 RabbitMQ direct exchange。 |
| `celery.async.queue` | API 或其他调用方发布的异步任务队列。 |
| `celery.scheduled.queue` | Celery Beat 发布的定时任务队列。 |

路由规则在 `src/client/celery_config.py` 中：

- `app.tasks.async.*` 会进入 `celery.async.queue`。
- `app.tasks.scheduled.*` 会进入 `celery.scheduled.queue`。

`src/client/celery_config.py` 中设置了 `task_create_missing_queues=False`。这表示 Celery 不会因为队列名写错而自动创建未知队列。新增队列必须显式修改该配置文件，并重新声明拓扑。

## 四、本地启动完整 Celery 消息流

项目使用 `uv` 管理 Python 依赖，RabbitMQ 通过 Docker Compose 启动。

### 1. 准备环境

```bash
cp .env.example .env
uv sync
docker compose up -d rabbitmq
uv run python -m src.client.celery_topology
```

说明：

- `.env.example` 提供 RabbitMQ 和 Celery 配置键；复制后需要填写 RabbitMQ 账号和密码。
- `uv sync` 会根据 `pyproject.toml` 和 `uv.lock` 安装 Celery、FastAPI、Supervisor 等依赖。
- `docker compose up -d rabbitmq` 会启动 RabbitMQ 管理版镜像。
- `uv run python -m src.client.celery_topology` 会声明 `celery.tasks.direct`、`celery.async.queue` 和 `celery.scheduled.queue`。

RabbitMQ 管理页面：

```text
http://127.0.0.1:15672
```

登录账号和密码分别来自 `.env` 中的 `RABBITMQ_USER` 和 `RABBITMQ_PASSWORD`。

### 2. 开发模式启动

开发时可以开三个终端。

终端 1：启动 FastAPI。

```bash
uv run uvicorn main:app --host 127.0.0.1 --port 8000 --reload
```

终端 2：启动 Celery Worker。开发时可以让一个 Worker 同时消费异步队列和定时队列。

```bash
uv run celery -A src.client.celery_config:celery_app worker \
  --queues=celery.async.queue,celery.scheduled.queue \
  --loglevel=INFO
```

终端 3：启动 Celery Beat。

```bash
uv run celery -A src.client.celery_config:celery_app beat \
  --loglevel=INFO \
  --schedule=runtime/celerybeat-schedule
```

注意：同一个环境只能启动一个 Celery Beat。多个 Beat 会重复发布定时任务。

### 3. 调用当前异步任务示例

当前项目提供了一个示例接口：

```bash
curl -X POST http://127.0.0.1:8000/tasks/messages \
  -H 'Content-Type: application/json' \
  -d '{"message":"hello celery"}'
```

成功时接口返回 `202`：

```json
{
  "task_id": "00000000-0000-0000-0000-000000000000",
  "status": "已入队"
}
```

这个接口的实际代码链路是：

```text
src/controller/api.py
  -> enqueue_message()
  -> asyncio.to_thread(publish_task, process_message_task, payload)
  -> src/client/celery_publisher.py
  -> process_message_task.apply_async(...)
  -> RabbitMQ
  -> Celery Worker
  -> src/task/async_task.py
  -> src/service/example_service.py::process_message()
```

`asyncio.to_thread(...)` 的作用是避免 RabbitMQ 发布时的网络 I/O 阻塞 FastAPI 的事件循环。

### 4. 查看定时任务

当前定时任务在 `src/client/celery_config.py` 中：

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

含义：Celery Beat 每分钟向 `celery.scheduled.queue` 发布一次 `app.tasks.scheduled.heartbeat`，由监听该队列的 Worker 执行。

## 五、使用 Supervisor 启动整套服务

如果不想开多个终端，可以使用 Supervisor。

先确保已经执行过：

```bash
uv sync
docker compose up -d rabbitmq
uv run python -m src.client.celery_topology
```

然后启动 Supervisor：

```bash
mkdir -p runtime/logs
uv run supervisord -c supervisor/supervisord.conf
uv run supervisorctl -c supervisor/supervisord.conf status
```

当前 Supervisor 会守护这些进程：

| 进程 | 配置文件 | 职责 |
| --- | --- | --- |
| `fastapi` | `supervisor/programs/fastapi.conf` | 启动 FastAPI。 |
| `celery-async-worker` | `supervisor/programs/celery-async-worker.conf` | 只消费 `celery.async.queue`，并发数为 2。 |
| `celery-scheduled-worker` | `supervisor/programs/celery-scheduled-worker.conf` | 只消费 `celery.scheduled.queue`，并发数为 1。 |
| `celery-beat` | `supervisor/programs/celery-beat.conf` | 运行唯一的 Celery Beat 调度进程。 |

停止时建议先停 Beat，再停 Worker：

```bash
uv run supervisorctl -c supervisor/supervisord.conf stop celery-beat
uv run supervisorctl -c supervisor/supervisord.conf stop celery-async-worker
uv run supervisorctl -c supervisor/supervisord.conf stop celery-scheduled-worker
uv run supervisorctl -c supervisor/supervisord.conf shutdown
```

日志位置：

```text
runtime/logs/fastapi.log
runtime/logs/celery-async-worker.log
runtime/logs/celery-scheduled-worker.log
runtime/logs/celery-beat.log
runtime/logs/supervisord.log
```

## 六、新增异步任务的推荐方式

新增 API 触发的异步任务时，按下面顺序修改。

### 1. 添加参数模型

在 `src/model/task_model.py` 中添加 Pydantic 模型，并禁止额外字段：

```python
from pydantic import BaseModel, ConfigDict, Field


class GenerateFilePayload(BaseModel):
    model_config = ConfigDict(extra="forbid")

    filename: str = Field(min_length=1, max_length=200)
```

### 2. 添加业务函数

在 `src/service/` 中添加普通业务函数。业务函数不导入 Celery。

```python
def generate_file(payload: GenerateFilePayload) -> None:
    ...
```

业务函数应该尽量幂等。因为当前 Task 使用 `acks_late=True`，Worker 崩溃或连接异常时任务可能被重新投递。

### 3. 添加 Celery Task 包装

在 `src/task/async_task.py` 中添加薄包装：

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

关键约定：

- Task 名称使用 `app.tasks.async.<task_name>` 前缀。
- 入参统一使用 `raw_payload`。
- Task 内先做 Pydantic 校验，再调用业务函数。
- 只对明确可重试的异常使用 `RetryableTaskError`。
- 不要使用 `autoretry_for=(Exception,)`，否则参数错误、权限错误、代码缺陷也会被反复重试。

只要 Task 名称符合 `app.tasks.async.*`，它会自动路由到 `celery.async.queue`。

### 4. 在 API 中发布任务

FastAPI 路由里不要到处直接写 `.delay()` 或 `.apply_async()`，优先使用统一的 `publish_task()`：

```python
task_id = await asyncio.to_thread(
    publish_task,
    generate_file_task,
    payload,
)
```

`publish_task()` 会把 Pydantic 模型转换成 JSON 兼容 dict，并按统一的 `raw_payload` 参数发布：

```python
task.apply_async(
    kwargs={"raw_payload": payload.model_dump(mode="json")},
)
```

## 七、新增定时任务的推荐方式

新增定时任务时，按下面顺序修改。

### 1. 添加业务函数

在 `src/service/` 中添加普通函数，例如：

```python
def cleanup_expired_data() -> None:
    ...
```

如果任务执行时间可能超过调度间隔，业务层必须自己处理重叠执行问题，例如使用数据库锁、唯一运行记录或状态条件更新。

### 2. 添加 scheduled Task 包装

在 `src/task/scheduled_task.py` 中添加 Task，名称使用 `app.tasks.scheduled.*` 前缀：

```python
@celery_app.task(
    bind=True,
    base=LoggedTask,
    name="app.tasks.scheduled.cleanup_expired_data",
    acks_late=True,
)
def cleanup_expired_data_task(self: LoggedTask) -> None:
    cleanup_expired_data()
```

### 3. 添加 Beat 调度配置

在 `src/client/celery_config.py` 中添加计划：

```python
"cleanup-expired-data-every-day": {
    "task": "app.tasks.scheduled.cleanup_expired_data",
    "schedule": crontab(hour=3, minute=0),
    "options": {
        "queue": SCHEDULED_QUEUE_NAME,
        "routing_key": SCHEDULED_ROUTING_KEY,
    },
},
```

修改 Beat 配置后，需要重启唯一的 Celery Beat。

## 八、什么时候需要新增队列

默认情况下，不要为每个任务创建独立队列。复用当前两个队列即可：

- API 触发的任务：`celery.async.queue`
- Beat 触发的任务：`celery.scheduled.queue`

只有出现下面情况时，才考虑新增队列：

- 某类任务需要独立并发数。
- 某类任务很慢，需要和普通任务隔离。
- 某类任务依赖特殊资源，例如 GPU、外部服务限流、独立机器。
- 某类任务故障率高，不能影响普通任务消费。

新增队列时至少要同步修改：

1. `src/client/celery_config.py`：新增 queue、routing key 和 `TASK_ROUTES`。
2. `src/client/celery_config.py`：如果新增任务模块，加入 `TASK_IMPORTS`。
3. `supervisor/programs/`：新增或调整对应 Worker。
4. 执行 `uv run python -m src.client.celery_topology`：声明新拓扑。
5. 添加配置测试，并更新文档。

不要在业务代码、API 路由或 Task 内临时指定未知队列。

## 九、测试与检查

单元测试默认通过 `tests/conftest.py` 启用 Celery eager 模式，任务会在当前进程同步执行，不需要启动 RabbitMQ。

常用检查命令：

```bash
uv run ruff check .
uv run pytest
uv run python -m compileall -q src app main.py
```

如果需要确认 Worker 是否识别任务：

```bash
uv run celery -A src.client.celery_config:celery_app inspect registered
```

如果需要确认 RabbitMQ 拓扑是否可用：

```bash
docker compose ps
docker compose logs rabbitmq
uv run python -m src.client.celery_topology
```

## 十、项目内需要遵守的约束

1. 不要在多个模块里重复创建 `Celery(...)`，统一使用 `src/client/celery_config.py` 中的 `celery_app`。
2. 不要让 `src/service/` 中的业务函数依赖 Celery、FastAPI、RabbitMQ 或 Supervisor。
3. 不要在 API 中散落 `.delay()` 或 `.apply_async()`，优先通过 `publish_task()` 发布。
4. 不要开启动态队列创建，`task_create_missing_queues=False` 应保持不变。
5. 不要运行多个 Celery Beat。
6. 不要把所有异常都配置成自动重试。
7. 使用 `acks_late=True` 的任务必须按业务场景保证幂等。
8. 当前没有结果后端，不要把 `task_id` 当成任务状态查询能力。

更多新增任务细节见 `docs/adding-tasks.md`，常见问题见 `docs/troubleshooting.md`。
