# FastAPI + Consul 学习项目

本项目包含两个相互独立的 Python 3.13 + FastAPI 应用。它们启动时注册到 Consul，由 Consul 主动执行 HTTP 健康检查，并通过 Consul 服务发现相互调用。

## 服务

| 项目 | Consul 服务名 | 默认地址 | 发现目标 |
| --- | --- | --- | --- |
| `service-a` | `service-a` | `127.0.0.1:8001` | `service-b` |
| `service-b` | `service-b` | `127.0.0.1:8002` | `service-a` |

两个项目均使用 `uv` 独立管理依赖和虚拟环境，Python 版本固定为 3.13。

## 前置条件

Consul HTTP API 需要能从宿主机通过 `http://127.0.0.1:8500` 访问。可以先验证：

```bash
curl http://127.0.0.1:8500/v1/status/leader
```

如果地址、令牌或端口不同，请分别修改两个项目中的 `.env`。可用配置项记录在各项目的 `.env.example` 中。

Consul 容器还需要将 `host.docker.internal` 映射到宿主机网关。两个 FastAPI 服务默认监听 `0.0.0.0`，使 Consul 容器可以主动访问 `/health`。

## 安装

```bash
cd service-a
uv sync
```

```bash
cd service-b
uv sync
```

## 启动

打开两个终端：

```bash
cd service-a
uv run main
```

```bash
cd service-b
uv run main
```

也可以直接执行两个项目根目录的 `main.py`：

```bash
uv run python -m main
```

监听地址和端口直接定义在代码中：服务 A 使用 `0.0.0.0:8001`，服务 B 使用 `0.0.0.0:8002`。服务名和 Consul 配置继续从各自项目根目录的 `.env` 读取。

## 验证

服务 A 通过 Consul 发现并调用服务 B：

```bash
curl http://127.0.0.1:8001/call-peer
```

服务 B 通过 Consul 发现并调用服务 A：

```bash
curl http://127.0.0.1:8002/call-peer
```

查询 Consul 中的健康实例：

```bash
curl 'http://127.0.0.1:8500/v1/health/service/service-a?passing=true'
curl 'http://127.0.0.1:8500/v1/health/service/service-b?passing=true'
```

还可以访问：

- 服务 A 的 API 文档：`http://127.0.0.1:8001/docs`
- 服务 B 的 API 文档：`http://127.0.0.1:8002/docs`
- Consul UI：`http://127.0.0.1:8500/ui/`

## 健康检查行为

- 应用启动时注册服务及 HTTP 健康检查。
- Consul 默认每 5 秒主动访问一次服务的 `/health`，请求超时时间为 2 秒。
- HTTP 状态码为 `200` 时，Consul 将服务实例标记为健康。
- 正常关闭时应用主动从 Consul 注销。
- 异常退出或 `/health` 无法访问时，Consul 将服务标记为不健康；持续不健康 60 秒后由 Consul 清理。
- `/call-peer` 只查询 `passing=true` 的实例。没有健康实例时返回 HTTP 503，实例已发现但均无法调用时返回 HTTP 502。

健康检查使用 `http://host.docker.internal:<端口>/health`，服务发现返回的实例地址仍为 `127.0.0.1:<端口>`。前者供 Consul 容器检查宿主机服务，后者供两个宿主机服务相互调用。

## 单元测试

```bash
cd service-a
uv run pytest
```

```bash
cd service-b
uv run pytest
```
