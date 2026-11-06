import uvicorn

from service_b import app


def main() -> None:
    """以固定监听地址和端口启动 FastAPI 服务 B。"""
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8002,
    )


if __name__ == "__main__":
    main()
