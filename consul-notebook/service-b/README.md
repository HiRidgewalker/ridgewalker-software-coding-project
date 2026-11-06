# 服务 B

FastAPI 服务 B。启动时向 Consul 注册主动 HTTP 健康检查，并通过服务名发现和调用 `service-a`。

业务代码位于 `src/service_b`，项目根目录的 `main.py` 负责启动 Uvicorn。`src/service_b/__init__.py` 只提供模块统一出口。

## 配置

本地运行读取项目根目录的 `.env`。配置模板保存在 `.env.example`：

```bash
cp .env.example .env
```

## 运行

```bash
uv sync
uv run main
```

或者：

```bash
uv run python -m main
```

默认监听 `0.0.0.0:8002`，本机通过 `http://127.0.0.1:8002` 访问。Consul 容器通过 `http://host.docker.internal:8002/health` 主动检查服务。

## 测试

```bash
uv run pytest
```
