"""A small MCP client that launches quickstart_server.py over stdio."""

from __future__ import annotations

import asyncio
import sys
from pathlib import Path

from mcp.client.session import ClientSession
from mcp.client.stdio import StdioServerParameters, stdio_client
from mcp.types import AnyUrl


ROOT = Path(__file__).resolve().parent


def server_parameters() -> StdioServerParameters:
    """Return parameters that launch the local quickstart server.

    StdioServerParameters 描述“客户端应该如何启动 MCP Server 进程”。
    这里不是连接一个已经在监听端口的 HTTP 服务，而是让 MCP client
    直接启动一个本地 Python 子进程，然后通过 stdin/stdout 和它通信。
    """
    return StdioServerParameters(
        # sys.executable 是当前正在运行 quickstart_client.py 的 Python 解释器路径。
        # 如果你用 `uv run python quickstart_client.py` 启动客户端，它通常会指向
        # 当前项目的 `.venv/bin/python`。这样 server 子进程会复用同一个虚拟环境，
        # 能找到已经安装好的 `mcp` 依赖。
        command=sys.executable,
        # args 是传给 command 的命令行参数。组合起来等价于执行：
        #
        #   <当前虚拟环境的 python> /绝对路径/quickstart_server.py
        #
        # ROOT / "quickstart_server.py" 会得到 server 文件的绝对路径，
        # str(...) 是因为 StdioServerParameters 需要字符串参数。
        args=[str(ROOT / "quickstart_server.py")],
    )


async def main() -> None:
    # stdio_client 会根据 server_parameters() 启动 quickstart_server.py 子进程。
    # MCP 的 stdio transport 使用标准输入/标准输出作为协议通道：
    #
    # - write：客户端写入 JSON-RPC 消息，实际会发到 server 进程的 stdin
    # - read：客户端读取 JSON-RPC 消息，实际来自 server 进程的 stdout
    #
    # async with 会负责进程生命周期：进入时启动 server，退出时关闭输入流并回收进程。
    async with stdio_client(server_parameters()) as (read, write):
        # ClientSession 在 read/write 之上封装了 MCP 协议细节。
        # 后面的 initialize、list_tools、call_tool、read_resource 等方法，
        # 最终都会被编码成 MCP JSON-RPC 请求，通过上面的 stdio 流发送给 server。
        async with ClientSession(read, write) as session:
            await session.initialize()

            tools = await session.list_tools()
            print("Tools:", [tool.name for tool in tools.tools])

            add_result = await session.call_tool("add", {"a": 2, "b": 40})
            print("add(2, 40):", add_result.content[0].text)

            concept_result = await session.call_tool("explain_concept", {"name": "tool"})
            print("explain_concept('tool'):", concept_result.content[0].text)

            resources = await session.list_resources()
            print("Resources:", [str(resource.uri) for resource in resources.resources])

            overview = await session.read_resource(AnyUrl("guide://overview"))
            print("guide://overview:", overview.contents[0].text)

            prompts = await session.list_prompts()
            print("Prompts:", [prompt.name for prompt in prompts.prompts])

            prompt = await session.get_prompt(
                "mcp_learning_prompt",
                {"topic": "resources", "level": "beginner"},
            )
            print("Prompt:", prompt.messages[0].content.text)


if __name__ == "__main__":
    asyncio.run(main())
