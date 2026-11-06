# 调试与常见问题

## 使用 MCP Inspector

执行：

```bash
npx -y @modelcontextprotocol/inspector uv run python quickstart_server.py
```

Inspector 会启动一个可视化调试界面。你可以在里面查看 Server 暴露的 tools、resources、prompts，并手动调用它们。

## 自写 Client 验证

执行：

```bash
uv run python quickstart_client.py
```

如果它能列出能力并成功调用 `add`，说明 stdio Server 和 Python SDK 的基本链路已经通了。

如果当前环境不允许写入默认 `uv` 缓存目录，可以使用：

```bash
UV_CACHE_DIR=/tmp/uv-cache uv run python quickstart_client.py
```

## 常见问题

### 找不到 `uv`

先确认：

```bash
uv --version
```

如果没有安装，可以参考 uv 官方安装方式，或把 `quickstart_client.py` 中的启动命令换成你自己的 Python 环境命令。

### stdout 被污染

stdio 模式下，stdout 是 MCP 协议通道。不要在 Server 中使用 `print()` 输出普通日志。需要调试时，优先用 Inspector、自写 Client，或者把日志写到 stderr。

### Inspector 启动慢

第一次运行 `npx -y @modelcontextprotocol/inspector ...` 会下载 npm 包。网络慢时会等待更久。Server 本身仍然可以先用 `uv run python quickstart_client.py` 验证。

### 修改 Server 后 Client 没变化

stdio 模式下 Client 每次运行都会重新启动 Server。确认你保存了文件，并重新执行 `uv run python quickstart_client.py`。

### Tool 参数报错

MCP SDK 会根据函数签名校验参数。比如 `add(a: int, b: int)` 需要两个整数参数：

```python
await session.call_tool("add", {"a": 2, "b": 40})
```

缺参数、参数名写错或类型不匹配都可能失败。
