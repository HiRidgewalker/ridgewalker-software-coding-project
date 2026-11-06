from dataclasses import dataclass
from urllib.parse import quote

import httpx

from .config import CONSUL_HEALTH_CHECK_URL, SERVICE_ADVERTISE_HOST, SERVICE_PORT
from .settings import Settings


class ConsulError(RuntimeError):
    """与 Consul 通信失败时抛出的异常。"""


@dataclass(frozen=True, slots=True)
class ServiceEndpoint:
    """Consul 服务发现返回的可调用服务实例。"""

    service_id: str
    address: str
    port: int

    @property
    def base_url(self) -> str:
        """构建当前服务实例的 HTTP 基础地址。"""
        host = f"[{self.address}]" if ":" in self.address else self.address
        return f"http://{host}:{self.port}"


class ConsulClient:
    """封装当前 FastAPI 服务需要使用的 Consul 操作。"""

    def __init__(
        self,
        settings: Settings,
        *,
        transport: httpx.AsyncBaseTransport | None = None,
    ) -> None:
        """根据服务配置创建异步 Consul HTTP 客户端。"""
        self._settings = settings
        headers = (
            {"X-Consul-Token": settings.consul_token}
            if settings.consul_token
            else None
        )
        self._client = httpx.AsyncClient(
            base_url=settings.consul_http_addr,
            headers=headers,
            timeout=settings.http_timeout_seconds,
            transport=transport,
            trust_env=False,
        )

    async def register(self) -> None:
        """注册当前服务实例并创建 Consul 主动 HTTP 健康检查。"""
        settings = self._settings
        payload = {
            "ID": settings.service_id,
            "Name": settings.service_name,
            "Address": SERVICE_ADVERTISE_HOST,
            "Port": SERVICE_PORT,
            "Tags": ["fastapi", "python-3.13"],
            "Meta": {"peer_service": settings.peer_service_name},
            "Check": {
                "CheckID": settings.consul_check_id,
                "Name": f"{settings.service_name} HTTP 健康检查",
                "HTTP": CONSUL_HEALTH_CHECK_URL,
                "Method": "GET",
                "Interval": f"{settings.consul_health_interval_seconds}s",
                "Timeout": f"{settings.consul_health_timeout_seconds}s",
                "DeregisterCriticalServiceAfter": (
                    f"{settings.consul_deregister_after_seconds}s"
                ),
            },
        }
        await self._request("PUT", "/v1/agent/service/register", json=payload)

    async def deregister(self) -> None:
        """从本地 Consul Agent 注销当前服务实例。"""
        service_id = quote(self._settings.service_id, safe="")
        await self._request("PUT", f"/v1/agent/service/deregister/{service_id}")

    async def discover(self, service_name: str) -> list[ServiceEndpoint]:
        """返回指定服务名下所有健康的服务实例。"""
        encoded_name = quote(service_name, safe="")
        response = await self._request(
            "GET",
            f"/v1/health/service/{encoded_name}",
            params={"passing": "true"},
        )
        try:
            records = response.json()
        except ValueError as exc:
            raise ConsulError("服务发现时 Consul 返回了无效的 JSON") from exc

        if not isinstance(records, list):
            raise ConsulError("Consul 返回了无效的服务发现响应")

        endpoints: list[ServiceEndpoint] = []
        for record in records:
            service = record.get("Service", {})
            node = record.get("Node", {})
            address = service.get("Address") or node.get("Address")
            port = service.get("Port")
            service_id = service.get("ID")
            if address and isinstance(port, int) and port > 0 and service_id:
                endpoints.append(
                    ServiceEndpoint(
                        service_id=str(service_id),
                        address=str(address),
                        port=port,
                    )
                )
        return endpoints

    async def close(self) -> None:
        """关闭底层异步 HTTP 客户端。"""
        await self._client.aclose()

    async def _request(self, method: str, path: str, **kwargs: object) -> httpx.Response:
        """发送 Consul 请求，并将 HTTP 错误转换为 ConsulError。"""
        try:
            response = await self._client.request(method, path, **kwargs)
            response.raise_for_status()
        except httpx.HTTPError as exc:
            raise ConsulError(f"Consul 请求失败：{method} {path}：{exc}") from exc
        return response
