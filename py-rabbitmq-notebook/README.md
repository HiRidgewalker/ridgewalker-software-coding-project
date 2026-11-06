# FastAPI + RabbitMQ 直连交换机学习示例

这个示例把 RabbitMQ 的拓扑管理、消息发布、消息消费和进程守护拆开，便于观察各自职责。

```text
FastAPI 服务启动
  └── 声明 orders.direct、orders.created.queue、order.created 绑定关系

发布接口 POST /messages
  └── 发布消息到 orders.direct

Supervisor 进程守护器
  └── 守护独立的 order-created-consumer 进程
        └── 消费 orders.created.queue，并在成功后确认消息
```

`direct` 类型的直连交换机只做精确匹配：`routing_key=order.created` 才会匹配
`binding_key=order.created`。

## 项目结构

```text
main.py          # FastAPI 入口：启动初始化并注册路由
app/
  settings.py   # 统一配置
  topology.py   # 唯一声明交换机、队列和绑定关系的模块
  router.py     # 健康检查与消息发布路由
  consumer.py   # 独立消费者进程，不管理 RabbitMQ 拓扑
supervisor/
  supervisord.conf
  programs/order-created-consumer.conf
compose.yaml    # 本地 RabbitMQ（含管理控制台）
```

## 启动

1. 准备本地 RabbitMQ 连接配置：

```bash
cp .env.example .env
```

默认配置连接已经运行在本机的 RabbitMQ：`127.0.0.1:5672`，账号密码为
`admin / admin`。管理控制台：<http://127.0.0.1:15672>。

仓库中的 `compose.yaml` 仅作为没有 RabbitMQ 时的备用环境。当前本机已有容器时不要执行
`docker compose up`，以免发生端口冲突。

2. 安装项目依赖并启动接口服务。FastAPI 的启动阶段会统一声明交换机、队列和绑定关系；初始化失败时，接口服务不会就绪。

```bash
uv sync
uv run uvicorn main:app --host 127.0.0.1 --port 8000 --reload
```

3. 在另一个终端启动 Supervisor，并人工启动消费者：

```bash
uv run supervisord -c supervisor/supervisord.conf
uv run supervisorctl -c supervisor/supervisord.conf start order-created-consumer
uv run supervisorctl -c supervisor/supervisord.conf status
```

消费者不是由 HTTP 接口控制的资源。它由你显式启动，但运行中异常退出时会由
Supervisor 自动重启。

## 发布消息

```bash
curl -X POST http://127.0.0.1:8000/messages \
  -H 'content-type: application/json' \
  -d '{
    "routing_key": "order.created",
    "payload": {
      "order_id": "ORDER-1001",
      "user_id": 101,
      "amount": 99.9
    }
  }'
```

成功时返回 `202（已接受）`。消费者日志位于：

```bash
tail -f runtime/logs/order-created-consumer.log
```

向当前没有绑定关系的路由键发布消息会返回 `409（冲突）`，例如：

```bash
curl -X POST http://127.0.0.1:8000/messages \
  -H 'content-type: application/json' \
  -d '{"routing_key":"order.paid","payload":{"order_id":"ORDER-1001"}}'
```

之所以能识别这种情况，是因为发布端开启了发布确认机制，并使用 `mandatory=True`。

## 验证消息确认、自动重启和重投递

将 `.env` 中的 `CONSUMER_PROCESSING_SECONDS` 设为 `10`，重启消费者后发布一条消息。处理期间在另一个终端执行：

```bash
uv run supervisorctl -c supervisor/supervisord.conf pid order-created-consumer
kill -KILL <上一步输出的进程号>
uv run supervisorctl -c supervisor/supervisord.conf status
```

该消息尚未确认，RabbitMQ 会在连接关闭后重新入队；Supervisor 会创建新的消费者进程，日志中会再次看到该消息。

## 测试与停止

```bash
uv run python -m unittest discover -s tests -v
uv run supervisorctl -c supervisor/supervisord.conf stop order-created-consumer
uv run supervisorctl -c supervisor/supervisord.conf shutdown
```

如果使用了仓库提供的备用 Compose 环境，再执行 `docker compose down` 停止它。该命令会保留 RabbitMQ 数据卷；如需清空所有消息和数据，再自行执行 `docker compose down -v`。
