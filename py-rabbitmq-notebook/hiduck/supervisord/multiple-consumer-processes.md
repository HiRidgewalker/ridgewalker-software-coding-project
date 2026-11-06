# 多消费者进程、并行消费与日志隔离

本文说明：一个 RabbitMQ 项目有多个队列或消费压力变大时，应该如何划分消费者进程，以及如何让 Supervisord 管理这些进程。

> 当前项目只有一个 `order-created-consumer`，监听 `orders.created.queue`。本文的多个队列和多个实例配置是扩展方案，不会直接修改当前正在使用的 Supervisor 配置。

## 结论先行

| 场景 | 推荐做法 | 目的 |
|---|---|---|
| 不同队列、不同业务逻辑 | 每种业务创建独立消费者进程，并分别由 Supervisord 管理。 | 业务隔离、独立发布、独立重启和独立扩缩容。 |
| 同一队列、同一业务逻辑，但消息处理能力不足 | 为同一消费者配置多个实例，使用 `numprocs`。 | 提升并行消费能力。 |
| 单一消费者实例 | 使用一个独立日志文件。 | 简单观察和排查。 |
| 多个消费者实例 | 每个实例使用不同日志文件。 | 避免日志交错和日志轮转冲突。 |

不要为每条 RabbitMQ 消息临时创建一个操作系统进程。消费者应该是长期运行的进程，由 RabbitMQ 持续投递消息。

## 场景一：不同业务使用不同消费者进程

假设系统有三种事件：

```text
orders.created.queue       → 创建订单后的业务处理
payments.success.queue     → 支付成功后的业务处理
emails.queue               → 发送邮件
```

推荐的进程划分为：

```text
RabbitMQ
├── orders.created.queue
│   └── order-created-consumer 进程
├── payments.success.queue
│   └── payment-success-consumer 进程
└── emails.queue
    └── email-consumer 进程
```

这里的重点并不只是“日志分离”，而是业务隔离：

- 邮件服务异常或重启时，不会停止支付消息消费。
- 支付消费者消息积压时，可以只扩容支付消费者。
- 每类业务能设置不同的重试策略、停止等待时间、资源限制和告警规则。
- 日志按业务分开，排查时不必从混杂日志中筛选。

每一类消费者通常使用一个独立的 Supervisor 配置文件，例如：

```text
supervisor/programs/
├── order-created-consumer.conf
├── payment-success-consumer.conf
└── email-consumer.conf
```

`payment-success-consumer.conf` 的形态示例：

```ini
[program:payment-success-consumer]
directory=%(here)s/../..
command=%(here)s/../../.venv/bin/python -m app.payment_consumer
autostart=false
autorestart=true
stopsignal=TERM
stopwaitsecs=30
stopasgroup=true
killasgroup=true
stdout_logfile=%(here)s/../../runtime/logs/payment-success-consumer.log
stdout_logfile_maxbytes=1MB
stdout_logfile_backups=3
redirect_stderr=true
environment=PYTHONUNBUFFERED="1"
```

`[program:payment-success-consumer]` 中的名称就是管理命令使用的程序名：

```bash
uv run supervisorctl -c supervisor/supervisord.conf start payment-success-consumer
uv run supervisorctl -c supervisor/supervisord.conf status payment-success-consumer
uv run supervisorctl -c supervisor/supervisord.conf restart payment-success-consumer
```

交换机、队列和绑定关系仍应由 FastAPI 的启动阶段统一声明；消费者进程只负责消费已存在的队列。

## 场景二：同一业务通过多个实例并行消费

假设 `orders.created.queue` 消息量增加，而每条消息的处理逻辑完全相同。可以创建同一个消费者的多个实例：

```text
orders.created.queue
├── order-created-consumer_00
├── order-created-consumer_01
└── order-created-consumer_02
```

它们被称为**竞争消费者**。同一条消息只会被其中一个消费者处理；RabbitMQ 会把后续消息继续分发给可以接收消息的实例。

当前项目设置了：

```python
channel.basic_qos(prefetch_count=1)
```

这表示每个消费者实例最多同时保留一条“已投递但尚未确认”的消息。处理较慢的实例因为还有未确认消息，通常不会继续获得下一条消息；处理较快的实例会获得更多工作，分配较为合理。

### 使用 numprocs 的配置示例

以下是把当前单实例消费者扩展为三个实例的示例：

```ini
[program:order-created-consumer]
directory=%(here)s/../..
command=%(here)s/../../.venv/bin/python -m app.consumer

numprocs=3
process_name=%(program_name)s_%(process_num)02d

autostart=false
autorestart=true
startsecs=3
startretries=5
stopsignal=TERM
stopwaitsecs=10
stopasgroup=true
killasgroup=true

stdout_logfile=%(here)s/../../runtime/logs/order-created-consumer_%(process_num)02d.log
stdout_logfile_maxbytes=1MB
stdout_logfile_backups=3
redirect_stderr=true
environment=PYTHONUNBUFFERED="1"
```

两个新增字段的含义：

| 配置 | 含义 |
|---|---|
| `numprocs=3` | Supervisord 启动三个相同命令的消费者进程。 |
| `process_name=%(program_name)s_%(process_num)02d` | 给每个实例生成唯一名称，例如 `order-created-consumer_00`、`order-created-consumer_01`、`order-created-consumer_02`。 |

`%(process_num)02d` 会把实例编号格式化为两位数字，因此日志文件也会分别是：

```text
runtime/logs/order-created-consumer_00.log
runtime/logs/order-created-consumer_01.log
runtime/logs/order-created-consumer_02.log
```

启动和查看命令：

```bash
uv run supervisorctl -c supervisor/supervisord.conf start order-created-consumer:*
uv run supervisorctl -c supervisor/supervisord.conf status
```

预期可以看到：

```text
order-created-consumer:order-created-consumer_00    RUNNING
order-created-consumer:order-created-consumer_01    RUNNING
order-created-consumer:order-created-consumer_02    RUNNING
```

停止所有该消费者实例：

```bash
uv run supervisorctl -c supervisor/supervisord.conf stop order-created-consumer:*
```

这里的 `order-created-consumer:*` 是 Supervisor 的进程组写法：前半部分是 `[program:...]` 的名称，`*` 匹配它创建的全部实例。

## 为什么多实例不能共用同一个日志文件

单实例时，当前项目使用：

```ini
stdout_logfile=%(here)s/../../runtime/logs/order-created-consumer.log
```

如果只增加 `numprocs=3`，却继续让三个实例写入这个文件，会有两个问题：

1. 三个进程的日志行会交错，无法快速确定是哪一个实例处理了消息。
2. 当前启用了 `stdout_logfile_maxbytes=1MB` 和 `stdout_logfile_backups=3`。多个进程同时进行日志轮转会发生竞争，可能造成日志丢失、覆盖或轮转文件异常。

所以多实例配置必须将实例编号加入日志文件名：

```ini
stdout_logfile=%(here)s/../../runtime/logs/order-created-consumer_%(process_num)02d.log
```

查看全部实例的日志：

```bash
tail -f runtime/logs/order-created-consumer_*.log
```

在生产环境中，更常见的做法是让应用日志输出到标准输出，再由容器平台、系统日志服务或集中式日志系统统一收集；仍然不应让多个进程同时进行同一个本地日志文件的轮转。

## 并行消费前必须确认的业务条件

增加 `numprocs` 不只是改一个数字，还会改变处理顺序和并发程度。

### 1. 业务必须允许并发

同一个队列的不同消息可能被不同实例同时处理。若两条消息同时修改同一订单、库存或账户，业务代码需要使用数据库事务、锁、乐观并发控制等方式保证正确性。

### 2. 不能依赖全局消费顺序

单队列中消息按顺序入队，不代表多消费者并行处理后的业务完成顺序仍然一致。处理慢的消息可能晚于后入队的消息完成。

如果同一个订单必须严格顺序处理，常见做法包括：

- 保持单消费者，牺牲部分吞吐量换取简单的顺序语义。
- 根据 `order_id` 等业务键分片到不同队列，确保同一业务键始终进入同一分片。
- 在消费端通过版本号、状态机或数据库约束拒绝过期操作。

### 3. 业务操作必须幂等

RabbitMQ 的手动确认意味着：处理成功后才 `basic_ack`。如果业务已执行、但确认发送前消费者进程崩溃，消息会重投递给任一新实例。

因此数据库写入、扣款、发券、发邮件等操作应依据 `message_id` 或业务唯一键识别重复请求，做到重复消费也不会产生重复业务结果。

### 4. 不要让不同协议的消费者共享业务队列

当前消费者使用 Pika 消费自定义 JSON 消息。Celery Worker 消费的是 Celery 任务协议消息。两者不能直接一起监听同一个业务队列；应为它们使用各自的队列，或统一采用一种消息协议和消费方式。

## 配置变更后的生效步骤

完成配置修改后，先检查并应用变更：

```bash
uv run supervisorctl -c supervisor/supervisord.conf reread
uv run supervisorctl -c supervisor/supervisord.conf update
uv run supervisorctl -c supervisor/supervisord.conf status
```

`reread` 只读取并比较配置，`update` 才会创建、移除或重启受影响的进程。

在当前学习项目中，不要直接把现有 `order-created-consumer.conf` 修改为多实例后立即用于重要消息。建议先确认业务幂等性，并在测试消息上验证：

1. 三个实例都能进入 `RUNNING`。
2. 三个独立日志文件都能产生消费记录。
3. 多条消息会由不同实例处理。
4. 杀死其中一个实例后，Supervisor 只会重启该实例。
5. 未确认的消息会被 RabbitMQ 重投递，且不会造成重复业务结果。

## 选择方式速查

```text
是否是不同业务逻辑？
├── 是
│   └── 每个队列/业务使用独立消费者程序和独立 [program:...] 配置。
│
└── 否，是同一类业务但处理量不足？
    ├── 是
    │   └── 使用 numprocs 增加同一消费者实例，并为每个实例设置独立日志文件。
    │
    └── 否
        └── 保持单实例即可，优先保证业务正确性和可观察性。
```
