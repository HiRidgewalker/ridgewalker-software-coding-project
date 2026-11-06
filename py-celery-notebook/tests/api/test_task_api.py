from collections.abc import Callable
from uuid import UUID

from httpx import ASGITransport, AsyncClient

import main


class TestTaskApi:
    """验证消息任务 HTTP 接口。"""

    async def test_enqueue_message_returns_task_id(self, monkeypatch) -> None:
        """合法消息应成功发布并返回任务标识。"""

        async def call_inline(function: Callable[..., object], *args: object) -> object:
            return function(*args)

        monkeypatch.setattr("src.controller.api.asyncio.to_thread", call_inline)
        transport = ASGITransport(app=main.create_app())
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.post("/tasks/messages", json={"message": "hello"})

        assert response.status_code == 202
        assert UUID(response.json()["task_id"])
        assert response.json()["status"] == "已入队"

    async def test_enqueue_message_rejects_extra_fields(self) -> None:
        """请求包含未知字段时应返回参数校验错误。"""

        transport = ASGITransport(app=main.create_app())
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.post(
                "/tasks/messages",
                json={"message": "hello", "unexpected": True},
            )

        assert response.status_code == 422

    async def test_enqueue_message_accepts_maximum_length(self, monkeypatch) -> None:
        """长度达到上限的消息仍应成功发布。"""

        async def call_inline(function: Callable[..., object], *args: object) -> object:
            return function(*args)

        monkeypatch.setattr("src.controller.api.asyncio.to_thread", call_inline)
        transport = ASGITransport(app=main.create_app())
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.post("/tasks/messages", json={"message": "x" * 500})

        assert response.status_code == 202
