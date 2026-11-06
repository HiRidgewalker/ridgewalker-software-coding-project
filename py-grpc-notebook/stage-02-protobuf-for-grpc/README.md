# 阶段二：学习 Protocol Buffers，但只学 gRPC 够用部分

这一阶段的目标不是“全面掌握 protobuf”，而是先掌握你马上会在 gRPC 里写到的那部分。

## 这一阶段优先学习什么

- `message`
- 字段类型
- `string`
- `int32` / `int64`
- `bool`
- `repeated`
- 字段编号的作用
- `service`
- `rpc`
- 请求消息 / 响应消息的定义方式
- 基本代码生成概念

## 这一阶段暂时不深究什么

- `oneof`
- `map`
- `enum` 的复杂设计
- 向前 / 向后兼容策略细节
- `optional` 演进历史
- 自定义 `option`
- 包管理和大型 proto 拆分策略

## 阶段目标

你要能看懂并自己写出这样的结构：

- 一个 `UserRequest`
- 一个 `UserReply`
- 一个 `UserService`
- 一个 `GetUser` 方法

也就是：先会“写接口描述”。

## 目录结构

```text
stage-02-protobuf-for-grpc/
├── proto/
│   └── user.proto
├── inspect_schema.py
├── user_pb2.py
├── user_pb2_grpc.py
└── README.md
```

## 先建立一个最小的 proto 视角

在这个阶段里，`proto` 文件主要做三件事：

1. 定义消息长什么样
2. 定义服务里有哪些方法
3. 作为代码生成的输入

所以你可以把 `proto` 理解成：

- 对消息结构的描述
- 对服务接口的描述
- 对客户端和服务端共同遵守的合同

## 核心示例

看 [proto/user.proto](./proto/user.proto)：

```proto
syntax = "proto3";

package stage2;

message UserRequest {
  int64 user_id = 1;
  bool include_tags = 2;
}

message UserReply {
  int64 user_id = 1;
  string name = 2;
  int32 age = 3;
  bool active = 4;
  repeated string tags = 5;
}

service UserService {
  rpc GetUser (UserRequest) returns (UserReply);
}
```

这份定义已经覆盖了你这一阶段最该熟悉的内容。

## 逐块理解这个 proto

### 1. `message` 是什么

`message` 用来定义一类数据结构。

例如：

```proto
message UserRequest {
  int64 user_id = 1;
  bool include_tags = 2;
}
```

它相当于在说：“请求用户信息时，需要哪些字段。”

### 2. 字段类型在干什么

这一阶段只先抓住最常见的几种：

- `string`：字符串
- `int32`：32 位整数
- `int64`：64 位整数
- `bool`：布尔值
- `repeated`：表示这是一个列表

例如：

```proto
string name = 2;
int32 age = 3;
bool active = 4;
repeated string tags = 5;
```

可以理解成：

- `name` 是字符串
- `age` 是整数
- `active` 是真假值
- `tags` 是字符串列表

### 3. 字段编号为什么存在

每个字段后面的数字不是装饰，而是字段编号。

例如：

```proto
int64 user_id = 1;
bool include_tags = 2;
```

这里的 `1`、`2` 是字段编号。

这一阶段你先记住这件事就够了：

- 字段名给人看
- 字段编号给 protobuf 编码和识别字段用

也就是说，`user_id = 1` 里的 `1` 非常重要，不能随便乱写。

## gRPC 里最关键的接口描述

### 1. 请求消息和响应消息

这一阶段先形成一个固定模式：

- 请求参数放进一个 `Request message`
- 返回结果放进一个 `Reply message`

例如：

```proto
message UserRequest {
  int64 user_id = 1;
  bool include_tags = 2;
}

message UserReply {
  int64 user_id = 1;
  string name = 2;
  int32 age = 3;
  bool active = 4;
  repeated string tags = 5;
}
```

### 2. `service` 和 `rpc`

在 gRPC 里，服务接口通常这样写：

```proto
service UserService {
  rpc GetUser (UserRequest) returns (UserReply);
}
```

你可以把它读成一句话：

- `UserService` 这个服务
- 提供了一个 `GetUser` 方法
- 输入是 `UserRequest`
- 输出是 `UserReply`

这就是最基础的 gRPC 接口描述。

## 代码生成概念

`proto` 文件不是只给人看，它还要被拿去生成代码。

在仓库根目录执行：

```bash
uv run python -m grpc_tools.protoc \
  -I ./stage-02-protobuf-for-grpc/proto \
  --python_out=./stage-02-protobuf-for-grpc \
  --grpc_python_out=./stage-02-protobuf-for-grpc \
  ./stage-02-protobuf-for-grpc/proto/user.proto
```

会生成两个文件：

- `user_pb2.py`：消息结构相关代码
- `user_pb2_grpc.py`：gRPC 服务和客户端桩相关代码

先不要把它们想得太复杂，你只需要知道：

- `message` 会变成 Python 里可直接实例化的类
- `service` / `rpc` 会变成服务端接口基类和客户端调用入口

## 用 Python 看 message 是怎么对应过来的

看 [inspect_schema.py](./inspect_schema.py)。

在仓库根目录执行：

```bash
uv run python stage-02-protobuf-for-grpc/inspect_schema.py
```

你会看到这个阶段的几个重点：

- `UserRequest` 可以像普通 Python 对象一样创建
- `UserReply` 里可以直接放 `repeated` 列表
- 生成代码里已经有 `UserServiceStub` 和 `UserServiceServicer`

## 这一阶段你应该能写出的 proto

你至少应该能自己写出下面这个结构：

```proto
syntax = "proto3";

package stage2;

message UserRequest {
  int64 user_id = 1;
}

message UserReply {
  int64 user_id = 1;
  string name = 2;
  int32 age = 3;
  bool active = 4;
}

service UserService {
  rpc GetUser (UserRequest) returns (UserReply);
}
```

如果你能自己不看资料写出这一版，就说明你已经达到了这个阶段的目标。

## 这一阶段真正要记住的事

- `message` 是数据结构定义
- 字段类型决定数据怎么表达
- `repeated` 表示列表
- 字段编号是 proto 里很重要的一部分
- gRPC 接口通常由 `service` + `rpc` + 请求消息 + 响应消息组成
- `proto` 写完以后，可以自动生成 Python 代码

## 下一阶段可以继续学什么

当你对“会写接口描述”已经有把握后，下一阶段可以继续进入：

- 一个服务里定义多个 RPC 方法
- 更复杂的消息结构
- 服务端如何真正实现 `GetUser`
- 客户端如何真正发起调用

## 补充：逐行理解 `stage-03` 的最小 gRPC proto

如果你已经看到 [stage-03-python-grpc-minimal-loop/proto/user_service.proto](../stage-03-python-grpc-minimal-loop/proto/user_service.proto)，可以用下面这份更细的方式去理解：

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

### `syntax = "proto3";` 是什么

这一行是在声明：这份 `.proto` 文件使用的是 `proto3` 语法版本。

你可以先把它理解成：

- 这是这份 proto 文件遵循的语法规则
- `protobuf` 有不同语法版本，常见的是 `proto2` 和 `proto3`
- 现在绝大多数新的 gRPC 教学和项目，默认都从 `proto3` 开始

对你当前阶段最重要的意义是：

- 你后面写 `message`、字段、`service`、`rpc` 时，都是按照 `proto3` 的规则在写
- 生成代码时，工具会按 `proto3` 的规则去解析这份文件

### `package stage3;` 是什么

这一行是在给这份 proto 里的定义放一个“命名空间”。

它的作用可以先这样理解：

- 避免不同 proto 文件里出现重名定义时互相冲突
- 让生成代码和 gRPC 方法的全名更清晰

例如这里的：

```proto
package stage3;
```

表示下面的 `UserRequest`、`UserReply`、`UserService` 都属于 `stage3` 这个包。

所以在底层标识里，它们更接近于：

- `stage3.UserRequest`
- `stage3.UserReply`
- `stage3.UserService`

你在生成后的 Python 文件里，也能看到类似 `.stage3.UserRequest` 这样的痕迹。

### `message UserRequest` 是什么

```proto
message UserRequest {
  int64 user_id = 1;
}
```

这部分是在定义“请求消息”的结构，也就是客户端调用 `GetUser` 时要发什么数据。

可以逐项拆开看：

- `message`：表示开始定义一个 protobuf 消息类型
- `UserRequest`：这个消息类型的名字
- `{ ... }`：消息内部有哪些字段

里面只有一个字段：

```proto
int64 user_id = 1;
```

它表示：

- 字段类型是 `int64`
- 字段名是 `user_id`
- 字段编号是 `1`

也就是：客户端请求一个用户时，需要提供一个用户 ID，而且这个 ID 用 64 位整数表示。

### `message UserReply` 是什么

```proto
message UserReply {
  int64 user_id = 1;
  string name = 2;
  bool active = 3;
}
```

这部分是在定义“响应消息”的结构，也就是服务端返回给客户端的数据长什么样。

这里有三个字段：

```proto
int64 user_id = 1;
```

- 返回的用户 ID
- 类型是 `int64`
- 字段编号是 `1`

```proto
string name = 2;
```

- 返回用户名字
- 类型是 `string`
- 字段编号是 `2`

```proto
bool active = 3;
```

- 返回用户是否激活
- 类型是 `bool`
- 字段编号是 `3`

你可以把整个 `UserReply` 理解成服务端返回的一条用户记录，只不过这里只保留了最基本的三个字段。

### 字段后面的 `= 1`、`= 2`、`= 3` 到底是什么

这些数字叫字段编号，也叫 field number。

例如：

```proto
int64 user_id = 1;
string name = 2;
bool active = 3;
```

这里的 `1`、`2`、`3` 不是默认值，也不是排序装饰，而是 protobuf 编码时真正使用的字段标识。

这一阶段先记住三件事：

- 字段名主要是给开发者看
- 字段编号主要是给 protobuf 序列化和反序列化使用
- 一个 `message` 内部，每个字段编号都必须唯一

所以字段编号一旦开始使用，就不应该随便改。

### `service UserService` 是什么

```proto
service UserService {
  rpc GetUser (UserRequest) returns (UserReply);
}
```

这里是在定义 gRPC 服务接口。

可以拆开理解：

- `service`：声明一个 gRPC 服务
- `UserService`：服务名
- `{ ... }`：服务里提供哪些 RPC 方法

也就是说，这里定义了一个叫 `UserService` 的服务。

### `rpc GetUser (UserRequest) returns (UserReply);` 是什么

这一行是整个 gRPC 接口定义里最关键的一句。

```proto
rpc GetUser (UserRequest) returns (UserReply);
```

可以逐段理解：

- `rpc`：声明这是一个远程调用方法
- `GetUser`：方法名
- `(UserRequest)`：请求参数类型
- `returns (UserReply)`：返回结果类型

把这一行翻译成自然语言就是：

- `UserService` 提供了一个 `GetUser` 方法
- 客户端调用这个方法时，要传入一个 `UserRequest`
- 服务端处理后，会返回一个 `UserReply`

如果换成接近 Python 函数签名的脑内模型，你可以把它先理解成：

```python
def GetUser(request: UserRequest) -> UserReply:
    ...
```

当然，gRPC 里的调用不是本地函数调用，但“输入一个请求对象，返回一个响应对象”这个理解方式非常适合入门。

### 整个 proto 合起来在表达什么

把这份 proto 从头到尾连起来读，就是：

1. 这是一份使用 `proto3` 语法的 protobuf 文件
2. 它属于 `stage3` 这个包
3. 它定义了一个请求消息 `UserRequest`
4. 它定义了一个响应消息 `UserReply`
5. 它定义了一个 gRPC 服务 `UserService`
6. 这个服务里有一个方法 `GetUser`
7. `GetUser` 接收 `UserRequest`，返回 `UserReply`

这就是一个最小可用的 gRPC 接口描述。

## 补充：逐项解释 `grpc_tools.protoc` 生成命令

下面这条命令的作用是：把 `.proto` 文件转换成 Python 可用的消息类和 gRPC 服务代码。

```bash
uv run python -m grpc_tools.protoc \
  -I ./stage-03-python-grpc-minimal-loop/proto \
  --python_out=./stage-03-python-grpc-minimal-loop \
  --grpc_python_out=./stage-03-python-grpc-minimal-loop \
  ./stage-03-python-grpc-minimal-loop/proto/user_service.proto
```

可以从左到右逐项看。

### `uv run`

- `uv` 是项目里用来管理 Python 环境和依赖的工具
- `run` 表示在当前项目的虚拟环境里执行后面的命令

这样做的好处是：

- 会优先使用项目里已经安装好的依赖
- 不容易和系统 Python 环境混在一起

### `python -m grpc_tools.protoc`

这一段表示：

- 使用 Python 模块方式运行 `grpc_tools.protoc`
- 它本质上是 `protoc` 的 Python 包装入口

这里的核心工具是：

- `grpc_tools.protoc`

它负责读取 `.proto` 文件，然后生成对应的 Python 代码。

你可以把它理解成：

- 输入：`user_service.proto`
- 输出：Python 版的消息类和 gRPC 接口代码

### `-I ./stage-03-python-grpc-minimal-loop/proto`

这里的 `-I` 可以理解成 include path，也就是“导入搜索路径”或“proto 文件查找路径”。

它告诉 `protoc`：

- 当你处理 `.proto` 文件时，到 `./stage-03-python-grpc-minimal-loop/proto` 目录里找相关 proto

这个参数很重要，因为：

- `protoc` 需要知道 proto 根目录在哪里
- 如果后面有 `import "other.proto"`，它也会从这些目录里找

在这个例子里，它的意思基本就是：

- `user_service.proto` 所在的 proto 根目录是 `stage-03-python-grpc-minimal-loop/proto`

### `--python_out=./stage-03-python-grpc-minimal-loop`

这个参数表示：

- 普通 protobuf 消息代码输出到 `./stage-03-python-grpc-minimal-loop` 目录

它主要生成的是：

- `user_service_pb2.py`

这个文件里通常包含：

- `UserRequest`
- `UserReply`
- 描述符等 protobuf 相关代码

你以后创建消息对象时，主要会用到这个文件。

例如：

```python
import user_service_pb2

request = user_service_pb2.UserRequest(user_id=1001)
```

### `--grpc_python_out=./stage-03-python-grpc-minimal-loop`

这个参数表示：

- gRPC 相关代码输出到 `./stage-03-python-grpc-minimal-loop` 目录

它主要生成的是：

- `user_service_pb2_grpc.py`

这个文件里通常包含：

- `UserServiceStub`
- `UserServiceServicer`
- `add_UserServiceServicer_to_server(...)`

它们分别用于：

- 客户端发起调用
- 服务端实现接口
- 把服务注册到 gRPC server

也就是说：

- `--python_out` 更偏向“消息结构代码”
- `--grpc_python_out` 更偏向“RPC 调用代码”

### `./stage-03-python-grpc-minimal-loop/proto/user_service.proto`

这部分是命令最后真正要处理的输入文件。

它表示：

- 这次要拿来生成代码的 proto 文件是 `user_service.proto`

所以整条命令的意思就是：

- 在当前项目环境中运行 protobuf/gRPC 代码生成工具
- 告诉工具 proto 根目录在哪里
- 把普通 protobuf Python 代码输出到指定目录
- 把 gRPC Python 代码输出到指定目录
- 输入文件是 `user_service.proto`

### 运行完后会生成什么

运行完成后，通常会生成两个最核心的文件：

- `user_service_pb2.py`
- `user_service_pb2_grpc.py`

你可以先这样记：

- `_pb2.py`：消息定义对应的 Python 代码
- `_pb2_grpc.py`：gRPC 服务端和客户端调用相关代码

## 你可以怎样把“proto 定义”和“生成命令”连起来理解

把这两部分连起来看，流程其实很简单：

1. 你先写 `user_service.proto`
2. 里面定义消息和服务接口
3. 再运行 `grpc_tools.protoc`
4. 工具根据这份合同生成 Python 代码
5. 服务端和客户端都基于这份生成代码开发

所以 `.proto` 文件不是普通注释文档，而是整个 gRPC 通信合同的源头。
