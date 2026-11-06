# FastAPI + Celery + RabbitMQ 模板

这是一个刻意保持简洁的异步任务模板，包含 FastAPI、Celery、RabbitMQ、uv 和
Supervisor。仓库只提供中性的消息处理与心跳示例，不包含具体业务。

## 结构与约束

```text
FastAPI 路由
    -> src/client/celery_publisher.py
    -> src/task/ 中的 Celery 薄包装
    -> Pydantic 参数校验
    -> src/service/ 中的普通业务函数
```

- `celery.async.queue`：API 等调用方发布的异步任务。
- `celery.scheduled.queue`：Celery Beat 发布的定时任务。
- `celery.tasks.direct`：上述队列共用的 direct exchange。
- 只使用 JSON，不配置结果后端，API 返回的 `task_id` 用于日志关联。
- 未在 `src/client/celery_config.py` 中配置的队列不会被自动创建。
- 业务函数不依赖 FastAPI、Celery、RabbitMQ 或 Supervisor。

## 本地启动

要求已安装 [uv](https://docs.astral.sh/uv/) 和 Docker Compose。

```bash
cp .env.example .env
uv sync
docker compose up -d rabbitmq
uv run python -m src.client.celery_topology
```

开发时可在三个终端分别启动：

```bash
uv run uvicorn main:app --host 127.0.0.1 --port 8000 --reload
uv run celery -A src.client.celery_config:celery_app worker \
  --queues=celery.async.queue,celery.scheduled.queue --loglevel=INFO
uv run celery -A src.client.celery_config:celery_app beat \
  --loglevel=INFO --schedule=runtime/celerybeat-schedule
```

发布中性示例任务：

```bash
curl -X POST http://127.0.0.1:8000/tasks/messages \
  -H 'Content-Type: application/json' \
  -d '{"message":"hello celery"}'
```

响应状态为 `202`：

```json
{"task_id":"00000000-0000-0000-0000-000000000000","status":"已入队"}
```

RabbitMQ 管理页面为 <http://127.0.0.1:15672>，登录信息由 `.env` 中的
`RABBITMQ_USER` 和 `RABBITMQ_PASSWORD` 提供。

## 使用 Supervisor

先执行一次依赖安装、RabbitMQ 启动和拓扑初始化，再启动 Supervisor：

```bash
mkdir -p runtime/logs
uv run supervisord -c supervisor/supervisord.conf
uv run supervisorctl -c supervisor/supervisord.conf status
```

该配置分别守护 FastAPI、异步 Worker、定时 Worker 和唯一的 Beat。停止时先停 Beat，
再停两个 Worker：

```bash
uv run supervisorctl -c supervisor/supervisord.conf stop celery-beat
uv run supervisorctl -c supervisor/supervisord.conf stop celery-async-worker
uv run supervisorctl -c supervisor/supervisord.conf stop celery-scheduled-worker
uv run supervisorctl -c supervisor/supervisord.conf shutdown
```

Worker 并发数在对应的 `supervisor/programs/*.conf` 中配置。Beat 在一个部署环境中只能
运行一个实例。

## 开发新任务

完整固定流程见 [hiduck/doc/adding-tasks.md](hiduck/doc/adding-tasks.md)：

- 异步任务：参数模型 -> 普通业务函数 -> Task 薄包装 -> API 调用 publisher -> 测试。
- 定时任务：参数/业务函数 -> Task 薄包装 -> `celery_config.py` 调度项 -> 测试。
- 只有需要资源隔离时才新增队列；此时同步更新队列、路由和 Supervisor Worker。

常见启动问题见 [hiduck/doc/troubleshooting.md](hiduck/doc/troubleshooting.md)。

## 检查

```bash
uv run ruff check .
uv run pytest
uv run python -m compileall -q src app main.py
```

单元测试启用 Celery eager 模式，不需要 RabbitMQ；真实消息流仍需按“本地启动”章节做
一次集成验证。
