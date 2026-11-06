# Celery 常用 CLI 命令

本文记录当前项目常用的 Celery CLI 命令。所有命令都基于本项目唯一的 Celery app：

```bash
uv run celery -A src.client.celery_config:celery_app <command>
```

本项目当前有两个 Celery 队列：

- `celery.async.queue`：API 或其他调用方发布的异步任务队列。
- `celery.scheduled.queue`：Celery Beat 发布的定时任务队列。

## 一、启动 Worker 和 Beat

### 1. 启动一个同时消费异步任务和定时任务的 Worker

功能：开发环境常用，一个 Worker 同时监听两个队列，方便本地验证完整任务流。

```bash
uv run celery -A src.client.celery_config:celery_app worker \
  --queues=celery.async.queue,celery.scheduled.queue \
  --loglevel=INFO
```

### 2. 启动只消费异步任务队列的 Worker

功能：只处理 API 等调用方发布到 `celery.async.queue` 的任务。

```bash
uv run celery -A src.client.celery_config:celery_app worker \
  --queues=celery.async.queue \
  --loglevel=INFO
```

### 3. 启动只消费定时任务队列的 Worker

功能：只处理 Celery Beat 发布到 `celery.scheduled.queue` 的任务。

```bash
uv run celery -A src.client.celery_config:celery_app worker \
  --queues=celery.scheduled.queue \
  --loglevel=INFO
```

### 4. 启动 Celery Beat

功能：启动定时任务调度进程，按 `src/client/celery_config.py` 中的 `BEAT_SCHEDULE` 发布任务消息。

```bash
uv run celery -A src.client.celery_config:celery_app beat \
  --loglevel=INFO \
  --schedule=runtime/celerybeat-schedule
```

注意：同一个环境只应运行一个 Celery Beat，否则定时任务会被重复发布。

## 二、查看 Worker 状态

### 1. 查看在线 Worker

功能：列出当前能被 Celery 控制命令发现的在线 Worker。

```bash
uv run celery -A src.client.celery_config:celery_app status
```

### 2. Ping Worker

功能：检查 Worker 是否能响应控制命令；正常情况下会返回 `pong`。

```bash
uv run celery -A src.client.celery_config:celery_app inspect ping
```

### 3. 查看 Worker 统计信息

功能：查看 Worker 的进程池、broker 连接、已执行任务计数、预取配置等运行统计。

```bash
uv run celery -A src.client.celery_config:celery_app inspect stats
```

### 4. 查看 Worker 正在监听的队列

功能：确认 Worker 实际绑定了哪些队列，用于排查 Worker 启动参数和预期队列不一致的问题。

```bash
uv run celery -A src.client.celery_config:celery_app inspect active_queues
```

## 三、查看 Task 状态

### 1. 查看已注册的 Task

功能：确认 Worker 是否已经导入 Task 模块，以及 `@celery_app.task(...)` 是否完成注册。

```bash
uv run celery -A src.client.celery_config:celery_app inspect registered
```

如果新增了独立 Task 模块但这里看不到对应任务，优先检查 `src/client/celery_config.py` 中的 `TASK_IMPORTS`。

### 2. 查看正在执行的 Task

功能：列出 Worker 当前正在执行的任务。

```bash
uv run celery -A src.client.celery_config:celery_app inspect active
```

### 3. 查看已预取但尚未执行的 Task

功能：列出 Worker 已从 broker 取到、但还没有开始执行的任务。

```bash
uv run celery -A src.client.celery_config:celery_app inspect reserved
```

### 4. 查看 Worker 内部等待调度的 Task

功能：列出带 ETA 或 countdown、已经被 Worker 接收但还没到执行时间的任务。

```bash
uv run celery -A src.client.celery_config:celery_app inspect scheduled
```

注意：这里查看的是 Worker 内部的 ETA/countdown 任务，不等同于 RabbitMQ 队列深度，也不等同于 Celery Beat 的 `BEAT_SCHEDULE` 配置。

### 5. 查看已撤销的 Task

功能：查看 Worker 当前记录的 revoked task id。

```bash
uv run celery -A src.client.celery_config:celery_app inspect revoked
```

### 6. 按 task id 查询任务

功能：查询指定 task id 在 Worker 侧的状态信息。

```bash
uv run celery -A src.client.celery_config:celery_app inspect query_task <task_id>
```

注意：本项目默认不配置 result backend，API 返回的 `task_id` 主要用于日志关联。已完成任务通常不能像有结果后端的项目一样长期查询状态。

## 四、手动发布测试任务

### 1. 发布异步消息处理任务

功能：绕过 FastAPI，直接通过 Celery CLI 发布 `app.tasks.async.process_message`，用于验证 broker、路由和 Worker 消费链路。

```bash
uv run celery -A src.client.celery_config:celery_app call app.tasks.async.process_message \
  --kwargs='{"raw_payload":{"message":"hello celery"}}'
```

该任务名称匹配 `app.tasks.async.*`，会按 `TASK_ROUTES` 进入 `celery.async.queue`。

### 2. 发布定时任务对应的 Task

功能：手动发布心跳 Task，用于验证 scheduled Worker 是否能消费 `celery.scheduled.queue`。这只是手动触发一次，不依赖 Beat 的定时调度。

```bash
uv run celery -A src.client.celery_config:celery_app call app.tasks.scheduled.heartbeat \
  --queue=celery.scheduled.queue \
  --routing-key=celery.scheduled
```

## 五、危险命令

### 1. 清空已配置队列中的待处理消息

功能：删除 Celery 已知任务队列中还没有被 Worker 消费的待处理消息。

```bash
uv run celery -A src.client.celery_config:celery_app purge
```

注意：该命令会造成未执行任务丢失。执行前必须确认当前环境、broker 和队列，生产环境不要随手执行。

## 六、Supervisor 对照命令

Supervisor 用于守护 FastAPI、Celery Worker 和 Celery Beat。下面命令不是 Celery CLI，但排查本项目运行状态时经常一起使用。

### 1. 查看 Supervisor 管理的进程状态

功能：查看 FastAPI、异步 Worker、定时 Worker 和 Beat 是否处于运行状态。

```bash
uv run supervisorctl -c supervisor/supervisord.conf status
```

### 2. 重启异步 Worker

功能：重启只消费 `celery.async.queue` 的 Worker。

```bash
uv run supervisorctl -c supervisor/supervisord.conf restart celery-async-worker
```

### 3. 重启定时 Worker

功能：重启只消费 `celery.scheduled.queue` 的 Worker。

```bash
uv run supervisorctl -c supervisor/supervisord.conf restart celery-scheduled-worker
```

### 4. 重启 Celery Beat

功能：重启唯一的定时任务发布进程。修改 `BEAT_SCHEDULE` 后需要重启 Beat 才会加载新配置。

```bash
uv run supervisorctl -c supervisor/supervisord.conf restart celery-beat
```

### 5. 按推荐顺序停止 Celery 相关进程

功能：先停止 Beat，避免继续发布新任务，再停止 Worker。

```bash
uv run supervisorctl -c supervisor/supervisord.conf stop celery-beat
uv run supervisorctl -c supervisor/supervisord.conf stop celery-async-worker
uv run supervisorctl -c supervisor/supervisord.conf stop celery-scheduled-worker
```

## 七、常见排查顺序

### 1. Worker 是否在线

```bash
uv run celery -A src.client.celery_config:celery_app status
```

### 2. Worker 是否监听了正确队列

```bash
uv run celery -A src.client.celery_config:celery_app inspect active_queues
```

### 3. Task 是否已经注册

```bash
uv run celery -A src.client.celery_config:celery_app inspect registered
```

### 4. 是否有任务正在执行或等待执行

```bash
uv run celery -A src.client.celery_config:celery_app inspect active
uv run celery -A src.client.celery_config:celery_app inspect reserved
uv run celery -A src.client.celery_config:celery_app inspect scheduled
```

### 5. Supervisor 进程是否正常

```bash
uv run supervisorctl -c supervisor/supervisord.conf status
```
