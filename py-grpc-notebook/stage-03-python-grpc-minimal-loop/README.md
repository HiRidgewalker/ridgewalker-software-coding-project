# 阶段三：进入 Python gRPC 最小闭环

这一阶段的目标是：把一个最小 gRPC 项目真正跑起来。

## 这一阶段必须完成的事情

你需要亲手完成：

- 一个 `proto` 文件
- Python 代码生成
- 一个 gRPC 服务端
- 一个 gRPC 客户端
- 一次完整调用跑通

## 建议学习顺序

1. 安装 `grpcio` 和代码生成工具
2. 写一个最简单的 `proto`
3. 生成 Python 文件
4. 实现服务端方法
5. 编写客户端调用
6. 成功返回结果

## 这一阶段只做什么

只做 `unary-unary`：

- 发一个请求
- 收一个响应

## 这一阶段先不碰什么

- 服务端流
- 客户端流
- 双向流
- 拦截器
- 认证鉴权
- 超时重试高级配置

## 阶段目标

你要达到下面这个状态：

- 知道 `proto` 怎么写
- 知道 Python 代码怎么生成
- 知道服务端实现写在哪里
- 知道客户端怎么发请求
- 知道返回对象怎么取字段

## 目录结构

```text
stage-03-python-grpc-minimal-loop/
├── proto/
│   └── user_service.proto
├── client.py
├── server.py
├── user_service_pb2.py
├── user_service_pb2_grpc.py
└── README.md
```

## 最小闭环示例

这一阶段继续使用你已经熟悉的 `UserService` / `GetUser`。

看 [proto/user_service.proto](./proto/user_service.proto)：

```proto
syntax = "proto3";

package stage3;

message UserRequest {
  int64 user_id = 1;
}

message UserReply {
  int64 user_id = 1;
  string name = 2;
  bool active = 3;
}

service UserService {
  rpc GetUser (UserRequest) returns (UserReply);
}
```

你可以把它读成：

- 客户端发一个 `UserRequest`
- 服务端返回一个 `UserReply`
- 方法名叫 `GetUser`

## 第一步：生成 Python 代码

在仓库根目录执行：

```bash
uv run python -m grpc_tools.protoc \
  -I ./stage-03-python-grpc-minimal-loop/proto \
  --python_out=./stage-03-python-grpc-minimal-loop \
  --grpc_python_out=./stage-03-python-grpc-minimal-loop \
  ./stage-03-python-grpc-minimal-loop/proto/user_service.proto
```

生成后你会得到：

- `user_service_pb2.py`
- `user_service_pb2_grpc.py`

它们的作用可以先这样理解：

- `user_service_pb2.py`：消息类
- `user_service_pb2_grpc.py`：服务端接口基类和客户端桩代码

## 第二步：服务端实现写在哪里

看 [server.py](./server.py)。

这一阶段你要重点知道的是：真正的业务逻辑写在服务类的方法里。

```python
class UserService(user_service_pb2_grpc.UserServiceServicer):
    def GetUser(self, request, context):
        return user_service_pb2.UserReply(
            user_id=request.user_id,
            name="Alice",
            active=True,
        )
```

这里表示：

- `proto` 已经声明了 `GetUser`
- 服务端现在把 `GetUser` 真正实现出来

## 第三步：客户端请求怎么发

看 [client.py](./client.py)。

核心代码是：

```python
request = user_service_pb2.UserRequest(user_id=1001)
response = stub.GetUser(request)
```

这就是最基础的 unary-unary 调用。

## 第四步：返回对象怎么取字段

客户端拿到 `response` 后，可以直接取字段：

```python
print(response.user_id)
print(response.name)
print(response.active)
```

这一步非常关键，因为它会让你真正建立“proto message 会变成 Python 对象”的感觉。

## 运行方式

### 1. 安装依赖

在仓库根目录执行：

```bash
uv sync
```

### 2. 生成代码

在仓库根目录执行：

```bash
uv run python -m grpc_tools.protoc \
  -I ./stage-03-python-grpc-minimal-loop/proto \
  --python_out=./stage-03-python-grpc-minimal-loop \
  --grpc_python_out=./stage-03-python-grpc-minimal-loop \
  ./stage-03-python-grpc-minimal-loop/proto/user_service.proto
```

### 3. 启动服务端

在仓库根目录执行：

```bash
uv run python stage-03-python-grpc-minimal-loop/server.py
```

### 4. 另开一个终端运行客户端

在仓库根目录执行：

```bash
uv run python stage-03-python-grpc-minimal-loop/client.py
```

你会看到类似输出：

```text
server started at 0.0.0.0:50052
response.user_id = 1001
response.name = Alice
response.active = True
```

## 这一阶段真正要记住的事

- `proto` 负责定义接口和消息
- `grpc_tools.protoc` 负责生成 Python 代码
- 服务端实现写在继承 `...Servicer` 的类里
- 客户端通过 `...Stub` 发请求
- 返回值不是字典，而是生成出来的消息对象

## 你完成这一阶段后，就已经真正跨过了分水岭

这时你已经不只是“知道 gRPC 是什么”，而是已经会：

- 写最小 `proto`
- 生成 Python 代码
- 实现一个 gRPC 方法
- 从客户端成功拿到响应字段

