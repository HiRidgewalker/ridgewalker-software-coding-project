# RabbitMQ 常用命令行命令

本文整理 RabbitMQ 单节点环境中常用的命令，重点覆盖交换机、队列、绑定、用户、权限和服务管理。

## 工具分工

RabbitMQ 常见命令工具不是只有 `rabbitmqctl` 一个。

| 工具 | 主要用途 |
|---|---|
| `rabbitmqctl` | 节点管理、用户管理、vhost 管理、权限管理、查看队列/交换机/绑定 |
| `rabbitmqadmin` | 通过 HTTP API 创建、删除、查看 exchange、queue、binding 等资源 |
| `rabbitmq-plugins` | 启用、关闭、查看插件 |
| `rabbitmq-diagnostics` | 节点状态检查、诊断、健康检查 |
| `systemctl` | Linux systemd 环境下启动、停止、重启 RabbitMQ 服务 |

简单记忆：

- 管节点、用户、权限：优先用 `rabbitmqctl`。
- 创建、删除交换机/队列/绑定：优先用 `rabbitmqadmin`。
- 管插件：用 `rabbitmq-plugins`。
- 看节点健康状态：用 `rabbitmq-diagnostics`。

## 前置说明

下面示例默认使用虚拟主机 `/`。

`rabbitmqadmin` v2 中，全局参数要写在命令组前面，例如：

```bash
rabbitmqadmin --vhost "/" queues list
```

而不是：

```bash
rabbitmqadmin queues list --vhost "/"
```

如果使用的是其他 vhost，例如 `events`，把 `--vhost "/"` 换成：

```bash
--vhost "events"
```

## 单节点常用终端命令

### 系统服务管理

适合通过系统包安装 RabbitMQ 的 Linux 环境。

```bash
# 启动 RabbitMQ
sudo systemctl start rabbitmq-server

# 停止 RabbitMQ
sudo systemctl stop rabbitmq-server

# 重启 RabbitMQ
sudo systemctl restart rabbitmq-server

# 查看服务状态
sudo systemctl status rabbitmq-server

# 设置开机自启
sudo systemctl enable rabbitmq-server

# 取消开机自启
sudo systemctl disable rabbitmq-server

# 查看服务日志
sudo journalctl -u rabbitmq-server -f
```

### RabbitMQ 进程管理

```bash
# 前台启动，适合调试
rabbitmq-server

# 后台启动
rabbitmq-server -detached

# 优雅关闭本机 RabbitMQ 节点
rabbitmqctl shutdown
```

### 节点状态和诊断

```bash
# 查看节点状态
rabbitmqctl status

# 查看更详细的诊断状态
rabbitmq-diagnostics status

# 检查命令行工具是否能连上 RabbitMQ 节点
rabbitmq-diagnostics ping

# 查看监听端口
rabbitmq-diagnostics listeners

# 查看环境配置
rabbitmq-diagnostics environment
```

### 管理插件

```bash
# 启用管理插件
sudo rabbitmq-plugins enable rabbitmq_management

# 查看插件列表
rabbitmq-plugins list

# 查看已启用插件
rabbitmq-plugins list --enabled
```

启用 `rabbitmq_management` 后，管理后台通常可以通过下面地址访问：

```text
http://localhost:15672
```

默认 AMQP 端口通常是：

```text
5672
```

管理后台 HTTP API 端口通常是：

```text
15672
```

### Docker 单节点示例

如果用 Docker 启动单节点 RabbitMQ，可以参考：

```bash
# 启动一个带管理后台的 RabbitMQ 容器
docker run -d \
  --name rabbitmq \
  -p 5672:5672 \
  -p 15672:15672 \
  rabbitmq:4-management

# 查看容器日志
docker logs -f rabbitmq

# 在容器内执行 rabbitmqctl
docker exec -it rabbitmq rabbitmqctl status

# 重启容器
docker restart rabbitmq

# 停止容器
docker stop rabbitmq
```

## 用户、虚拟主机与权限

### 用户管理

```bash
# 查看用户
rabbitmqctl list_users

# 创建用户
rabbitmqctl add_user app_user app_password

# 修改密码
rabbitmqctl change_password app_user new_password

# 设置用户标签，administrator 可以登录管理后台并拥有管理员能力
rabbitmqctl set_user_tags app_user administrator

# 删除用户
rabbitmqctl delete_user app_user
```

### 虚拟主机管理

vhost 可以理解为 RabbitMQ 内部的逻辑隔离空间。不同 vhost 中的交换机、队列、绑定互相隔离。

```bash
# 查看虚拟主机
rabbitmqctl list_vhosts

# 创建虚拟主机
rabbitmqctl add_vhost events

# 删除虚拟主机
rabbitmqctl delete_vhost events
```

### 权限管理

RabbitMQ 权限分为三类：

- `configure`：是否可以创建、删除、修改资源。
- `write`：是否可以向 exchange 发布消息。
- `read`：是否可以从 queue 消费消息。

```bash
# 给用户设置某个虚拟主机下的所有权限
rabbitmqctl set_permissions -p events app_user ".*" ".*" ".*"

# 查看某个虚拟主机下的权限
rabbitmqctl list_permissions -p events

# 查看某个用户拥有的权限
rabbitmqctl list_user_permissions app_user

# 清除用户在某个虚拟主机下的权限
rabbitmqctl clear_permissions -p events app_user
```

## 查看资源

这些查看命令既可以用 `rabbitmqctl`，也可以用 `rabbitmqadmin`。

### 使用 rabbitmqctl 查看

```bash
# 查看交换机
rabbitmqctl list_exchanges -p events name type durable auto_delete internal arguments

# 查看队列
rabbitmqctl list_queues -p events name durable messages_ready messages_unacknowledged consumers arguments

# 查看绑定关系
rabbitmqctl list_bindings -p events source_name source_kind destination_name destination_kind routing_key arguments

# 查看消费者
rabbitmqctl list_consumers -p events

# 查看连接
rabbitmqctl list_connections name user vhost peer_host peer_port state

# 查看通道
rabbitmqctl list_channels connection number user vhost consumer_count messages_unacknowledged
```

### 使用 rabbitmqadmin 查看

```bash
# 查看交换机
rabbitmqadmin --vhost "events" exchanges list

# 查看队列
rabbitmqadmin --vhost "events" queues list

# 查看某个队列详情
rabbitmqadmin --vhost "events" queues show --name "task.queue"

# 只查看队列的部分字段
rabbitmqadmin --vhost "events" queues show --name "task.queue" --columns "name,type,messages,consumers"

# 查看绑定关系
rabbitmqadmin --vhost "events" bindings list

# 查看消费者
rabbitmqadmin --vhost "events" consumers list
```

## 交换机操作

下面使用 `rabbitmqadmin` v2 语法。

### 创建直连交换机

`direct` 交换机要求消息的 `routing_key` 和队列绑定时的 `binding_key` 完全匹配。

```bash
rabbitmqadmin --vhost "events" exchanges declare \
  --name "log.direct.exchange" \
  --type "direct" \
  --durable true
```

### 创建广播交换机

`fanout` 交换机会广播到所有绑定队列，通常不关心 `routing_key`。

```bash
rabbitmqadmin --vhost "events" exchanges declare \
  --name "notice.fanout.exchange" \
  --type "fanout" \
  --durable true \
  --auto-delete false
```

### 创建主题交换机

`topic` 交换机会使用通配符匹配 `routing_key` 和 `binding_key`。

```bash
rabbitmqadmin --vhost "events" exchanges declare \
  --name "event.topic.exchange" \
  --type "topic" \
  --durable true
```

### 查看交换机

```bash
rabbitmqadmin --vhost "events" exchanges list

rabbitmqctl list_exchanges -p events name type durable auto_delete
```

### 删除交换机

```bash
rabbitmqadmin --vhost "events" exchanges delete --name "log.direct.exchange"
```

如果希望交换机不存在时也不报错：

```bash
rabbitmqadmin --vhost "events" exchanges delete --name "log.direct.exchange" --idempotently
```

## 队列操作

### 创建普通持久化队列

```bash
rabbitmqadmin --vhost "events" queues declare \
  --name "log.error.queue" \
  --type "classic" \
  --durable true \
  --auto-delete false
```

### 创建非持久化临时队列

适合本地测试，不适合重要业务消息。

```bash
rabbitmqadmin --vhost "events" queues declare \
  --name "temp.debug.queue" \
  --type "classic" \
  --durable false \
  --auto-delete true
```

### 查看队列

```bash
# 查看所有队列
rabbitmqadmin --vhost "events" queues list

# 查看某个队列详情
rabbitmqadmin --vhost "events" queues show --name "log.error.queue"

# 查看关心的字段
rabbitmqadmin --vhost "events" queues show \
  --name "log.error.queue" \
  --columns "name,type,messages,consumers"

# 使用 rabbitmqctl 查看队列消息情况
rabbitmqctl list_queues -p events name messages_ready messages_unacknowledged consumers
```

字段含义：

- `messages_ready`：队列中可投递但还没有投递给消费者的消息数。
- `messages_unacknowledged`：已经投递给消费者，但还没有 ack 的消息数。
- `consumers`：当前监听该队列的消费者数量。

### 清空队列

清空队列会删除队列中的消息，但不会删除队列本身。

```bash
rabbitmqadmin --vhost "events" queues purge --name "log.error.queue"
```

### 删除队列

```bash
rabbitmqadmin --vhost "events" queues delete --name "log.error.queue"
```

如果希望队列不存在时也不报错：

```bash
rabbitmqadmin --vhost "events" queues delete --name "log.error.queue" --idempotently
```

## 绑定操作

绑定关系决定交换机中的消息会进入哪些队列。

注意：

- 生产者发送消息时使用的是 `routing_key`。
- 队列绑定交换机时使用的是 `binding_key`。
- 在 `rabbitmqadmin` 的绑定命令里，参数名写作 `--routing-key`，但它表示的是这条绑定关系的匹配键，也就是前文说的 `binding_key`。

### 绑定直连交换机和队列

```bash
rabbitmqadmin --vhost "events" bindings declare \
  --source "log.direct.exchange" \
  --destination-type "queue" \
  --destination "log.error.queue" \
  --routing-key "error"
```

含义：

- `source`：源交换机。
- `destination-type`：目标类型，这里是 `queue`。
- `destination`：目标队列。
- `routing-key`：绑定关系上的匹配键，可以理解为 `binding_key`。

生产者发送消息时，如果使用：

```text
exchange = log.direct.exchange
routing_key = error
```

这条消息就会进入 `log.error.queue`。

### 绑定主题交换机和队列

```bash
rabbitmqadmin --vhost "events" bindings declare \
  --source "event.topic.exchange" \
  --destination-type "queue" \
  --destination "order.event.queue" \
  --routing-key "order.*"
```

这个绑定可以匹配：

```text
order.created
order.paid
order.cancelled
```

但不能匹配：

```text
user.created
order.created.email
```

### 查看绑定关系

```bash
rabbitmqadmin --vhost "events" bindings list

rabbitmqctl list_bindings -p events source_name source_kind destination_name destination_kind routing_key
```

### 删除绑定关系

删除绑定时，`source`、`destination-type`、`destination`、`routing-key` 必须和创建绑定时对应。

```bash
rabbitmqadmin --vhost "events" bindings delete \
  --source "log.direct.exchange" \
  --destination-type "queue" \
  --destination "log.error.queue" \
  --routing-key "error"
```

也可以使用 `exchanges unbind`：

```bash
rabbitmqadmin --vhost "events" exchanges unbind \
  --source "log.direct.exchange" \
  --destination-type "queue" \
  --destination "log.error.queue" \
  --routing-key "error"
```

## 可选：消息测试

`rabbitmqadmin` v2 主要用于资源管理和监控。如果只是想在命令行验证消息能否路由成功，可以直接调用管理插件提供的 HTTP API。

注意：HTTP API 发布消息效率不高，只适合临时验证，不适合正式业务生产消息。

```bash
# 发布一条消息到直连交换机
curl -u app_user:app_password \
  -H "content-type: application/json" \
  -X PUT \
  http://127.0.0.1:15672/api/exchanges/events/log.direct.exchange/publish \
  -d '{"properties":{},"routing_key":"error","payload":"{\"level\":\"error\",\"message\":\"disk almost full\"}","payload_encoding":"string"}'

# 从队列取一条消息，ack_requeue_false 表示取出后确认并删除
curl -u app_user:app_password \
  -H "content-type: application/json" \
  -X POST \
  http://127.0.0.1:15672/api/queues/events/log.error.queue/get \
  -d '{"count":1,"ackmode":"ack_requeue_false","encoding":"auto","truncate":50000}'
```

如果 vhost 是默认的 `/`，URL 中要写成 `%2F`：

```text
http://127.0.0.1:15672/api/queues/%2F/log.error.queue/get
```

如果当前环境使用的是旧版 `rabbitmqadmin` v1，也可以使用下面命令：

```bash
# 发布一条消息
rabbitmqadmin -V events publish \
  exchange=log.direct.exchange \
  routing_key=error \
  payload='{"level":"error","message":"disk almost full"}'

# 从队列取一条消息，requeue=false 表示取出后不重新放回队列
rabbitmqadmin -V events get \
  queue=log.error.queue \
  requeue=false
```

如果只有 `rabbitmqadmin` v2，也可以先用业务代码生产和消费消息，再用下面命令确认消息数量变化：

```bash
rabbitmqctl list_queues -p events name messages_ready messages_unacknowledged consumers
```

## 常见组合示例

下面完整演示一次 `direct exchange -> queue -> consumer` 所需的资源配置。

### 1. 创建虚拟主机

```bash
rabbitmqctl add_vhost events
```

### 2. 创建用户并授权

```bash
rabbitmqctl add_user app_user app_password
rabbitmqctl set_permissions -p events app_user ".*" ".*" ".*"
```

### 3. 创建交换机

```bash
rabbitmqadmin --vhost "events" exchanges declare \
  --name "log.direct.exchange" \
  --type "direct" \
  --durable true
```

### 4. 创建队列

```bash
rabbitmqadmin --vhost "events" queues declare \
  --name "log.error.queue" \
  --type "classic" \
  --durable true \
  --auto-delete false
```

### 5. 绑定交换机和队列

```bash
rabbitmqadmin --vhost "events" bindings declare \
  --source "log.direct.exchange" \
  --destination-type "queue" \
  --destination "log.error.queue" \
  --routing-key "error"
```

### 6. 查看配置结果

```bash
rabbitmqadmin --vhost "events" exchanges list
rabbitmqadmin --vhost "events" queues list
rabbitmqadmin --vhost "events" bindings list
```

### 7. 清理测试资源

删除顺序建议从绑定开始，再删除队列和交换机。

```bash
rabbitmqadmin --vhost "events" bindings delete \
  --source "log.direct.exchange" \
  --destination-type "queue" \
  --destination "log.error.queue" \
  --routing-key "error"

rabbitmqadmin --vhost "events" queues delete --name "log.error.queue"

rabbitmqadmin --vhost "events" exchanges delete --name "log.direct.exchange"

rabbitmqctl delete_vhost events
```

## 危险命令提醒

下面命令会删除数据或资源，执行前要确认目标 vhost、队列、交换机是否正确。

```bash
# 删除交换机
rabbitmqadmin --vhost "events" exchanges delete --name "log.direct.exchange"

# 删除队列，队列中的消息也会消失
rabbitmqadmin --vhost "events" queues delete --name "log.error.queue"

# 清空队列消息
rabbitmqadmin --vhost "events" queues purge --name "log.error.queue"

# 删除虚拟主机，会删除该虚拟主机下的交换机、队列、绑定关系、权限等
rabbitmqctl delete_vhost events
```

下面命令更危险，通常只在本地学习环境或明确要清空节点数据时使用：

```bash
# 先停止 RabbitMQ 应用
rabbitmqctl stop_app

# 清空节点数据，包括用户、虚拟主机、权限、持久化消息等
rabbitmqctl reset

# 重新启动 RabbitMQ 应用
rabbitmqctl start_app
```

不要在生产环境随意执行 `reset` 或 `force_reset`。

## 常用速查

```bash
# 帮助
rabbitmqctl help
rabbitmqadmin help
rabbitmq-diagnostics help

# 服务状态
sudo systemctl status rabbitmq-server
rabbitmqctl status
rabbitmq-diagnostics status

# 插件
sudo rabbitmq-plugins enable rabbitmq_management
rabbitmq-plugins list --enabled

# 用户和权限
rabbitmqctl list_users
rabbitmqctl list_vhosts
rabbitmqctl list_permissions -p events

# 交换机、队列、绑定
rabbitmqadmin --vhost "events" exchanges list
rabbitmqadmin --vhost "events" queues list
rabbitmqadmin --vhost "events" bindings list

# 队列消息数量
rabbitmqctl list_queues -p events name messages_ready messages_unacknowledged consumers
```

## 参考

- RabbitMQ CLI 文档：https://www.rabbitmq.com/docs/cli
- rabbitmqadmin v2 文档：https://www.rabbitmq.com/docs/management-cli
- RabbitMQ Management Plugin 文档：https://www.rabbitmq.com/docs/management
- RabbitMQ HTTP API 文档：https://www.rabbitmq.com/docs/http-api-reference
