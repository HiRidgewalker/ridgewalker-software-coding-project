import json

import httpx
import pytest

from service_b.consul import ConsulClient
from service_b.settings import Settings


def make_settings() -> Settings:
    return Settings(
        _env_file=None,
        consul_http_addr="http://consul.test:8500",
        consul_token=None,
        service_name="service-b",
        service_id="service-b-test",
        peer_service_name="service-a",
        consul_health_interval_seconds=5,
        consul_health_timeout_seconds=2,
        consul_deregister_after_seconds=60,
        http_timeout_seconds=5,
    )


@pytest.mark.asyncio
async def test_register_http_check_and_deregister() -> None:
    requests: list[httpx.Request] = []

    def handler(request: httpx.Request) -> httpx.Response:
        requests.append(request)
        return httpx.Response(200, request=request)

    client = ConsulClient(
        make_settings(),
        transport=httpx.MockTransport(handler),
    )
    try:
        await client.register()
        await client.deregister()
    finally:
        await client.close()

    registration = json.loads(requests[0].content)
    assert registration["Name"] == "service-b"
    assert registration["Address"] == "127.0.0.1"
    assert registration["Check"] == {
        "CheckID": "service:service-b-test",
        "Name": "service-b HTTP 健康检查",
        "HTTP": "http://host.docker.internal:8002/health",
        "Method": "GET",
        "Interval": "5s",
        "Timeout": "2s",
        "DeregisterCriticalServiceAfter": "60s",
    }
    assert requests[1].url.path == "/v1/agent/service/deregister/service-b-test"


@pytest.mark.asyncio
async def test_discover_returns_service_address_and_node_fallback() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        assert request.url.params["passing"] == "true"
        return httpx.Response(
            200,
            json=[
                {
                    "Node": {"Address": "10.0.0.10"},
                    "Service": {
                        "ID": "service-a-1",
                        "Address": "127.0.0.1",
                        "Port": 8001,
                    },
                },
                {
                    "Node": {"Address": "10.0.0.11"},
                    "Service": {
                        "ID": "service-a-2",
                        "Address": "",
                        "Port": 9001,
                    },
                },
            ],
            request=request,
        )

    client = ConsulClient(
        make_settings(),
        transport=httpx.MockTransport(handler),
    )
    try:
        endpoints = await client.discover("service-a")
    finally:
        await client.close()

    assert [endpoint.base_url for endpoint in endpoints] == [
        "http://127.0.0.1:8001",
        "http://10.0.0.11:9001",
    ]
