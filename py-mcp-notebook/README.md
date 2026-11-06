# MCP Python 快速上手

这个目录是一个从零开始的 MCP 入门示例。目标不是覆盖全部规范，而是快速理解 MCP 的概念，并能用 Python 跑通一个本地 stdio Server、一个自写 Client，以及 MCP Inspector 调试流程。

## 你会学到什么

- MCP 如何把 AI 应用连接到外部上下文和工具。
- Host、Client、Server 三个角色分别负责什么。
- Tools、Resources、Prompts 三类能力的区别。
- 为什么本地入门优先选择 stdio 传输。
- 如何用 Python SDK 的 `FastMCP` 写一个最小可用 Server。

## 快速开始

安装依赖：

```bash
uv sync
```

运行自写客户端。它会自动通过 stdio 启动本地 MCP Server，然后列出并调用 tools、resources 和 prompts。

```bash
uv run python quickstart_client.py
```

如果你的环境不允许写入默认 `uv` 缓存目录，可以改用：

```bash
UV_CACHE_DIR=/tmp/uv-cache uv run python quickstart_client.py
```

用 MCP Inspector 可视化调试：

```bash
npx -y @modelcontextprotocol/inspector uv run python quickstart_server.py
```

运行测试：

```bash
uv run pytest
```

## 文件导览

- `quickstart_server.py`：一个最小 MCP Server，包含 tool、resource、prompt。
- `quickstart_client.py`：一个最小 MCP Client，演示初始化、列出能力、调用能力。
- `docs/01-learning-route.md`：15/30/60 分钟学习路线。
- `docs/02-core-concepts.md`：MCP 核心概念。
- `docs/03-example-walkthrough.md`：示例代码逐步讲解。
- `docs/04-debugging-and-troubleshooting.md`：调试方法和常见问题。
- `docs/05-tool-transport-choice.md`：MCP tool 在 stdio 和 Streamable HTTP 之间的选型建议。

## 最小心智模型

MCP 可以理解为 AI 应用和外部能力之间的一套标准协议：

- Host 是用户面对的 AI 应用，例如 IDE、桌面助手或聊天应用。
- Client 通常由 Host 创建，每个 Client 连接一个 MCP Server。
- Server 暴露能力，常见能力包括 tools、resources、prompts。
- Tools 用来执行动作，Resources 用来读取上下文，Prompts 用来复用提示词模板。

本仓库使用 stdio，因为它最适合本地开发：Client 启动 Server 进程，然后双方通过标准输入输出交换 JSON-RPC 消息。写 Server 时不要往 stdout 打普通日志，否则会污染协议数据。

## 官方资料

- MCP 文档：https://modelcontextprotocol.io/docs
- MCP Python SDK：https://github.com/modelcontextprotocol/python-sdk
- MCP Inspector：https://modelcontextprotocol.io/docs/tools/inspector
