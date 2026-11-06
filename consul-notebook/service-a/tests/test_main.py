import httpx
import pytest

from service_a import app


@pytest.mark.asyncio
async def test_health_and_hello() -> None:
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(
        transport=transport,
        base_url="http://test",
    ) as client:
        health = await client.get("/health")
        hello = await client.get("/hello")

    assert health.status_code == 200
    assert health.json()["service"] == "service-a"
    assert hello.status_code == 200
    assert hello.json()["message"] == "你好，这里是服务 A"
