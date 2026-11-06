# JSON-RPC Demo For Beginners

这是一个面向初学者的 JSON-RPC 学习项目，目标不是做一个功能很多的框架，而是用尽量少的代码，把 JSON-RPC 在实际开发中的关键点讲清楚、跑起来、测起来。

这个 Demo 选择了一个非常适合入门的组合：

- 使用 Python 标准库实现，不依赖第三方包。
- 使用 HTTP 作为传输层，便于用 `curl`、浏览器插件、Postman 之类的工具调试。
- 使用一个简单的 JSON-RPC dispatcher，让你直接看到请求是如何被解析、校验、分发和返回结果的。

## 你会学到什么

通过这个项目，你可以掌握以下内容：

- JSON-RPC 请求和响应的基本结构。
- `method`、`params`、`id`、`result`、`error` 各自的作用。
- 如何实现一个最小可用的 JSON-RPC 服务端。
- 如何编写客户端来调用 JSON-RPC 方法。
- 什么是 notification，以及它为什么没有返回值。
- 什么是 batch request，以及服务端如何批量处理。
- 在真实开发中，如何把 JSON-RPC 用在“命令式接口”而不是“资源式接口”上。

## 项目结构

```text
.
├── README.md
├── json-rpc常见问题.md
├── jsonrpc_demo
│   ├── __init__.py
│   ├── client.py
│   ├── dispatcher.py
│   └── server.py
└── tests
    └── test_dispatcher.py
```

各文件职责如下：

- `jsonrpc_demo/dispatcher.py`
  这是整个 Demo 的核心。它负责解析 JSON-RPC 请求、校验格式、查找方法、执行方法、封装响应。
- `jsonrpc_demo/server.py`
  这是一个基于 Python 标准库 HTTP 服务的 JSON-RPC 服务端，对外提供 `POST /rpc`。
- `jsonrpc_demo/client.py`
  这是一个简单客户端，可以直接向服务端发起 JSON-RPC 请求，帮助你理解客户端应该怎么构造消息。
- `tests/test_dispatcher.py`
  这里放的是核心单元测试，用来验证请求分发逻辑是否符合预期。

## 快速开始

### 1. 启动服务端

在项目根目录运行：

```bash
python3 -m jsonrpc_demo.server
```

默认会启动在：

```text
http://127.0.0.1:8000/rpc
```

如果你看到类似输出，说明服务已经启动：

```text
JSON-RPC server listening on http://127.0.0.1:8000/rpc
```

### 2. 使用内置客户端发送请求

另开一个终端，执行：

```bash
python3 -m jsonrpc_demo.client
```

这个客户端会演示多个请求：

- `ping`
- `add`
- `get_user`
- 调用不存在的方法
- notification
- batch request

### 3. 使用 curl 手动调试

这是最推荐初学者练手的方式，因为你能清楚看到请求体和响应体。

#### 示例 1：调用 `ping`

```bash
curl -X POST http://127.0.0.1:8000/rpc \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "method": "ping",
    "params": {},
    "id": 1
  }'
```

预期响应：

```json
{
  "jsonrpc": "2.0",
  "result": "pong",
  "id": 1
}
```

#### 示例 2：调用 `add`

```bash
curl -X POST http://127.0.0.1:8000/rpc \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "method": "add",
    "params": {
      "a": 3,
      "b": 5
    },
    "id": 2
  }'
```

#### 示例 3：获取用户信息

```bash
curl -X POST http://127.0.0.1:8000/rpc \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "method": "get_user",
    "params": {
      "user_id": 1
    },
    "id": 3
  }'
```

#### 示例 4：notification

notification 的特点是带 `method` 和 `params`，但不带 `id`。  
因为客户端不要求响应，所以服务端也不会返回 JSON-RPC 响应体。

```bash
curl -i -X POST http://127.0.0.1:8000/rpc \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "method": "notify_hello",
    "params": {
      "name": "Alice"
    }
  }'
```

这个 Demo 中，notification 通常会返回 HTTP `204 No Content`。

#### 示例 5：batch request

```bash
curl -X POST http://127.0.0.1:8000/rpc \
  -H "Content-Type: application/json" \
  -d '[
    {
      "jsonrpc": "2.0",
      "method": "ping",
      "params": {},
      "id": 10
    },
    {
      "jsonrpc": "2.0",
      "method": "add",
      "params": {
        "a": 10,
        "b": 20
      },
      "id": 11
    }
  ]'
```

## Demo 中实现了哪些方法

为了让初学者更容易理解，这个项目只放了少量方法：

- `ping`
  用来验证服务是否存活，返回 `"pong"`。
- `add`
  接收 `a` 和 `b`，返回两数之和。
- `get_user`
  根据 `user_id` 查询一个内置的模拟用户。
- `list_methods`
  返回当前支持的方法名列表。
- `notify_hello`
  一个通知型方法，用来演示 notification 场景。

这些方法故意设计得很简单，因为重点不是业务本身，而是 JSON-RPC 的调用方式和分发逻辑。

## 项目里体现了哪些 JSON-RPC 关键点

### 1. 单一入口

服务端只暴露一个入口：

```text
POST /rpc
```

这和 RESTful API 很不一样。REST 更强调不同资源路径，例如 `/users/1`、`/orders/2`；  
JSON-RPC 更强调“我调用哪个方法”，所以通常会统一走一个入口。

### 2. Dispatcher 是核心

在实际开发里，JSON-RPC 的核心往往不是 HTTP，而是 dispatcher。

dispatcher 负责做这些事情：

- 判断请求是不是合法 JSON。
- 判断是不是合法 JSON-RPC 2.0 消息。
- 找到 `method` 对应的 Python 函数。
- 把 `params` 交给函数执行。
- 把返回值包装成 `result`。
- 如果执行失败，把异常包装成 `error`。

只要你真正理解了 dispatcher，你就已经掌握了 JSON-RPC 服务端最核心的部分。

### 3. 错误返回是统一结构

JSON-RPC 不建议随意返回字符串错误，而应该统一返回：

```json
{
  "jsonrpc": "2.0",
  "error": {
    "code": -32601,
    "message": "Method not found"
  },
  "id": 123
}
```

这个 Demo 中实现了几类常见错误：

- Parse error
- Invalid Request
- Method not found
- Invalid params
- Internal error

另外，这个 Demo 也演示了一个简单的业务错误：

- `User not found`

这里特意没有复用 `Method not found`，因为“RPC 方法不存在”和“业务数据不存在”是两回事。  
这也是实际开发里很重要的一点：**协议错误** 和 **业务错误** 最好分开设计。

### 4. notification 没有返回值

如果请求没有 `id`，说明客户端不关心结果。  
这类请求通常用于“通知式动作”，例如：

- 记录日志
- 刷新缓存
- 告诉后台开始执行某个任务

### 5. batch request 可以一次发多个调用

batch request 是一个 JSON 数组。  
服务端需要逐个处理其中的请求，再把所有响应聚合成数组返回。  
如果其中某些请求是 notification，那么它们不会出现在返回结果里。

## 如何把这个 Demo 运用到实际开发中

这个 Demo 最适合帮助你迈出第一步。你可以在它基础上快速改造成下面这些真实场景：

### 1. 内部工具平台

把方法扩展成：

- `run_task`
- `deploy_service`
- `get_job_status`
- `cancel_job`

这类需求天然更像“方法调用”，非常适合 JSON-RPC。

### 2. 本地 CLI + Worker 通信

你可以保留 dispatcher 逻辑，只把 HTTP 传输层替换成：

- `stdin/stdout`
- 本地 socket
- 子进程通信

这样就能演变成一个本地工具链架构。

### 3. WebSocket 实时命令通道

如果你的业务需要长连接和双向通信，可以保留现有方法设计，再把传输层换成 WebSocket。

### 4. AI / Agent Tool 调用层

如果你在做 AI 工具调用系统，JSON-RPC 也很自然，因为很多工具本质上就是：

- 调某个方法
- 传入参数
- 拿到结构化结果

## 推荐的学习方式

建议不要只读代码，要边改边学。可以按下面顺序练习：

1. 先运行服务端和客户端，确认整个流程能跑通。
2. 手动用 `curl` 发送请求，观察响应。
3. 故意把 `method` 改错，观察错误码。
4. 自己新增一个方法，例如 `multiply`。
5. 再新增一个需要校验参数的方法，例如 `divide`，并处理除零错误。
6. 尝试给方法增加简单认证，例如 token 校验。
7. 最后思考是否需要把 HTTP 传输层替换成 WebSocket 或 stdio。

## 运行测试

在项目根目录执行：

```bash
python3 -m unittest discover -s tests -v
```

这些测试主要覆盖：

- 正常请求
- 方法不存在
- 参数错误
- notification
- batch request

## 下一步你可以继续做什么

如果你已经把这个 Demo 跑通，建议按这个顺序继续演进：

1. 给方法增加更严格的参数校验。
2. 增加认证和权限控制。
3. 增加日志和请求追踪。
4. 把内存数据替换成数据库。
5. 加入更真实的业务方法，例如任务执行、报表生成、异步任务状态查询。

## 总结

对于初学者来说，学习 JSON-RPC 最好的方式不是先记规范，而是先做一个最小可运行项目。  
这个 Demo 的重点就是帮助你完成这个过程：

- 看懂 JSON-RPC 消息结构
- 跑通一个最小服务端
- 理解 dispatcher 的工作机制
- 明白它在实际开发里适合哪些场景

当你把这个 Demo 改出两三个自己的方法后，JSON-RPC 基本就算真正入门了。
