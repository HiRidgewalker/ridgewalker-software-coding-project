import pytest
from mcp.client.session import ClientSession
from mcp.client.stdio import stdio_client
from mcp.types import AnyUrl

from quickstart_client import server_parameters


@pytest.mark.asyncio
async def test_stdio_server_exposes_core_capabilities() -> None:
    async with stdio_client(server_parameters()) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()

            tools = await session.list_tools()
            tool_names = {tool.name for tool in tools.tools}
            assert {"add", "explain_concept"} <= tool_names

            add_result = await session.call_tool("add", {"a": 20, "b": 22})
            assert add_result.content[0].text == "42"

            resources = await session.list_resources()
            resource_uris = {str(resource.uri) for resource in resources.resources}
            assert "guide://overview" in resource_uris

            overview = await session.read_resource(AnyUrl("guide://overview"))
            assert "MCP 快速概览" in overview.contents[0].text

            prompts = await session.list_prompts()
            prompt_names = {prompt.name for prompt in prompts.prompts}
            assert "mcp_learning_prompt" in prompt_names

            prompt = await session.get_prompt(
                "mcp_learning_prompt",
                {"topic": "resources", "level": "beginner"},
            )
            assert "resources" in prompt.messages[0].content.text
