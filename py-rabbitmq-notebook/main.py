"""FastAPI 应用入口。

应用生命周期和路由注册集中在本文件；具体接口实现在 app.router。
"""

from __future__ import annotations

import asyncio
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.logging_utils import configure_logging
from app.router import router
from app.settings import get_settings
from app.topology import TopologyInitializationError, initialize_topology

configure_logging()
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """在开始处理请求前初始化完整的固定 RabbitMQ 拓扑。"""

    settings = get_settings()
    app.state.settings = settings
    app.state.topology_ready = False

    try:
        await asyncio.to_thread(initialize_topology, settings)
    except TopologyInitializationError:
        logger.exception("RabbitMQ 拓扑不可用，FastAPI 启动失败")
        raise

    app.state.topology_ready = True
    try:
        yield
    finally:
        app.state.topology_ready = False


app = FastAPI(
    title="RabbitMQ 直连交换机学习示例",
    description="演示启动时统一声明拓扑、接口发布消息、独立进程消费消息的完整流程。",
    version="0.1.0",
    lifespan=lifespan,
)

# 路由集中在 app.router，本文件只负责创建应用并完成注册。
app.include_router(router)
