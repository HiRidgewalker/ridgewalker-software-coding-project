# MCP 核心概念

## MCP 是什么

MCP，全称 Model Context Protocol，是一套让 AI 应用连接外部上下文和工具的开放协议。它解决的问题是：不同 AI 应用不用为每个数据源或工具都写一套专用集成，而是通过统一协议发现和调用能力。

## 三个角色

Host 是用户直接使用的 AI 应用，例如 IDE、聊天应用或桌面助手。

Client 是 Host 内部创建的协议客户端。一个 Client 通常维护到一个 MCP Server 的连接，负责初始化、能力发现和请求调用。

Server 是能力提供方。它可以运行在本地，也可以作为远程服务，负责暴露 tools、resources 和 prompts。

## 三类常见能力

Tools 表示可以执行的动作。它们可能是纯计算，也可能访问文件、数据库或外部 API。模型通常会在需要行动时请求调用 tool。

Resources 表示可读取的上下文。它们更像只读数据，例如文档、配置、日志、数据库记录或某个动态 URI 下的数据。

Prompts 表示可复用的提示词模板。它们把常见任务封装成结构化输入，让 Host 或用户更容易复用。

## 传输方式

stdio 是本地入门最简单的方式。Client 启动 Server 子进程，双方通过标准输入输出交换协议消息。这个方式适合本地开发、IDE 集成和桌面应用。

Streamable HTTP 更适合远程服务。Server 作为 HTTP 服务运行，Client 通过网络连接它，适合团队共享、部署和跨机器访问。

## 一个请求会发生什么

1. Client 启动或连接 Server。
2. Client 发送初始化请求。
3. 双方确认协议版本和能力。
4. Client 请求列出 tools、resources 或 prompts。
5. Host 或用户选择能力后，Client 发送调用请求。
6. Server 返回结构化结果。

## 入门时最容易混淆的点

- MCP 不等于模型本身，它是模型应用和外部能力之间的协议层。
- Tool 不是普通函数暴露这么简单，它需要可被协议发现、描述和调用。
- Resource 适合提供上下文，不适合表达“执行动作”。
- stdio Server 的 stdout 是协议通道，不要用 `print()` 输出调试日志。
