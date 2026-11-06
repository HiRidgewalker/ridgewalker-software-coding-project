# MCP 学习路线

## 15 分钟：先跑起来

1. 执行 `uv sync` 安装依赖。
2. 执行 `uv run python quickstart_client.py`。
3. 观察输出里的 `Tools`、`Resources`、`Prompts`。
4. 打开 `quickstart_server.py`，找到 `@mcp.tool()`、`@mcp.resource()`、`@mcp.prompt()`。

目标：知道 MCP Server 能暴露三类能力，Client 可以按协议发现和调用它们。

## 30 分钟：理解角色

阅读 `docs/02-core-concepts.md`，重点理解：

- Host：用户正在使用的 AI 应用。
- Client：Host 内部负责协议连接的组件。
- Server：提供上下文、工具和提示词的进程或服务。
- stdio：本地进程间通信方式。

然后改一下 `quickstart_client.py` 中调用 `explain_concept` 的参数，例如改成 `server` 或 `prompt`，重新运行。

目标：把概念和代码调用路径对应起来。

## 60 分钟：开始改造

尝试给 `quickstart_server.py` 增加一个新的 tool：

```python
@mcp.tool()
def multiply(a: int, b: int) -> int:
    """Multiply two integers."""
    return a * b
```

再在 `quickstart_client.py` 中调用它：

```python
result = await session.call_tool("multiply", {"a": 6, "b": 7})
print(result.content[0].text)
```

目标：理解 MCP 的开发闭环是“定义能力、启动 server、由 client 发现和调用”。

## 后续方向

- 接入真实数据源，例如本地文件、数据库、内部 HTTP API。
- 尝试 Streamable HTTP 传输，让 Server 以远程服务形式运行。
- 给工具增加更严格的参数、错误处理和权限边界。
- 把 Server 配到支持 MCP 的 IDE 或桌面客户端中。
