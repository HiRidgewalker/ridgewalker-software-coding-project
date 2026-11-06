# FastAPI + Celery + RabbitMQ 异步任务与定时任务模板落地方案

本文是后续模板开发的实施依据。目标是在当前 FastAPI + RabbitMQ + Supervisor 项目上，增加一套规范化的 Celery 基础设施，使后续开发异步任务或定时任务时，只需要在约定目录添加业务函数、任务包装和必要的调度配置。

本文只确定方案，不在当前阶段修改应用代码、依赖或运行配置。后续实现应以本文为边界，若需求发生变化，应先更新本文再扩展代码。

## 一、建设目标

最终模板需要支持：

- FastAPI 接口异步发布 Celery 任务，并立即返回任务标识。
- Celery 使用当前 RabbitMQ 作为消息代理。
- 不同业务使用独立队列和独立 Worker。
- Worker 支持并发消费、失败重试、退避等待和中文日志。
- Celery Beat 统一发布周期任务。
- Supervisor 分别守护各类 Worker 和唯一的 Beat 进程。
- 交换机、队列、绑定关系集中定义，不允许任务代码动态创建未知队列。
- 任务请求通过 Pydantic 校验，并仅使用 JSON 序列化。
- 业务逻辑与 Celery 解耦，普通单元测试无需启动 RabbitMQ 或 Worker。
- 当前 Pika 消费者与 Celery 可以在迁移期间并行存在，但不能消费同一个队列。

第一版不追求覆盖所有分布式任务能力。以下组件暂不引入：

- Redis 结果后端。
- Flower 可视化监控。
- 数据库动态调度器。
- 分布式锁服务。
- 自动伸缩和 Kubernetes 部署。

这些能力只有在出现明确需求时再增加。

## 二、核心设计结论

### 1. Celery 只做任务基础设施，业务逻辑保持普通函数

代码调用关系固定为：

```text
FastAPI 路由
    ↓
任务发布器 publisher.py
    ↓
Celery Task 薄包装
    ↓
Pydantic 参数校验
    ↓
services/ 中的普通业务函数
```

业务函数不能依赖以下对象：

- Celery `Task` 对象。
- RabbitMQ Channel 或 Connection。
- FastAPI `Request`。
- Supervisor 进程信息。

这样做的目的，是让业务函数可以被单元测试、命令行、同步接口、Celery Task，甚至未来的 Temporal Activity 复用。

### 2. Celery 使用独立 RabbitMQ 拓扑

当前队列 `orders.created.queue` 保存的是项目自定义的 `MessageEnvelope` JSON。Celery 使用自己的任务消息协议，因此不能让 Celery Worker 直接监听该队列。

第一版新增独立拓扑：

```text
交换机：celery.tasks.direct

celery.orders.queue
  └── binding_key=celery.orders

celery.maintenance.queue
  └── binding_key=celery.maintenance
```

职责划分：

| 队列 | 用途 | Worker |
|---|---|---|
| `celery.orders.queue` | 订单、通知等接口触发的异步任务 | `celery-orders-worker` |
| `celery.maintenance.queue` | 清理、统计、归档等维护和周期任务 | `celery-maintenance-worker` |

新增业务队列必须先更新集中拓扑和路由配置，不允许在任务函数中临时指定一个不存在的队列。

### 3. Supervisor 只管理 Celery 主进程

```text
Supervisor
├── celery-orders-worker
│   └── Celery 自己管理并发执行子进程
├── celery-maintenance-worker
│   └── Celery 自己管理并发执行子进程
└── celery-beat
    └── 只允许一个周期调度进程
```

Supervisor 不管理每一条任务，也不直接管理 Celery 创建的并发池子进程。

## 三、目标目录结构

在当前项目中新增以下结构：

```text
app/
├── task_queue/
│   ├── __init__.py
│   ├── celery_app.py          # 创建全局唯一的 Celery 应用
│   ├── config.py              # 通用 Celery 配置
│   ├── queues.py              # 交换机、队列、路由集中定义
│   ├── schedules.py           # 周期任务配置
│   ├── base_task.py           # 任务日志和通用生命周期行为
│   ├── exceptions.py          # 可重试异常等任务异常类型
│   ├── publisher.py           # FastAPI 发布任务的统一入口
│   └── topology.py            # Celery 拓扑初始化命令
│
├── tasks/
│   ├── __init__.py
│   ├── order_tasks.py         # 订单类 Celery Task
│   └── maintenance_tasks.py   # 维护类 Celery Task
│
├── services/
│   ├── __init__.py
│   ├── order_service.py       # 订单类普通业务函数
│   └── maintenance_service.py # 维护类普通业务函数
│
└── task_models.py             # 任务请求和响应 Pydantic 模型

supervisor/programs/
├── celery-orders-worker.conf
├── celery-maintenance-worker.conf
└── celery-beat.conf

tests/
├── task_queue/
├── tasks/
└── services/

hiduck/celery/
├── fastapi-celery-rabbitmq-template-plan.md
├── celery-usage.md
├── adding-tasks.md
└── troubleshooting.md
```

当前已经存在 `app/models.py`，第一版新增任务模型时使用 `app/task_models.py`，避免为了增加 Celery 而进行无关的大规模模型目录重构。

## 四、依赖与配置方案

### 1. Python 依赖

后续实施时通过 `uv` 添加 Celery，并锁定在同一个主版本范围内：

```bash
uv add "celery>=5.5,<6"
```

实际落地时应以 Celery 当前稳定版和项目 Python 版本兼容性为准，再更新 `uv.lock`。

第一版不添加 Redis 客户端、Flower 或数据库调度器依赖。

### 2. Settings 配置

继续使用现有 RabbitMQ 配置作为唯一连接信息来源：

```text
RABBITMQ_HOST
RABBITMQ_PORT
RABBITMQ_USER
RABBITMQ_PASSWORD
RABBITMQ_VHOST
```

在 `Settings` 中增加只读属性 `celery_broker_url`，由这些字段安全构造 AMQP 地址，避免 `.env` 同时维护两套账号密码。

新增 Celery 配置项：

```text
CELERY_TIMEZONE=Asia/Shanghai
CELERY_ORDERS_CONCURRENCY=2
CELERY_MAINTENANCE_CONCURRENCY=1
CELERY_TASK_ALWAYS_EAGER=false
```

测试环境才允许启用 `CELERY_TASK_ALWAYS_EAGER=true`。

### 3. 第一版不配置结果后端

第一版设置：

```python
task_ignore_result = True
```

FastAPI 返回 `task_id` 只用于日志关联，不提供基于 `AsyncResult` 的任务状态查询接口。

业务状态必须写入业务数据库，例如：

```text
订单邮件发送状态
报表生成状态
数据清理批次状态
```

以后若明确需要短期任务结果查询，再单独评估 Redis 或数据库结果后端。Celery 结果后端不能替代业务数据库中的最终状态。

## 五、Celery 应用初始化

`app/task_queue/celery_app.py` 只创建一个全局 Celery 实例：

```python
from celery import Celery

from app.settings import get_settings
from app.task_queue.config import configure_celery

settings = get_settings()

celery_app = Celery(
    "rabbitmq_learning_project",
    broker=settings.celery_broker_url,
)

configure_celery(celery_app)
```

禁止在不同任务模块中重复创建 `Celery(...)`。

`config.py` 统一配置：

```python
def configure_celery(celery_app: Celery) -> None:
    celery_app.conf.update(
        task_serializer="json",
        accept_content=["json"],
        result_serializer="json",
        timezone="Asia/Shanghai",
        enable_utc=True,
        task_ignore_result=True,
        task_create_missing_queues=False,
        worker_prefetch_multiplier=1,
        task_queues=TASK_QUEUES,
        task_routes=TASK_ROUTES,
        beat_schedule=BEAT_SCHEDULE,
        imports=(
            "app.tasks.order_tasks",
            "app.tasks.maintenance_tasks",
        ),
    )
```

配置含义：

| 配置 | 目的 |
|---|---|
| `task_serializer="json"` | 任务只使用 JSON 序列化。 |
| `accept_content=["json"]` | 拒绝 Pickle 等未允许的消息格式。 |
| `timezone="Asia/Shanghai"` | 周期任务按项目约定时区配置。 |
| `enable_utc=True` | 内部统一处理时间，显示和调度使用配置时区。 |
| `task_create_missing_queues=False` | 禁止任务名称或队列名称写错时自动创建未知队列。 |
| `worker_prefetch_multiplier=1` | 减少一个 Worker 预取过多任务，便于公平分发。 |
| `imports` | Worker 启动时显式注册全部任务模块。 |

新增任务到已有 `order_tasks.py` 或 `maintenance_tasks.py` 时，无需修改 `imports`；只有新增任务模块时才增加一条导入配置。

## 六、交换机、队列和路由定义

`queues.py` 是 Celery RabbitMQ 拓扑的唯一配置源：

```python
from kombu import Exchange, Queue

TASK_EXCHANGE = Exchange(
    "celery.tasks.direct",
    type="direct",
    durable=True,
)

TASK_QUEUES = (
    Queue(
        "celery.orders.queue",
        exchange=TASK_EXCHANGE,
        routing_key="celery.orders",
        durable=True,
    ),
    Queue(
        "celery.maintenance.queue",
        exchange=TASK_EXCHANGE,
        routing_key="celery.maintenance",
        durable=True,
    ),
)

TASK_ROUTES = {
    "app.tasks.order.*": {
        "queue": "celery.orders.queue",
        "routing_key": "celery.orders",
    },
    "app.tasks.maintenance.*": {
        "queue": "celery.maintenance.queue",
        "routing_key": "celery.maintenance",
    },
}
```

任务名称必须符合路由前缀：

```text
app.tasks.order.send_order_email
app.tasks.order.process_order_created
app.tasks.maintenance.cleanup_expired_orders
app.tasks.maintenance.generate_daily_report
```

### 拓扑初始化要求

新增 `app/task_queue/topology.py`，提供一次性初始化命令：

```bash
uv run python -m app.task_queue.topology
```

该命令负责声明：

- `celery.tasks.direct` 直连交换机。
- `celery.orders.queue` 持久化队列。
- `celery.maintenance.queue` 持久化队列。
- 两组绑定关系。

FastAPI 的 `lifespan` 可以复用该初始化函数，保持当前“应用启动时统一初始化拓扑”的行为；部署脚本仍应在启动 Worker 前显式执行初始化命令，使 Worker 不依赖 FastAPI 必须先运行。

任务模块、业务函数和路由模块中都不允许出现 `exchange_declare`、`queue_declare` 或 `queue_bind`。

## 七、业务函数开发规范

业务逻辑写入 `app/services/`。示例：

```python
def send_order_email(payload: SendOrderEmailPayload) -> None:
    """发送订单邮件。"""

    # 查询业务数据、调用邮件服务、更新发送状态。
    ...
```

业务函数必须满足：

- 输入参数是明确的 Pydantic 模型或基础类型。
- 不接收 Celery、FastAPI、Pika 对象。
- 不把 ORM 对象、数据库连接、文件句柄作为参数传入。
- 对可能重复执行的操作实现幂等。
- 对瞬时故障抛出明确的可重试异常。
- 对参数错误和业务规则错误抛出不可重试异常。

推荐的幂等方式：

- 数据库唯一约束。
- 业务请求号。
- `message_id` 或 `task_id` 对应的任务执行记录。
- 状态机条件更新，例如只允许 `待发送 → 已发送`。

## 八、任务参数模型

`app/task_models.py` 保存任务请求模型和接口响应模型：

```python
class SendOrderEmailPayload(BaseModel):
    model_config = ConfigDict(extra="forbid")

    order_id: str = Field(min_length=1, max_length=64)
    user_id: int = Field(gt=0)
    email: EmailStr


class TaskAcceptedResponse(BaseModel):
    task_id: UUID
    status: Literal["已入队"] = "已入队"
```

传给 Celery 的参数只允许包含可 JSON 序列化的数据：

```text
字符串、数字、布尔值、空值、列表、字典
```

日期、UUID、Decimal 等类型在发布前通过 Pydantic 的 JSON 模式转换：

```python
payload.model_dump(mode="json")
```

任务参数应传业务标识，不传完整大对象。例如传 `order_id`，由 Worker 根据标识查询当前数据。

## 九、Celery Task 开发规范

Celery Task 是业务函数的薄包装，职责限定为：

1. 反序列化并校验任务参数。
2. 记录任务开始、重试、成功和失败日志。
3. 调用普通业务函数。
4. 将明确的瞬时错误交给 Celery 重试。

示例：

```python
@celery_app.task(
    bind=True,
    base=LoggedTask,
    name="app.tasks.order.send_order_email",
    autoretry_for=(RetryableTaskError,),
    retry_backoff=True,
    retry_backoff_max=600,
    retry_jitter=True,
    max_retries=5,
    acks_late=True,
)
def send_order_email_task(
    self: LoggedTask,
    raw_payload: dict[str, object],
) -> None:
    payload = SendOrderEmailPayload.model_validate(raw_payload)
    send_order_email(payload)
```

### 重试规则

禁止使用：

```python
autoretry_for=(Exception,)
```

这会导致参数错误、代码缺陷、权限拒绝等不可恢复错误反复重试。

第一版定义：

```python
class RetryableTaskError(RuntimeError):
    """网络抖动或外部服务暂时不可用等可恢复错误。"""
```

业务层捕获底层瞬时异常后，可以转换成 `RetryableTaskError`。校验错误和明确业务拒绝直接失败，不自动重试。

### ACK 与幂等规则

`acks_late=True` 表示任务执行完成后再确认消息。Worker 在确认前异常退出时，任务可能再次执行，因此使用该配置的任务必须幂等。

`task_reject_on_worker_lost` 不在第一版全局开启。它可能让持续导致进程崩溃或内存溢出的任务不断重投递。确有需求时，应按任务评估，并结合最大重试、失败记录和告警使用。

## 十、基础 Task 与中文日志

`base_task.py` 提供 `LoggedTask`：

```python
class LoggedTask(Task):
    abstract = True

    def on_success(self, retval, task_id, args, kwargs) -> None:
        logger.info("任务执行成功：任务名称=%s，任务标识=%s", self.name, task_id)

    def on_retry(self, exc, task_id, args, kwargs, einfo) -> None:
        logger.warning(
            "任务准备重试：任务名称=%s，任务标识=%s，原因=%s",
            self.name,
            task_id,
            exc,
        )

    def on_failure(self, exc, task_id, args, kwargs, einfo) -> None:
        logger.error(
            "任务执行失败：任务名称=%s，任务标识=%s，原因=%s",
            self.name,
            task_id,
            exc,
        )
```

技术标识、任务名称和异常类名保留英文；应用说明和日志正文统一使用中文。

日志至少包含：

- `task_id`。
- 任务名称。
- 重试次数。
- 业务唯一标识，例如 `order_id`。
- 执行结果或失败原因。

禁止在日志中记录密码、完整认证令牌或不必要的个人信息。

## 十一、任务发布器与 FastAPI 接口

FastAPI 路由不直接散落 `.delay()` 或 `.apply_async()` 调用，统一通过 `publisher.py`：

```python
def enqueue_order_email(payload: SendOrderEmailPayload) -> str:
    result = send_order_email_task.apply_async(
        kwargs={
            "raw_payload": payload.model_dump(mode="json"),
        },
    )
    return result.id
```

路由示例：

```python
@router.post(
    "/tasks/order-email",
    response_model=TaskAcceptedResponse,
    status_code=status.HTTP_202_ACCEPTED,
)
async def create_order_email_task(
    payload: SendOrderEmailPayload,
) -> TaskAcceptedResponse:
    task_id = await asyncio.to_thread(enqueue_order_email, payload)
    return TaskAcceptedResponse(task_id=task_id)
```

因为 Celery 的任务发布调用可能等待 RabbitMQ 网络操作，所以 FastAPI 异步路由使用 `asyncio.to_thread()`，避免阻塞事件循环。

第一版接口返回：

```json
{
  "task_id": "任务唯一标识",
  "status": "已入队"
}
```

第一版不实现 `/tasks/{task_id}` 查询接口。若未来增加结果后端或业务任务表，再设计统一查询接口。

## 十二、定时任务开发规范

周期计划集中定义在 `schedules.py`，不能散落到任务模块：

```python
from celery.schedules import crontab

BEAT_SCHEDULE = {
    "cleanup-expired-orders-every-five-minutes": {
        "task": "app.tasks.maintenance.cleanup_expired_orders",
        "schedule": crontab(minute="*/5"),
        "options": {
            "queue": "celery.maintenance.queue",
            "routing_key": "celery.maintenance",
        },
    },
    "generate-daily-order-report": {
        "task": "app.tasks.maintenance.generate_daily_order_report",
        "schedule": crontab(hour=0, minute=0),
        "options": {
            "queue": "celery.maintenance.queue",
            "routing_key": "celery.maintenance",
        },
    },
}
```

调度项名称是稳定技术标识，使用小写英文和连字符；文档与日志解释使用中文。

Celery Beat 只负责按时间发布任务，实际执行仍由 Worker 完成：

```text
Celery Beat 到达调度时间
    ↓
向 celery.maintenance.queue 发布任务
    ↓
celery-maintenance-worker 执行任务
```

### 防止周期任务重叠

如果任务每 5 分钟执行一次，但单次执行可能超过 5 分钟，Beat 仍会继续发布下一条任务。

第一版要求业务函数自行保证重入安全。后续如需严格禁止重叠，可以增加：

- 数据库唯一运行记录。
- 数据库悲观锁或乐观锁。
- Redis 分布式锁。
- 按时间窗口生成唯一幂等键。

Beat 在一个调度环境中只能运行一个实例，否则会重复发布周期任务。生产配置不使用 `celery worker -B` 将 Beat 嵌入 Worker，而是保持独立进程。

## 十三、Supervisor 配置方案

### 1. 订单 Worker

`supervisor/programs/celery-orders-worker.conf`：

```ini
[program:celery-orders-worker]
directory=%(here)s/../..
command=%(here)s/../../.venv/bin/celery -A app.task_queue.celery_app:celery_app worker --queues=celery.orders.queue --hostname=orders@%%h --concurrency=2 --loglevel=INFO
autostart=false
autorestart=true
startsecs=5
startretries=5
stopsignal=TERM
stopwaitsecs=120
stopasgroup=true
killasgroup=true
stdout_logfile=%(here)s/../../runtime/logs/celery-orders-worker.log
stdout_logfile_maxbytes=5MB
stdout_logfile_backups=5
redirect_stderr=true
environment=PYTHONUNBUFFERED="1"
```

`%%h` 必须写两个百分号，因为 Supervisor 会先处理 `%`，最终 Celery 才能收到 `%h`。

### 2. 维护 Worker

`supervisor/programs/celery-maintenance-worker.conf` 与订单 Worker 相同，但调整：

```ini
[program:celery-maintenance-worker]
command=... worker --queues=celery.maintenance.queue --hostname=maintenance@%%h --concurrency=1 --loglevel=INFO
stdout_logfile=.../runtime/logs/celery-maintenance-worker.log
```

维护任务通常执行时间更长，第一版并发数设为 1，后续按压测结果调整。

### 3. Celery Beat

`supervisor/programs/celery-beat.conf`：

```ini
[program:celery-beat]
directory=%(here)s/../..
command=%(here)s/../../.venv/bin/celery -A app.task_queue.celery_app:celery_app beat --loglevel=INFO --schedule=runtime/celerybeat-schedule
autostart=false
autorestart=true
startsecs=5
startretries=5
stopsignal=TERM
stopwaitsecs=30
stdout_logfile=%(here)s/../../runtime/logs/celery-beat.log
stdout_logfile_maxbytes=5MB
stdout_logfile_backups=5
redirect_stderr=true
environment=PYTHONUNBUFFERED="1"
```

`runtime/celerybeat-schedule*` 属于运行文件，需要加入 `.gitignore`。

### 4. 并发职责

同一业务队列优先使用 Celery 的 `--concurrency` 调整并发，不同时叠加 Supervisor `numprocs`，避免第一版出现两层并发配置难以判断总进程数。

不同业务队列继续使用独立 `[program:...]`，实现日志、重启和资源隔离。

## 十四、启动和停止顺序

第一次启动：

```bash
# 1. 安装依赖
uv sync

# 2. 启动或确认 RabbitMQ 已运行

# 3. 初始化 RabbitMQ 和 Celery 拓扑
uv run python -m app.task_queue.topology

# 4. 启动 FastAPI
uv run uvicorn main:app --host 127.0.0.1 --port 8000 --reload

# 5. 启动 Supervisord
uv run supervisord -c supervisor/supervisord.conf

# 6. 启动两个 Worker
uv run supervisorctl -c supervisor/supervisord.conf start celery-orders-worker
uv run supervisorctl -c supervisor/supervisord.conf start celery-maintenance-worker

# 7. 最后启动唯一 Beat
uv run supervisorctl -c supervisor/supervisord.conf start celery-beat

# 8. 查看状态
uv run supervisorctl -c supervisor/supervisord.conf status
```

停止顺序：

```bash
# 先停止新的周期任务发布
uv run supervisorctl -c supervisor/supervisord.conf stop celery-beat

# 再优雅停止 Worker
uv run supervisorctl -c supervisor/supervisord.conf stop celery-orders-worker
uv run supervisorctl -c supervisor/supervisord.conf stop celery-maintenance-worker

# 最后关闭 Supervisord
uv run supervisorctl -c supervisor/supervisord.conf shutdown
```

`stopwaitsecs` 必须大于最长任务正常执行时间并留出缓冲。超过时间后 Supervisor 会使用强制终止，任务可能发生重投递。

## 十五、测试方案

### 1. 业务函数单元测试

直接调用 `services/` 中的函数：

```python
def test_send_order_email() -> None:
    payload = SendOrderEmailPayload(...)
    send_order_email(payload)
```

这类测试不启动 Celery、RabbitMQ 或 Supervisor。

### 2. 参数模型测试

验证：

- 必填字段缺失。
- 字段类型错误。
- 额外字段被拒绝。
- UUID、时间和 Decimal 能转换为 JSON。

### 3. Task 包装测试

测试环境配置：

```python
task_always_eager = True
task_eager_propagates = True
```

验证：

- Task 能正确调用业务函数。
- 可重试异常触发重试。
- 参数错误不会进入业务函数。
- 不可重试异常不会被错误重试。

Eager 模式不会经过 RabbitMQ，不能替代集成测试。

### 4. 配置测试

验证：

- 所有 Task 名称都能匹配一个路由。
- 所有路由目标都存在于 `TASK_QUEUES`。
- 所有 Beat 调度项引用的 Task 已注册。
- Beat 调度项使用维护队列。
- `task_create_missing_queues` 保持关闭。

### 5. RabbitMQ 集成测试

使用本地 RabbitMQ 验证：

- FastAPI 返回 `202` 和 `task_id`。
- 任务进入预期队列。
- 对应 Worker 能消费任务。
- Worker 日志包含任务标识和业务标识。
- 瞬时异常按照退避策略重试。
- Worker 处理期间被终止后，幂等任务不会产生重复业务结果。
- Supervisor 能重新拉起异常退出的 Worker。
- Beat 只发布一次周期任务。

## 十六、当前 Pika 消费者迁移策略

迁移期间保留两套独立消息流：

```text
现有学习消息流：
FastAPI → orders.direct → orders.created.queue → app.consumer

新增 Celery 消息流：
FastAPI → Celery → celery.tasks.direct → celery.*.queue → Celery Worker
```

禁止：

- Celery Worker 消费 `orders.created.queue`。
- `app.consumer` 消费 `celery.orders.queue`。
- 同一个发布接口同时向两套系统发送正式业务任务，除非已经设计去重和补偿。

现有业务迁移步骤：

1. 把 `_on_message` 中的业务逻辑提取到 `services/`。
2. 保持 Pika 消费者调用新的业务函数，验证行为不变。
3. 增加调用同一业务函数的 Celery Task。
4. 增加新的 Celery 发布接口或切换发布器。
5. 观察 Celery 队列、日志、重试和业务幂等结果。
6. 停止旧消息发布。
7. 等待旧 `orders.created.queue` 完全消费。
8. 停止并移除旧 Pika 消费者配置。

该过程是业务级迁移，不是让 Celery 直接读取旧消息。

## 十七、后续新增任务的标准流程

### 新增普通异步任务

1. 在 `app/task_models.py` 添加请求模型。
2. 在 `app/services/` 添加普通业务函数。
3. 在对应的 `app/tasks/*_tasks.py` 添加 Task 包装。
4. 使用符合路由前缀的唯一 Task 名称。
5. 在 `publisher.py` 添加发布函数。
6. FastAPI 路由通过发布函数入队。
7. 添加业务、参数和 Task 测试。
8. 如果复用已有队列，不修改 Supervisor 和拓扑。

### 新增周期任务

1. 完成普通异步任务的前三步。
2. 在 `schedules.py` 增加一个调度项。
3. 明确是否允许任务重叠。
4. 添加调度配置测试。
5. 重启 Beat，使新配置生效。

### 新增业务队列

只有在需要业务隔离、独立并发或独立资源时才新增队列：

1. 在 `queues.py` 添加 Queue 和路由。
2. 在拓扑初始化器中声明交换机、队列和绑定。
3. 新增专用 Worker 的 Supervisor 配置。
4. 为 Worker 设置独立日志文件。
5. 更新配置测试、启动文档和排错文档。

## 十八、实施阶段

### 第一阶段：基础设施骨架

- 添加 Celery 依赖。
- 扩展 Settings。
- 创建 `task_queue/`、`tasks/`、`services/`。
- 实现 Celery 应用、队列、路由、基础 Task 和中文日志。
- 实现独立拓扑初始化命令。

### 第二阶段：异步任务示例

- 实现一个订单邮件或订单处理演示业务函数。
- 实现 Pydantic 任务参数模型。
- 实现 Celery Task 和发布器。
- 增加 FastAPI `202` 发布接口。
- 添加单元测试和 RabbitMQ 集成验证。

### 第三阶段：定时任务示例

- 实现一个无副作用的维护任务，例如定时记录运行时间或清理演示数据。
- 增加 `BEAT_SCHEDULE`。
- 验证时区、调度频率和单 Beat 约束。

### 第四阶段：Supervisor 管理

- 新增两个 Worker 配置。
- 新增 Beat 配置。
- 验证启动、停止、异常重启、日志轮转和优雅退出。
- 更新 `.gitignore` 中的 Celery 运行文件。

### 第五阶段：文档与迁移

- 新增 Celery 使用文档。
- 新增异步任务和周期任务开发规范。
- 新增常见故障排查文档。
- 保留当前 Pika 示例，明确两套消息协议边界。

## 十九、第一版验收标准

全部满足以下条件才算模板落地完成：

- `uv sync` 能完成依赖安装。
- FastAPI、两个 Worker 和 Beat 能分别启动。
- RabbitMQ 拓扑在任务发布前统一初始化。
- 未配置队列不会被动态创建。
- FastAPI 发布异步任务后返回 `202` 和 `task_id`。
- 订单任务只进入订单队列。
- 维护任务只进入维护队列。
- Worker 日志为中文，并包含任务标识。
- 可重试异常按照最大次数和退避策略重试。
- 参数错误不会重试。
- 周期任务由唯一 Beat 按配置发布。
- Supervisor 能自动重启异常退出的 Worker 和 Beat。
- 多个进程不共享同一个轮转日志文件。
- 单元测试不依赖 RabbitMQ。
- 集成测试能够验证真实 RabbitMQ 消息流。
- `git diff --check`、Python 编译检查和全部测试通过。
- README 与 `hiduck/celery/` 文档中的命令可以从项目根目录直接执行。

## 二十、后续可选扩展

只有出现明确需求时再增加：

| 需求 | 可选方案 |
|---|---|
| 查询短期任务结果 | Redis 或数据库结果后端 |
| Worker 可视化监控 | Flower |
| 在线编辑周期计划 | `django-celery-beat` 或自建数据库调度管理 |
| 严格防止周期任务重叠 | 数据库锁或 Redis 分布式锁 |
| 失败任务人工补偿 | 业务任务记录表和补偿接口 |
| 指标与告警 | Prometheus、Grafana 和 Celery Events |
| 跨服务长流程编排 | 评估 Temporal，而不是继续堆叠 Task 链 |
| 容器化扩缩容 | Docker Compose 或 Kubernetes |

## 二十一、最终落地边界

第一版最终架构固定为：

```text
FastAPI
  ├── 普通 Web 接口
  ├── 任务参数校验
  └── 通过 publisher 发布 Celery 任务

RabbitMQ
  ├── 保留当前自定义学习消息拓扑
  └── 新增 celery.tasks.direct 和 Celery 专用队列

Celery
  ├── orders Worker
  ├── maintenance Worker
  └── 唯一 Beat

Supervisor
  ├── 守护两个 Worker
  └── 守护 Beat

业务代码
  ├── services/ 普通函数
  ├── tasks/ Celery 薄包装
  └── task_models.py 参数契约
```

后续实现应优先保证边界清晰、任务幂等、配置集中和可测试性，再逐步增加结果后端、监控或动态调度等高级能力。
