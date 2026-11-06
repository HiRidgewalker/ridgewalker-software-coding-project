# learning-grpc-notebook

使用 Python + `uv` 分阶段学习 gRPC 与 Protocol Buffers。

环境约定：

- 整个仓库共用一个顶层 `.venv`
- 只在仓库根目录执行一次 `uv sync`
- 每个阶段只放学习内容，不再单独创建虚拟环境

当前阶段：

- [stage-01-minimal-cognition](./stage-01-minimal-cognition/)：建立最小认知，理解 RPC、gRPC、proto 文件分别是什么，以及最基础的调用链路。
- [stage-02-protobuf-for-grpc](./stage-02-protobuf-for-grpc/)：只学习 gRPC 场景里马上会用到的 Protocol Buffers 内容，重点练习接口描述。
- [stage-03-python-grpc-minimal-loop](./stage-03-python-grpc-minimal-loop/)：进入 Python gRPC 最小闭环，完成 proto、代码生成、服务端、客户端和一次完整调用。
- [stage-04-practical-grpc-patterns](./stage-04-practical-grpc-patterns/)：补充实际开发够用的进阶点，包括多接口组织、消息拆分、错误处理、metadata、timeout 和结构查看。
