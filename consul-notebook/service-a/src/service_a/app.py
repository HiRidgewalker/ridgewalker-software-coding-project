import logging
import random
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

import httpx
from fastapi import FastAPI, HTTPException, Request

from .consul import ConsulClient, ConsulError, ServiceEndpoint
from .settings import get_settings


logger = logging.getLogger(__name__)
settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    """启动时注册 HTTP 健康检查，关闭时从 Consul 注销。"""
    consul = ConsulClient(settings)
    upstream = httpx.AsyncClient(
        timeout=settings.http_timeout_seconds,
        trust_env=False,
    )
    registered = False
    app.state.consul = consul
    app.state.upstream = upstream

    try:
        await consul.register()
        registered = True
        logger.info(
            "已向 Consul 注册服务 %s（%s）",
            settings.service_name,
            settings.service_id,
        )
        yield
    finally:
        if registered:
            try:
                await consul.deregister()
                logger.info("已从 Consul 注销服务 %s", settings.service_id)
            except ConsulError:
                logger.exception("从 Consul 注销服务失败")
        await upstream.aclose()
        await consul.close()


app = FastAPI(
    title="服务 A",
    version="0.1.0",
    lifespan=lifespan,
)


@app.get("/health")
async def health() -> dict[str, str]:
    """返回本地进程的健康状态和服务标识。"""
    return {
        "status": "正常",
        "service": settings.service_name,
        "service_id": settings.service_id,
    }


@app.get("/hello")
async def hello() -> dict[str, str]:
    """返回用于标识服务 A 的问候信息。"""
    return {
        "message": "你好，这里是服务 A",
        "service": settings.service_name,
        "service_id": settings.service_id,
    }


@app.get("/call-peer")
async def call_peer(request: Request) -> dict[str, object]:
    """从 Consul 发现健康的服务 B 实例并调用其中一个。"""
    consul: ConsulClient = request.app.state.consul
    upstream: httpx.AsyncClient = request.app.state.upstream
    try:
        endpoints = await consul.discover(settings.peer_service_name)
    except ConsulError as exc:
        raise HTTPException(
            status_code=503,
            detail=f"发现服务 {settings.peer_service_name} 失败",
        ) from exc

    if not endpoints:
        raise HTTPException(
            status_code=503,
            detail=f"未找到服务 {settings.peer_service_name} 的健康实例",
        )

    candidates: list[ServiceEndpoint] = endpoints.copy()
    random.shuffle(candidates)
    for endpoint in candidates:
        try:
            response = await upstream.get(f"{endpoint.base_url}/hello")
            response.raise_for_status()
            peer_response = response.json()
        except (httpx.HTTPError, ValueError):
            logger.warning(
                "调用对端实例 %s 失败，地址为 %s",
                endpoint.service_id,
                endpoint.base_url,
                exc_info=True,
            )
            continue

        return {
            "caller": settings.service_name,
            "discovered_service": settings.peer_service_name,
            "target": endpoint.base_url,
            "response": peer_response,
        }

    raise HTTPException(
        status_code=502,
        detail=f"服务 {settings.peer_service_name} 的所有已发现实例均调用失败",
    )
