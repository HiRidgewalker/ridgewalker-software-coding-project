# 从零使用 Supervisord：本项目消费者进程管理指南

本文面向第一次接触 Supervisord 的读者，结合本项目实际文件说明：它解决什么问题、如何安装和启动、配置文件怎么写、如何日常管理进程，以及出现问题时如何排查。

## 先建立三个概念

`Supervisor` 是一套 Unix 进程管理工具的统称；日常使用时会接触到三个名字：

| 名称 | 是什么 | 在本项目中的职责 |
|---|---|---|
| `supervisord` | 常驻运行的守护进程，即进程管理器本身。 | 启动、停止、监控并在需要时重启消费者。 |
| `supervisorctl` | 与 `supervisord` 通信的命令行客户端。 | 查看状态，手动启动、停止、重启消费者。 |
| `supervisord.conf` | 进程管理器的配置文件。 | 定义控制通道、日志、PID 文件，以及要载入的程序配置。 |

可以把它们理解为：`supervisord` 是管理员，`supervisorctl` 是你发给管理员的控制台命令，配置文件则是管理员的工作清单。

> 本示例运行在 Linux、macOS 或 WSL 等具备 Unix 信号和 Unix Socket 的环境中。Windows 原生环境建议通过 WSL 使用本项目。

## 它在本项目中解决什么问题

本项目有三个相互独立的进程/服务：

```text
FastAPI 服务（main.py）
  ├── 启动时统一声明 RabbitMQ 交换机、队列和绑定关系
  └── 接收 POST /messages，并向交换机发布消息

RabbitMQ 服务
  └── 保存、路由并投递消息

order-created-consumer 消费者进程（python -m app.consumer）
  └── 消费 orders.created.queue，处理成功后手动确认消息
```

Supervisord 只管理最后一个消费者进程：

```text
你执行 supervisorctl start order-created-consumer
                  ↓
supervisord 创建消费者子进程
                  ↓
消费者连接 RabbitMQ 并开始消费
                  ↓
进程异常退出 ─────────→ supervisord 按 autorestart=true 自动重启
```

它**不管理 FastAPI，也不管理 RabbitMQ 容器**。这是刻意的职责划分：

- FastAPI 是开发时可通过 `uvicorn --reload` 频繁重启的 Web 服务。
- RabbitMQ 是独立的消息代理，本机已有容器负责运行它。
- 消费者是长期后台进程，最需要“异常退出后恢复运行”的守护能力。

消费者本身也不会声明交换机、队列或绑定关系；这些拓扑资源由 FastAPI 的生命周期启动阶段统一创建。故而推荐顺序是：**RabbitMQ → FastAPI → Supervisord → 消费者**。

## 本项目的文件结构

```text
supervisor/
├── supervisord.conf                         # supervisord 主配置
└── programs/
    └── order-created-consumer.conf           # 一个受管消费者的配置

runtime/
├── supervisor.sock                           # 本地控制 Socket，运行时生成
├── supervisord.pid                           # supervisord 的进程号，运行时生成
└── logs/
    ├── supervisord.log                       # supervisord 自身日志
    └── order-created-consumer.log             # 消费者标准输出和错误日志
```

`runtime/` 中的 Socket、PID 和日志都属于运行产物，已在 `.gitignore` 中忽略，不应提交到 Git。

## 安装

### 本项目的推荐方式：使用 uv

项目已经在 `pyproject.toml` 中声明了 `supervisor` 依赖。因此在项目根目录执行一次：

```bash
uv sync
```

`uv` 会创建或更新 `.venv` 虚拟环境，并把 `supervisord`、`supervisorctl` 安装进去。验证安装：

```bash
uv run supervisord --version
uv run supervisorctl --help
```

之后，始终使用 `uv run` 执行命令，可以确保使用的就是本项目锁定版本，而不是系统中可能存在的其他版本。

### 不使用 uv 时的通用安装方式

如果是独立学习环境，也可以安装到某个 Python 虚拟环境：

```bash
python -m venv .venv
. .venv/bin/activate
python -m pip install supervisor
supervisord --version
```

本项目不建议使用 `sudo pip install` 把它装到系统 Python：这会混淆依赖来源，也可能影响系统工具。生产环境通常由操作系统的软件包管理器、容器镜像或专门的 Python 环境来安装。

## 配置文件的通用语法

Supervisor 使用 INI 风格的文本配置文件。基本形态是：

```ini
# 井号或分号可作为注释
[配置段名称]
配置项=值
```

几个需要记住的规则：

1. `[名称]` 表示一个配置段。`[program:订单消费者]` 这类形式中，冒号后的部分是程序名称。
2. 大多数配置写成 `键=值`；不要把命令行参数单独换成配置项。
3. `%(here)s` 是 Supervisor 的路径替换变量，表示“**当前这份配置文件所在的目录**”。因此它不会依赖你从哪个目录执行命令。
4. 如果配置值本身要使用百分号，写成 `%%`，避免被当作变量替换标记。
5. 配置中出现的 `TERM`、`RUNNING`、`stdout` 等英文是 Supervisor、Unix 和日志流的固定术语，不可随意翻译或改名。

例如，消费者配置文件位于 `supervisor/programs/`，所以其中的：

```ini
directory=%(here)s/../..
```

会得到项目根目录；而 `command` 中的 `%(here)s/../../.venv/bin/python` 也能稳定定位到项目虚拟环境的 Python。

## 解读主配置：supervisor/supervisord.conf

当前文件完整内容如下：

```ini
[unix_http_server]
file=%(here)s/../runtime/supervisor.sock
chmod=0700

[supervisord]
logfile=%(here)s/../runtime/logs/supervisord.log
pidfile=%(here)s/../runtime/supervisord.pid
childlogdir=%(here)s/../runtime/logs

[rpcinterface:supervisor]
supervisor.rpcinterface_factory=supervisor.rpcinterface:make_main_rpcinterface

[supervisorctl]
serverurl=unix://%(here)s/../runtime/supervisor.sock

[include]
files=%(here)s/programs/*.conf
```

### [unix_http_server]：本地控制通道

```ini
[unix_http_server]
file=%(here)s/../runtime/supervisor.sock
chmod=0700
```

- `[unix_http_server]`：开启 Unix Socket 控制端点。它不是 HTTP Web 服务；名字中的 `http` 是 Supervisor 的历史命名。
- `file=...`：Socket 文件的位置。本项目把它放到 `runtime/supervisor.sock`，避免污染系统目录。
- `chmod=0700`：只允许当前文件所有者读、写和连接该 Socket。由于任何能连接控制 Socket 的用户都可管理进程，这是一项本地访问保护。

`supervisorctl` 后续就是通过这个 Socket 与 `supervisord` 通信的。

### [supervisord]：守护进程自身的运行信息

```ini
[supervisord]
logfile=%(here)s/../runtime/logs/supervisord.log
pidfile=%(here)s/../runtime/supervisord.pid
childlogdir=%(here)s/../runtime/logs
```

- `logfile`：记录 Supervisord 自己的日志，例如启动、加载配置、拉起或重启子进程等。它不是消费者业务日志。
- `pidfile`：写入 Supervisord 自己的进程号，用于识别它是否已在运行。
- `childlogdir`：没有为子进程显式指定日志文件时，Supervisor 放置自动生成子进程日志的目录。本项目为消费者指定了独立日志文件，但仍将这个默认目录限制在 `runtime/logs/`。

### [rpcinterface:supervisor]：启用控制接口

```ini
[rpcinterface:supervisor]
supervisor.rpcinterface_factory=supervisor.rpcinterface:make_main_rpcinterface
```

这段注册 Supervisor 内置的 RPC 控制接口。`supervisorctl` 的 `status`、`start`、`stop` 等命令都依赖它。缺少此段时，即使 Socket 文件存在，也无法进行正常的进程管理。

`rpcinterface:supervisor` 中的 `supervisor` 是接口名称；右侧 Python 路径是 Supervisor 内置工厂函数，必须保持原样。

### [supervisorctl]：命令行客户端连接到哪里

```ini
[supervisorctl]
serverurl=unix://%(here)s/../runtime/supervisor.sock
```

- `serverurl`：告诉 `supervisorctl` 连接地址。
- `unix://`：表示使用 Unix Socket，而非开放 TCP 端口。
- 此地址必须与 `[unix_http_server]` 中的 `file` 指向同一个文件。

因此本项目的每一条控制命令都带上同一个配置文件：

```bash
uv run supervisorctl -c supervisor/supervisord.conf status
```

其中 `-c` 的通用语法是 `-c <配置文件路径>`。它让 `supervisorctl` 确定要连接哪个 Supervisord 实例。

### [include]：按目录加载受管程序

```ini
[include]
files=%(here)s/programs/*.conf
```

- `files` 接受文件路径或通配符。
- `*.conf` 会匹配 `supervisor/programs/` 下的每个 `.conf` 文件。
- 新增一个消费者、定时任务或其他后台程序时，通常只需在该目录新建一个 `[program:名称]` 配置文件，无需把所有配置塞进主文件。

## 解读消费者配置：supervisor/programs/order-created-consumer.conf

当前配置如下：

```ini
[program:order-created-consumer]
directory=%(here)s/../..
command=%(here)s/../../.venv/bin/python -m app.consumer
autostart=false
autorestart=true
startsecs=3
startretries=5
stopsignal=TERM
stopwaitsecs=10
stopasgroup=true
killasgroup=true
stdout_logfile=%(here)s/../../runtime/logs/order-created-consumer.log
stdout_logfile_maxbytes=1MB
stdout_logfile_backups=3
redirect_stderr=true
environment=PYTHONUNBUFFERED="1"
```

### 程序身份、目录与启动命令

```ini
[program:order-created-consumer]
directory=%(here)s/../..
command=%(here)s/../../.venv/bin/python -m app.consumer
```

- `[program:order-created-consumer]`：声明一个受管程序，`order-created-consumer` 就是后续 `start`、`stop`、`status` 使用的进程名。
- `directory`：启动命令前先切换到的工作目录。这里是项目根目录，确保 `app.consumer` 可以被正确导入，`.env` 也能按项目约定读取。
- `command`：真正启动子进程的命令。它直接使用 `.venv/bin/python`，不依赖当前 Shell 是否激活了虚拟环境；`-m app.consumer` 表示把 `app.consumer` 当作 Python 模块运行。

注意：`command` 不是 Shell 脚本。不要随意写 `source .venv/bin/activate && ...`、管道符或复杂重定向；如确实需要 Shell 功能，应明确使用 `bash -c '...'`，并谨慎处理引号和信号转发。

### 启动与自动重启策略

```ini
autostart=false
autorestart=true
startsecs=3
startretries=5
```

| 配置 | 含义 | 本项目为什么这样设定 |
|---|---|---|
| `autostart=false` | Supervisord 自身启动后，不自动启动该程序。 | 必须先由 FastAPI 初始化 RabbitMQ 拓扑，再由人手动启动消费者。 |
| `autorestart=true` | 进程从 `RUNNING` 状态退出后，无论退出码是否为 0，都尝试自动重启。 | 消费者意外退出后应尽快恢复，不让队列长期无人消费。 |
| `startsecs=3` | 新进程持续运行满 3 秒，才被判定为启动成功并进入 `RUNNING`。 | 能区分“刚启动就连接 RabbitMQ 失败”和“真正运行起来”。 |
| `startretries=5` | 启动期间连续失败最多重试 5 次，随后进入 `FATAL`。 | 防止配置错误或 RabbitMQ 不可用时无限高速创建进程。 |

`autostart=false` 不等于无法启动，它只影响 Supervisord 刚启动的那一刻；之后仍可随时执行 `supervisorctl start order-created-consumer`。

### 停止策略与优雅退出

```ini
stopsignal=TERM
stopwaitsecs=10
stopasgroup=true
killasgroup=true
```

当你执行 `stop` 时，Supervisor 的实际流程是：

```text
supervisorctl stop order-created-consumer
       ↓
supervisord 发送 SIGTERM
       ↓
消费者的 _request_stop() 调用 channel.stop_consuming()
       ↓
start_consuming() 退出，finally 关闭 RabbitMQ 连接
       ↓
10 秒内退出：正常停止
10 秒仍未退出：发送 SIGKILL 强制结束
```

各项含义：

- `stopsignal=TERM`：停止时先发 `SIGTERM`。当前消费者已注册该信号的处理函数，因此能够停止接收新消息并释放连接。
- `stopwaitsecs=10`：发送 `SIGTERM` 后最多等待 10 秒。
- `stopasgroup=true`：向消费者所在的整个进程组发送正常停止信号；如果消费者以后创建子进程，它们不会被遗漏。
- `killasgroup=true`：等待超时后的 `SIGKILL` 也发送给整个进程组。

`SIGKILL` 不可被程序捕获，届时 `finally` 也没有执行机会。所以应让 `stopwaitsecs` 大于“单条消息最长处理时间 + 余量”。例如单条业务处理最长可能为 30 秒，应将其调整到至少 40 秒，然后执行 `reread` 和 `update` 使新配置生效。

消费者使用手动确认（`basic_ack`）。在确认前连接断开时，RabbitMQ 会把未确认消息重新入队并投递给重启后的消费者，故真实业务逻辑必须保持幂等。

### 日志与环境变量

```ini
stdout_logfile=%(here)s/../../runtime/logs/order-created-consumer.log
stdout_logfile_maxbytes=1MB
stdout_logfile_backups=3
redirect_stderr=true
environment=PYTHONUNBUFFERED="1"
```

- `stdout_logfile`：消费者写到标准输出的内容保存到这个文件。本项目的 Python 日志默认输出到标准错误，但下一项会将其合并进来。
- `redirect_stderr=true`：把标准错误重定向到标准输出，因此异常堆栈和普通日志都在 `order-created-consumer.log`。
- `stdout_logfile_maxbytes=1MB`：单个日志文件最大 1 MB。
- `stdout_logfile_backups=3`：轮转时最多保留 3 份旧文件，例如 `.1`、`.2`、`.3`，避免日志无限增长。
- `environment=PYTHONUNBUFFERED="1"`：只为这个子进程设置环境变量，使 Python 不缓冲输出；日志会更快落到文件，便于实时查看。

`environment` 的语法是用逗号分隔的 `键="值"` 对，例如：

```ini
environment=PYTHONUNBUFFERED="1",APP_ENV="development"
```

它只影响当前 `[program:...]` 启动的进程，不会修改你的终端环境或系统全局环境。

## 第一次完整启动

以下命令都在**项目根目录**执行。开始前确保本地 RabbitMQ 容器已经运行，且 `.env` 中账号密码与当前项目一致。

### 1. 安装依赖

```bash
uv sync
```

### 2. 启动 FastAPI，并等待 RabbitMQ 拓扑就绪

打开第一个终端：

```bash
uv run uvicorn main:app --host 127.0.0.1 --port 8000 --reload
```

看到“RabbitMQ 拓扑已就绪”日志后再继续。此步骤会声明直连交换机、队列及 `order.created` 绑定关系。

### 3. 启动 Supervisord

打开第二个终端：

```bash
uv run supervisord -c supervisor/supervisord.conf
```

默认会以守护进程方式运行，命令返回并不代表失败。确认它已启动：

```bash
uv run supervisorctl -c supervisor/supervisord.conf status
```

首次预期看到：

```text
order-created-consumer    STOPPED    未启动
```

这是正常的，因为配置中的 `autostart=false` 要求人工启动消费者。

想在当前终端前台运行并观察 Supervisord 自身输出，可用：

```bash
uv run supervisord -n -c supervisor/supervisord.conf
```

`-n` 表示不转入后台，适合学习和排错；它与后台方式二选一，不要同时运行两份 Supervisord。

### 4. 人工启动消费者

```bash
uv run supervisorctl -c supervisor/supervisord.conf start order-created-consumer
uv run supervisorctl -c supervisor/supervisord.conf status order-created-consumer
```

等待超过 `startsecs=3` 后，预期状态类似：

```text
order-created-consumer    RUNNING   pid 12345, uptime 0:00:03
```

### 5. 发布一条测试消息

```bash
curl -X POST http://127.0.0.1:8000/messages \
  -H 'content-type: application/json' \
  -d '{
    "routing_key": "order.created",
    "payload": {
      "order_id": "ORDER-20260802-001",
      "user_id": 10001,
      "product_name": "RabbitMQ 实战课程",
      "quantity": 1,
      "amount": 99.9
    }
  }'
```

查看消费者日志：

```bash
tail -f runtime/logs/order-created-consumer.log
```

## supervisorctl：管理进程的命令语法

在本项目中统一使用下面的前缀：

```bash
uv run supervisorctl -c supervisor/supervisord.conf <命令> [参数]
```

其中：

- `<命令>` 是 `status`、`start`、`stop`、`restart` 等动作。
- `[参数]` 通常是程序名 `order-created-consumer`。
- `all` 代表所有受管程序；当前项目只有一个消费者，但多个程序时会很方便。

### 最常用命令

| 目的 | 命令 |
|---|---|
| 查看所有程序状态 | `uv run supervisorctl -c supervisor/supervisord.conf status` |
| 查看某个消费者状态 | `uv run supervisorctl -c supervisor/supervisord.conf status order-created-consumer` |
| 启动消费者 | `uv run supervisorctl -c supervisor/supervisord.conf start order-created-consumer` |
| 停止消费者 | `uv run supervisorctl -c supervisor/supervisord.conf stop order-created-consumer` |
| 重启消费者 | `uv run supervisorctl -c supervisor/supervisord.conf restart order-created-consumer` |
| 获取消费者 PID | `uv run supervisorctl -c supervisor/supervisord.conf pid order-created-consumer` |
| 启动所有程序 | `uv run supervisorctl -c supervisor/supervisord.conf start all` |
| 停止所有程序 | `uv run supervisorctl -c supervisor/supervisord.conf stop all` |
| 关闭 Supervisord 及其管理的进程 | `uv run supervisorctl -c supervisor/supervisord.conf shutdown` |

### 查看日志和帮助

```bash
# 持续查看消费者的标准输出日志；本项目已把标准错误合并到此日志
uv run supervisorctl -c supervisor/supervisord.conf tail -f order-created-consumer stdout

# 直接跟踪日志文件，效果相同且可查看历史内容
tail -f runtime/logs/order-created-consumer.log

# 查看 Supervisord 自己的日志，例如启动失败原因
tail -n 100 runtime/logs/supervisord.log

# 列出当前配置中可用的受管程序
uv run supervisorctl -c supervisor/supervisord.conf avail

# 进入交互控制台；可输入 status、start 等命令，以 exit 退出
uv run supervisorctl -c supervisor/supervisord.conf

# 查看完整命令帮助
uv run supervisorctl -c supervisor/supervisord.conf help
```

### 修改配置后的标准流程

修改 `supervisor/programs/order-created-consumer.conf` 后，不能只保存文件，正在运行的 Supervisord 不会自动读取它。请按顺序执行：

```bash
# 读取磁盘上的新配置，并报告新增、修改、删除的程序
uv run supervisorctl -c supervisor/supervisord.conf reread

# 应用上一步发现的变化；必要时新增、删除或重启对应程序
uv run supervisorctl -c supervisor/supervisord.conf update

# 确认最终状态
uv run supervisorctl -c supervisor/supervisord.conf status
```

`reread` 只做“发现变化”，不实际改变运行中的进程；`update` 才真正应用变化。

如果修改的是主配置中的 Socket、PID、日志等 `[supervisord]` 级别设置，则需要更谨慎地重启 Supervisord 本身。学习环境可先停止它，再用 `supervisord -c ...` 重新启动；不要在不理解影响时直接使用 `reload`，因为它会中断 Supervisor 管理的进程。

## 如何理解 status 输出

`status` 常见状态及含义：

| 状态 | 含义 | 常见处理 |
|---|---|---|
| `STOPPED` | 当前未运行；可能是从未启动或人工停止。 | 执行 `start`。 |
| `STARTING` | 已创建进程，但尚未通过 `startsecs` 的稳定期。 | 等待几秒再查。 |
| `RUNNING` | 已稳定运行。 | 正常状态。 |
| `BACKOFF` | 进程启动后很快退出，Supervisor 正在按重试策略再次尝试。 | 检查消费者日志、RabbitMQ 和 `.env`。 |
| `EXITED` | 进程已退出，但未被继续重启。 | 查看退出原因和重启策略。 |
| `STOPPING` | Supervisor 已发出停止信号，正在等待进程退出。 | 等待不超过 `stopwaitsecs`；过久则检查业务处理耗时。 |
| `FATAL` | 启动连续失败次数超过 `startretries`，Supervisor 不再重试。 | 修复配置或连接问题后执行 `start`。 |

## 验证自动重启与消息重投递

### 验证消费者被自动重启

先确认消费者正在运行，然后查看其 PID：

```bash
uv run supervisorctl -c supervisor/supervisord.conf pid order-created-consumer
```

在另一个终端向该 PID 发送终止信号：

```bash
kill -TERM <消费者进程号>
```

由于本项目设置了 `autorestart=true`，Supervisor 会重新创建消费者。再次执行 `status` 或 `pid`，可以看到新的 PID。

不要把这个测试与 `supervisorctl stop` 混淆：后者是管理员明确要求停止，Supervisor 会将进程保持在 `STOPPED`，不会自动重启。

### 验证未确认消息会重投递

为了观察处理期间的故障恢复，可暂时将 `.env` 里的 `CONSUMER_PROCESSING_SECONDS` 设为 `40`，然后执行：

```bash
uv run supervisorctl -c supervisor/supervisord.conf restart order-created-consumer
```

发布一条消息后，在它完成 `basic_ack` 前结束消费者进程。RabbitMQ 会在连接断开后将未确认消息重新入队，Supervisor 重启消费者后会再次收到它；日志中的“是否重投递”会显示为 `True`。

实验结束后应将等待时间改回 `0` 并重启消费者。生产业务不能仅依赖“只会消费一次”：消息重投递是正常的可靠性机制，业务写入、扣款、发邮件等动作应以 `message_id` 或业务唯一键实现幂等。

## 常见故障排查

### 1. `supervisorctl` 提示无法连接

依次检查：

```bash
# 是否有 Supervisord 进程
ps -ef | rg '[s]upervisord'

# 控制 Socket 是否存在
ls -l runtime/supervisor.sock

# 读取 Supervisord 自身日志
tail -n 100 runtime/logs/supervisord.log
```

常见原因：尚未启动 `supervisord`、`-c` 指向了错误配置文件、Socket 路径两处配置不一致，或上次异常退出留下了旧 Socket/PID 文件。

处理旧 Socket/PID 前，必须先用 `ps` 确认没有正在运行的 Supervisord；确认后才可以清理**明确属于本项目的** `runtime/supervisor.sock` 与 `runtime/supervisord.pid`，再重新启动。

### 2. `status` 一直是 BACKOFF 或 FATAL

先看最直接的两份日志：

```bash
tail -n 100 runtime/logs/order-created-consumer.log
tail -n 100 runtime/logs/supervisord.log
```

再检查：

- RabbitMQ 容器是否正在运行，且端口 `5672` 可连接。
- `.env` 中 `RABBITMQ_USER`、`RABBITMQ_PASSWORD`、`RABBITMQ_VHOST` 是否正确。
- FastAPI 是否先完成“RabbitMQ 拓扑已就绪”。
- `command` 中的 `.venv/bin/python` 是否存在；必要时重新运行 `uv sync`。
- 消费者配置改动后是否执行过 `reread` 和 `update`。

修复问题后，手动重新发起启动：

```bash
uv run supervisorctl -c supervisor/supervisord.conf start order-created-consumer
```

### 3. 消费者日志没有新内容

检查顺序：

1. `status` 是否为 `RUNNING`。
2. FastAPI 是否成功发布消息，而不是返回 `409` 或 `503`。
3. 请求体 `routing_key` 是否为当前绑定的 `order.created`。
4. RabbitMQ 管理控制台中，`orders.created.queue` 的消息是否堆积。
5. 使用 `tail -f runtime/logs/order-created-consumer.log` 重新观察日志。

### 4. 为什么手动 stop 后没有自动重启

这是预期行为。`autorestart=true` 用来应对进程自行异常/退出；`supervisorctl stop` 是管理者明确要求停止，Supervisor 会尊重它并让状态停留在 `STOPPED`。需要恢复时再执行 `start`。

## 日常最短操作清单

```bash
# 1. 启动 FastAPI（另开终端执行）
uv run uvicorn main:app --host 127.0.0.1 --port 8000 --reload

# 2. 启动进程管理器
uv run supervisord -c supervisor/supervisord.conf

# 3. 启动并检查消费者
uv run supervisorctl -c supervisor/supervisord.conf start order-created-consumer
uv run supervisorctl -c supervisor/supervisord.conf status

# 4. 查看消费者日志
tail -f runtime/logs/order-created-consumer.log

# 5. 结束学习后依次停止消费者和进程管理器
uv run supervisorctl -c supervisor/supervisord.conf stop order-created-consumer
uv run supervisorctl -c supervisor/supervisord.conf shutdown
```

掌握这份清单后，再回头阅读“配置语法”和“消费者配置”两节，会更容易把每个配置项与实际命令、进程状态对应起来。
