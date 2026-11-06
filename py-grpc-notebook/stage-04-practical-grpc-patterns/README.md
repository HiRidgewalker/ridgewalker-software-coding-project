# 阶段四：补充“实际开发够用”的进阶点

这一阶段不是再讲“gRPC 是什么”，而是把最小闭环补成更接近实际开发的样子。

你已经在阶段三里跑通过：

- `proto`
- Python 代码生成
- 服务端
- 客户端
- 一次完整调用

所以这一阶段开始补“写代码时马上会遇到的问题”。

## 这一阶段怎么分

### 第一优先级

这些内容已经直接放进代码示例里：

- 多个接口怎么组织
- 多个 `message` 怎么拆分
- 常见标量类型与 Python 对应关系
- `repeated` 的使用
- 嵌套 `message`
- 错误处理与状态码基础
- 如何查看请求 / 响应结构

### 第二优先级

这些内容一部分放到了代码里，一部分放到了文档解释里：

- 超时
- `metadata`
- 异常返回
- 服务端并发处理的基本认识
- 项目目录如何组织

### 第三优先级

这些暂时不落代码，只在这里说明“现在为什么不学”：

- 流式 RPC
- 拦截器
- TLS
- 认证授权
- 负载均衡
- 服务发现
- 健康检查
- 生产环境部署

## 目录结构

```text
stage-04-practical-grpc-patterns/
├── proto/
│   ├── common.proto
│   ├── user_service.proto
│   └── order_service.proto
├── client_demo.py
├── inspect_messages.py
├── server.py
├── common_pb2.py
├── order_service_pb2.py
├── order_service_pb2_grpc.py
├── user_service_pb2.py
├── user_service_pb2_grpc.py
└── README.md
```

这套结构本身就在展示两个实践点：

- `proto` 不一定只写一个文件
- 一个服务进程里可以同时挂多个 service

## 代码里具体展示了什么

### 1. 多个接口怎么组织

这一阶段不是只放一个 `UserService`，而是放了两个 service：

- `UserService`
- `OrderService`

这样你会看到：

- 多个业务接口可以分不同 `proto`
- 也可以由同一个 gRPC 服务进程统一挂载

对应文件：

- [proto/user_service.proto](./proto/user_service.proto)
- [proto/order_service.proto](./proto/order_service.proto)
- [server.py](./server.py)

### 2. 多个 message 怎么拆分

共享消息放到了 [proto/common.proto](./proto/common.proto)：

- `Address`
- `Money`

然后其他 `proto` 文件通过 `import "common.proto";` 复用这些结构。

这比把所有消息都硬塞进一个 `proto` 文件更接近实际开发。

### 3. `repeated` 怎么用

代码里有两个很典型的例子：

- `UserReply.tags`
- `OrderReply.items`

它们分别表示：

- 一个用户可以有多个标签
- 一个订单可以有多个商品项

你会在客户端里看到如何遍历这些字段。

### 4. 嵌套 message 怎么用

[proto/user_service.proto](./proto/user_service.proto) 里定义了：

```proto
message UserReply {
  message Profile {
    string email = 1;
    Address address = 2;
  }
  ...
}
```

这表示：

- `Profile` 只服务于 `UserReply`
- 它没有必要被提升成一个全局顶级消息

这是嵌套 `message` 很常见的使用场景。

### 5. 错误处理和状态码基础

[server.py](./server.py) 里演示了两类基础错误：

- 参数不合法：`INVALID_ARGUMENT`
- 资源不存在：`NOT_FOUND`

客户端里通过捕获 `grpc.RpcError` 来读取：

- `exc.code()`
- `exc.details()`

这就是 gRPC 最基础、最常见的错误处理方式。

### 6. 如何查看请求 / 响应结构

[inspect_messages.py](./inspect_messages.py) 提供了两种查看方式：

1. 用 `DESCRIPTOR` 看字段名、字段编号、字段类型
2. 实例化消息后直接打印结构

这比只盯着生成代码读更高效。

## 运行方式

### 1. 生成代码

在仓库根目录执行：

```bash
uv run python -m grpc_tools.protoc \
  -I ./stage-04-practical-grpc-patterns/proto \
  --python_out=./stage-04-practical-grpc-patterns \
  --grpc_python_out=./stage-04-practical-grpc-patterns \
  ./stage-04-practical-grpc-patterns/proto/common.proto \
  ./stage-04-practical-grpc-patterns/proto/user_service.proto \
  ./stage-04-practical-grpc-patterns/proto/order_service.proto
```

### 2. 启动服务端

```bash
uv run python stage-04-practical-grpc-patterns/server.py
```

### 3. 运行客户端演示

```bash
uv run python stage-04-practical-grpc-patterns/client_demo.py
```

### 4. 查看消息结构

```bash
uv run python stage-04-practical-grpc-patterns/inspect_messages.py
```

## 第一优先级内容的详细解释

### 多个接口怎么组织

最小示例里经常只有一个 service，但真实项目里很快就会出现多个业务域。

这一阶段用两个 service 演示：

- 用户相关放 `UserService`
- 订单相关放 `OrderService`

你现在先记住一个简单原则：

- 同一类业务方法放进同一个 service
- 不同业务域分不同 `proto` / `service`

不要一开始就把所有 RPC 都塞进一个超级大的 service。

### 多个 message 怎么拆分

现在这套拆法是：

- 共享结构放 `common.proto`
- 用户接口放 `user_service.proto`
- 订单接口放 `order_service.proto`

这是一个非常适合入门的拆分方式，因为它足够简单，但已经有模块边界。

### 常见标量类型与 Python 对应关系

这一阶段先记住最常见的一小部分：

| proto 类型 | Python 里通常看到什么 |
| --- | --- |
| `string` | `str` |
| `bool` | `bool` |
| `int32` | `int` |
| `int64` | `int` |
| `repeated string` | 类列表字段，可像序列一样遍历 |
| `repeated message` | 消息对象列表 |

要点只有一个：

- Python 不区分 `int32` 和 `int64` 这两种独立整数类型
- 但在 `proto` 设计里，你仍然要明确自己表达的是哪一种

### `repeated` 的使用

`repeated` 表示“一个值变成多个值”。

例如：

```proto
repeated string tags = 5;
repeated Item items = 4;
```

它在 Python 侧看起来很像列表，但你最好把它理解成“protobuf 管理的重复字段容器”。

对当前阶段来说，先掌握两件事就够了：

- 可以直接赋初始值
- 可以遍历读取

### 错误处理与状态码基础

你现在不用背全部状态码，只需要先建立这两个最常见的映射：

- 请求参数不对：`INVALID_ARGUMENT`
- 要查的数据不存在：`NOT_FOUND`

这比直接抛普通 Python 异常更符合 gRPC 约定，因为客户端拿到的是明确的 RPC 状态。

### 如何查看请求 / 响应结构

很多初学者一开始喜欢只看生成后的 `*_pb2.py`，但那样会陷入“看得见代码，看不懂结构”。

更直接的方式是：

1. 先看 `proto`
2. 再用 `DESCRIPTOR` 看字段元信息
3. 最后实例化一个消息对象直接打印

这就是 [inspect_messages.py](./inspect_messages.py) 要解决的问题。

## 第二优先级内容的详细解释

### 超时

客户端调用 gRPC 方法时可以传 `timeout`：

```python
stub.SearchUsers(request, timeout=0.2)
```

如果服务端来不及返回，客户端会收到：

- `DEADLINE_EXCEEDED`

这一阶段你只要记住：

- 超时是客户端控制的
- 它是 RPC 调用边界的一部分
- 不要默认所有请求都无限等待

### metadata

`metadata` 可以理解成 gRPC 里的“附加键值对”。

它常被用来传：

- 请求链路 ID
- 调用方名称
- token
- 灰度标记

在本阶段代码里，客户端会传：

- `x-request-id`
- `client-name`

服务端则会把：

- `x-request-id`
- `served-by`

作为尾部 metadata 返回。

这能帮助你建立一个关键认识：

- 有些信息适合进 `message`
- 有些横切信息更适合进 `metadata`

### 异常返回

服务端不要把“业务错误”简单写成裸 `raise Exception(...)`。

对于当前阶段，更合适的做法是：

- 用 `context.abort(...)`
- 明确返回一个 gRPC 状态码和错误说明

这样客户端拿到的是标准化的 RPC 错误。

### 服务端并发处理的基本认识

[server.py](./server.py) 里使用的是：

```python
grpc.server(futures.ThreadPoolExecutor(max_workers=10))
```

你现在只需要先建立一个朴素认识：

- gRPC Python 服务端通常会交给线程池处理请求
- 所以你的服务逻辑不是天然“只会串行执行一次一个请求”
- 共享内存数据时要开始有并发意识

这一阶段的示例数据是只读的，所以没有加锁问题。

### 项目目录如何组织

当前阶段示例已经给出一个适合学习到小项目过渡的结构：

- `proto/`：只放协议文件
- `server.py`：服务端入口
- `client_demo.py`：客户端演示入口
- `inspect_messages.py`：辅助理解结构
- 生成代码和业务示例先放同级目录，便于学习时快速来回对照

等后面项目变大，再考虑：

- `generated/`
- `clients/`
- `services/`
- `schemas/`

但你现在还不需要为了“以后可能会大”而把目录提前设计得过重。

## 第三优先级为什么现在不落地

### 流式 RPC

它会显著增加心智负担，应该放在你对 unary-unary 已经非常稳之后。

### 拦截器

它适合解决日志、鉴权、链路追踪等横切问题，但前提是你已经有明确的基础调用链。

### TLS、认证授权、负载均衡、服务发现、健康检查、生产部署

这些都更偏“工程化和生产环境能力”。

它们重要，但不适合在“刚把 gRPC 用顺手”的阶段混进来一起学。

## 这一阶段学完后，你应该达到什么状态

你应该能自己说清楚这些事：

- 一个项目里可以有多个 service
- 公共消息可以拆到独立 proto 文件复用
- `repeated` 和嵌套 `message` 在 Python 中怎么表现
- 服务端如何返回标准 gRPC 错误
- 客户端如何读取状态码和错误详情
- 调用时如何加 `timeout` 和 `metadata`
- 如何快速查看请求 / 响应消息结构

