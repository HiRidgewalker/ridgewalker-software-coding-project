# 常见问题排查

## FastAPI 或 Worker 无法连接 RabbitMQ

确认容器健康、端口和 `.env` 一致：

```bash
docker compose ps
docker compose logs rabbitmq
uv run python -m src.client.celery_topology
```

修改 RabbitMQ 默认用户、密码或 vhost 后，已有 Docker volume 不会自动重建用户。开发
环境可明确确认数据可丢弃后执行 `docker compose down -v`，再重新启动。

## Worker 显示未注册任务

- 新任务放在现有 `async_task.py` 或 `scheduled_task.py` 时，重启对应 Worker。
- 新建任务模块时，把完整模块路径加入 `src/client/celery_config.py` 的 `TASK_IMPORTS`。
- 检查 Task 名称是否唯一且使用 `app.tasks.async.*` 或
  `app.tasks.scheduled.*` 前缀。

可查看注册结果：

```bash
uv run celery -A src.client.celery_config:celery_app inspect registered
```

## 消息进入了错误队列

检查 Task 的显式 `name` 是否匹配 `src/client/celery_config.py` 中的路由前缀。不要在路由
或业务代码里临时传 `queue`。RabbitMQ 管理页面可以检查 exchange binding 和队列消息数。

## Beat 重复发布任务

同一环境只能启动一个 Beat。确认没有使用 `celery worker -B`，并检查 Supervisor 之外
是否还残留手工启动的 Beat。Beat 不防止长任务重叠，重叠控制必须在业务层实现。

## Supervisor 启动失败

先确认执行过 `uv sync`，且 `runtime/logs` 存在：

```bash
mkdir -p runtime/logs
uv run supervisord -n -c supervisor/supervisord.conf
```

前台模式会直接显示配置路径、日志文件和子进程启动错误。生产部署时，Worker 的
`stopwaitsecs` 应大于最长任务正常执行时间。
