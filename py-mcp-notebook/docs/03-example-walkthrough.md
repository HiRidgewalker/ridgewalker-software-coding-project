# 示例代码讲解

## Server 入口

`quickstart_server.py` 创建了一个 `FastMCP` 实例：

```python
mcp = FastMCP("MCP Python Quickstart")
```

这个对象负责注册能力，并在最后通过 stdio 运行：

```python
mcp.run(transport="stdio")
```

## Tool：让模型执行动作

示例里的 `add` 是最小 tool：

```python
@mcp.tool()
def add(a: int, b: int) -> int:
    return add_numbers(a, b)
```

Python 类型注解和 docstring 会帮助 SDK 生成工具描述。Client 可以通过 `list_tools()` 发现它，再通过 `call_tool()` 调用它。

## Resource：提供上下文

静态资源：

```python
@mcp.resource("guide://overview")
def guide_overview() -> str:
    ...
```

动态资源：

```python
@mcp.resource("guide://concept/{name}")
def guide_concept(name: str) -> str:
    ...
```

Resource 的重点是“读取上下文”。在真实项目里，它可以映射到文档、配置、知识库、日志或业务数据。

## Prompt：复用任务模板

```python
@mcp.prompt()
def mcp_learning_prompt(topic: str, level: str = "beginner") -> str:
    ...
```

Prompt 不执行外部动作，而是生成一段可复用的提示词。适合封装团队常用的分析、总结、生成任务。

## Client 调用路径

`quickstart_client.py` 用 `stdio_client` 启动本地 Server：

```python
async with stdio_client(server_parameters()) as (read, write):
    async with ClientSession(read, write) as session:
        await session.initialize()
```

初始化后，Client 分别演示：

- `list_tools()` 和 `call_tool()`
- `list_resources()` 和 `read_resource()`
- `list_prompts()` 和 `get_prompt()`

这就是 MCP 最核心的开发和验证闭环。
