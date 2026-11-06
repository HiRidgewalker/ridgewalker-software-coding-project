import uvicorn

from service_a import app


def main() -> None:
    """以固定监听地址和端口启动 FastAPI 服务 A。"""
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8001,
    )


if __name__ == "__main__":
    main()
