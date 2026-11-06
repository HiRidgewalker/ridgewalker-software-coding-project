import uvicorn

from .app import app
from .config import SERVICE_BIND_HOST, SERVICE_PORT


def main() -> None:
    """为项目命令提供 FastAPI 服务 B 的启动入口。"""
    uvicorn.run(
        app,
        host=SERVICE_BIND_HOST,
        port=SERVICE_PORT,
    )
