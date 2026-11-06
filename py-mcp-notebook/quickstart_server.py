"""A tiny MCP stdio server for learning the core protocol concepts.

Run directly:
    uv run python quickstart_server.py

Or inspect it visually:
    npx -y @modelcontextprotocol/inspector uv run python quickstart_server.py
"""

from __future__ import annotations

from mcp.server.fastmcp import FastMCP


mcp = FastMCP("MCP Python Quickstart")


CONCEPTS: dict[str, str] = {
    "host": "Host 是用户直接使用的 AI 应用，例如 IDE、桌面助手或聊天应用。",
    "client": "Client 由 Host 创建，负责和某一个 MCP Server 建立一条协议连接。",
    "server": "Server 暴露外部能力，比如工具、资源和提示词模板，供 AI 应用按协议调用。",
    "tool": "Tool 表示模型可以请求执行的动作，适合计算、查询或调用外部系统。",
    "resource": "Resource 表示可读取的上下文数据，类似只读文件或数据记录。",
    "prompt": "Prompt 是可复用的提示词模板，用来把常见任务包装成结构化输入。",
    "stdio": "stdio 是最适合本地入门的传输方式，客户端通过标准输入输出和 server 通信。",
}


def add_numbers(a: int, b: int) -> int:
    """Return the sum of two integers."""
    return a + b


def explain_mcp_concept(name: str) -> str:
    """Return a short Chinese explanation for an MCP concept."""
    key = name.strip().lower()
    return CONCEPTS.get(
        key,
        f"暂时没有收录 {name!r}。可以先了解 host、client、server、tool、resource、prompt、stdio。",
    )


def build_learning_prompt(topic: str, level: str = "beginner") -> str:
    """Build a reusable learning prompt."""
    level_map = {
        "beginner": "零基础入门",
        "intermediate": "已经能跑通基础示例",
        "advanced": "准备设计真实 MCP 服务",
    }
    learner_level = level_map.get(level, level_map["beginner"])
    return (
        f"请面向一位{learner_level}的开发者，用中文解释 MCP 中的 {topic}。"
        "要求包含：一句话定义、典型使用场景、一个最小示例、一个常见误区。"
    )


@mcp.tool()
def add(a: int, b: int) -> int:
    """Add two integers."""
    return add_numbers(a, b)


@mcp.tool()
def explain_concept(name: str) -> str:
    """Explain one MCP concept in Chinese."""
    return explain_mcp_concept(name)


@mcp.resource("guide://overview")
def guide_overview() -> str:
    """Read the quick overview resource."""
    return (
        "# MCP 快速概览\n\n"
        "MCP 用统一协议把 AI 应用和外部上下文、工具连接起来。\n"
        "本示例用 stdio 运行一个本地 Server，并暴露 tools、resources 和 prompts。"
    )


@mcp.resource("guide://concept/{name}")
def guide_concept(name: str) -> str:
    """Read a concept explanation resource."""
    return explain_mcp_concept(name)


@mcp.prompt()
def mcp_learning_prompt(topic: str, level: str = "beginner") -> str:
    """Generate a Chinese learning prompt for an MCP topic."""
    return build_learning_prompt(topic, level)


if __name__ == "__main__":
    mcp.run(transport="stdio")
