# 阶段一：建立最小认知

这一阶段只解决三件事：

1. 什么是 RPC
2. gRPC 和普通 HTTP API 的关系
3. proto 文件在 gRPC 里扮演什么角色

## 一句话结论

- RPC：像调用本地函数一样调远程服务
- gRPC：一种高性能 RPC 框架
- Protocol Buffers：定义接口和消息结构的方式，同时也是序列化格式

## 这一阶段不深究

- HTTP/2 细节
- 四种流式通信细节
- 底层连接复用
- 性能优化原理

## 这一阶段的核心脑图

```text
写 proto
  ↓
生成 Python 代码
  ↓
服务端实现接口
  ↓
客户端调用接口
```

## 目录结构

```text
stage-01-minimal-cognition/
├── proto/
│   └── hello.proto
├── hello_pb2.py
├── hello_pb2_grpc.py
├── client.py
├── server.py
└── README.md
```

## 你在这一阶段要建立的理解

### 1. RPC 是什么

RPC 的目标是：让你调用远端服务时，写起来像在调用一个普通函数。

本地函数是这样：

```python
result = say_hello("grpc")
```

远端 RPC 调用在使用体验上尽量接近：

```python
response = stub.SayHello(request)
```

差别只是这个函数真正执行在另一台进程甚至另一台机器上。

### 2. gRPC 和普通 HTTP API 的关系

它们都属于“客户端请求服务端，服务端返回结果”的通信方式。

- 普通 HTTP API 常见形式是：`GET /users/1`、`POST /orders`
- gRPC 常见形式是：调用一个明确的方法，比如 `Greeter.SayHello`

你可以把它理解成：

- HTTP API 更像“访问 URL 资源”
- gRPC 更像“调用远程对象的方法”

这一阶段只需要建立这个感受，不需要立刻深入协议细节。

### 3. proto 文件扮演什么角色

`proto` 文件是整个 gRPC 交互的合同。

它定义两类内容：

1. 服务接口长什么样
2. 请求和响应消息长什么样

在这个阶段里，`proto/hello.proto` 定义的是：

- 服务：`Greeter`
- 方法：`SayHello`
- 请求消息：`HelloRequest`
- 响应消息：`HelloReply`

然后我们会根据这个 `proto` 文件生成 Python 代码：

- `hello_pb2.py`：消息结构
- `hello_pb2_grpc.py`：gRPC 服务与客户端桩代码

## 最小示例的调用链路

### 第一步：写 proto

见 [proto/hello.proto](./proto/hello.proto)。

### 第二步：生成 Python 代码

在仓库根目录运行：

```bash
uv run python -m grpc_tools.protoc \
  -I ./stage-01-minimal-cognition/proto \
  --python_out=./stage-01-minimal-cognition \
  --grpc_python_out=./stage-01-minimal-cognition \
  ./stage-01-minimal-cognition/proto/hello.proto
```

这一步不是“手写业务代码”，而是“根据合同自动生成通信代码”。

### 第三步：服务端实现接口

见 [server.py](./server.py)。

重点看这段逻辑：

```python
class Greeter(hello_pb2_grpc.GreeterServicer):
    def SayHello(self, request, context):
        return hello_pb2.HelloReply(message=f"Hello, {request.name}!")
```

这表示：

- `proto` 里声明过 `SayHello`
- 现在由服务端真正把这个方法实现出来

### 第四步：客户端调用接口

见 [client.py](./client.py)。

重点看这段逻辑：

```python
stub = hello_pb2_grpc.GreeterStub(channel)
response = stub.SayHello(hello_pb2.HelloRequest(name="grpc learner"))
```

你可以把它理解成“调用远程函数 `SayHello`”。

这里的客户端额外关闭了 HTTP 代理：

```python
channel_options = [("grpc.enable_http_proxy", 0)]
with grpc.insecure_channel("127.0.0.1:50051", options=channel_options) as channel:
    ...
```

这样做是为了避免本机代理环境干扰本地 gRPC 示例。

## 运行方式

### 1. 安装依赖

在仓库根目录执行：

```bash
uv sync
```

### 2. 启动服务端

在仓库根目录执行：

```bash
uv run python stage-01-minimal-cognition/server.py
```

### 3. 另开一个终端运行客户端

在仓库根目录执行：

```bash
uv run python stage-01-minimal-cognition/client.py
```

如果你当前就在 `stage-01-minimal-cognition/` 目录下，也可以直接执行同样的 `uv run` 命令，`uv` 会向上找到仓库根目录的项目配置。

你会看到类似输出：

```text
server started at 0.0.0.0:50051
response from server: Hello, grpc learner!
```

## 这一阶段你真正要记住的事

- gRPC 不是先写 URL，而是先定义服务方法
- `proto` 不是注释文档，而是生成代码的源头
- 服务端和客户端都围绕同一个 `proto` 合同协作
- 最小闭环就是：定义接口 -> 生成代码 -> 实现接口 -> 发起调用

## 下一阶段可以继续学什么

当你把这一阶段跑通之后，下一阶段再进入这些内容会更自然：

- `repeated`、嵌套消息、枚举
- 多个 RPC 方法如何组织
- 生成出来的 Python 文件到底提供了哪些类
- gRPC 的四种通信模式
