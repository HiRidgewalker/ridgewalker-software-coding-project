from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI

from src.client.celery_client.celery_config import get_celery_settings
from src.client.celery_client.celery_topology import declare_topology
from src.controller.api import router


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncGenerator[None]:
    """在接收任务前确保 RabbitMQ 拓扑已经存在。"""

    settings = get_celery_settings()
    if settings.declare_topology_on_startup:
        declare_topology()
    yield


def create_app() -> FastAPI:
    """创建并配置 FastAPI 应用。"""

    application = FastAPI(
        title="FastAPI Celery Template",
        version="0.1.0",
        lifespan=lifespan,
    )
    application.include_router(router)
    return application


app = create_app()
