# 项目启动命令

以下命令均在项目根目录执行。启动前应完成依赖安装、`.env` 配置和 RabbitMQ 启动。

## 1. 启动 Web 服务

```bash
uv run uvicorn main:app --host 127.0.0.1 --port 8000
```

服务启动后可通过 <http://127.0.0.1:8000> 访问。

## 2. 启动 Celery Beat

```bash
mkdir -p runtime
uv run celery -A src.client.celery_client.celery_config:celery_app beat \
  --loglevel=INFO \
  --pidfile=runtime/celerybeat.pid \
  --schedule=runtime/celerybeat-schedule
```

同一套部署环境只能启动一个 Celery Beat 实例，否则定时任务会被重复发布。

## 3. 启动监听所有队列的单实例 Celery Worker

```bash
mkdir -p runtime
uv run celery -A src.client.celery_client.celery_config:celery_app worker \
  --queues=celery.async.queue,celery.scheduled.queue \
  --hostname=all-queues@%h \
  --concurrency=1 \
  --pidfile=runtime/celery-all-queues.pid \
  --loglevel=INFO
```

该命令只启动一个 Worker 实例，同时监听以下队列：

- `celery.async.queue`
- `celery.scheduled.queue`

`--concurrency=1` 表示该 Worker 同一时刻只执行一个任务。`--pidfile` 用于阻止同一项目目录在同一台主机上重复启动该 Worker 实例。
