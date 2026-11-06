# FastAPI + Next.js 的 Prometheus、Grafana、Alloy、Loki 搭配说明

本文档说明在个人单机 DevOps 环境中，如何搭配使用以下四个组件：

- Prometheus：指标采集和存储。
- Grafana：监控数据和日志数据的可视化面板。
- Grafana Alloy：统一采集器，用于采集日志、指标等数据并转发到后端。
- Loki：日志存储和查询系统。

示例业务服务以 `FastAPI + Next.js` 为主。

## 总体结论

这四个组件通常是各自独立运行一个容器。

在单机 Docker Compose 阶段，可以理解为：

```text
backend-fastapi     一个容器
frontend-nextjs     一个容器
prometheus          一个容器
grafana             一个容器
alloy               一个容器
loki                一个容器
```

在 Docker Swarm 阶段，可以理解为：

```text
backend-fastapi     一个 service，可多副本
frontend-nextjs     一个 service，可多副本
prometheus          一个 service，通常单副本
grafana             一个 service，通常单副本
alloy               一个 service，通常每台机器一个
loki                一个 service，单机阶段通常单副本
```

它们不是放进 FastAPI 或 Next.js 容器内部运行，而是作为独立的基础设施服务运行。业务服务只需要做好两件事：

- 对外暴露指标接口，例如 `/metrics`。
- 将日志输出到标准输出和标准错误，也就是容器日志。

## 四个组件分别负责什么

### Prometheus

Prometheus 负责采集和存储指标数据。

指标是数值型、结构化、适合画趋势图的数据，例如：

- HTTP 请求总数。
- HTTP 请求耗时。
- 接口错误率。
- CPU 使用率。
- 内存使用率。
- 容器重启次数。
- PostgreSQL 连接数。
- Jenkins 构建耗时。

Prometheus 的工作方式是主动拉取，也就是定时访问服务的指标地址：

```text
Prometheus -> http://backend:8000/metrics
Prometheus -> http://node-exporter:9100/metrics
Prometheus -> http://cadvisor:8080/metrics
```

所以 FastAPI 如果想被 Prometheus 采集，需要暴露 `/metrics` 接口。

### Grafana

Grafana 负责展示和查询，不负责采集。

Grafana 可以连接多个数据源：

```text
Grafana -> Prometheus
Grafana -> Loki
```

常见用途：

- 从 Prometheus 查询指标，画 CPU、内存、QPS、错误率、响应时间图表。
- 从 Loki 查询日志，查看某个服务在某个时间段的错误日志。
- 将指标和日志放在同一个 Dashboard 中联动排查问题。

Grafana 本身不直接采集 FastAPI 或 Next.js 的数据。

### Grafana Alloy

Grafana Alloy 是采集器。

它可以采集日志、指标、trace 等数据，并转发给对应后端。在当前路线里，重点先用它做日志采集：

```text
Docker 容器日志 -> Alloy -> Loki
```

也就是说，FastAPI 和 Next.js 只要把日志打印到终端，Docker 就会记录容器日志，Alloy 再从 Docker 读取这些日志并发送到 Loki。

如果未来需要，也可以让 Alloy 采集部分 Prometheus 指标，再转发给 Prometheus 或远程监控系统。但单机阶段最容易理解、最推荐的方式是：

```text
Prometheus 直接 scrape 指标
Alloy 采集 Docker 日志并发送到 Loki
```

### Loki

Loki 负责存储日志和提供日志查询能力。

日志是文本型、事件型数据，例如：

```text
2026-06-15 10:20:31 INFO user login success user_id=1001
2026-06-15 10:21:09 ERROR database connection timeout
```

Loki 不主动进入业务容器抓日志。它需要采集器把日志推过来：

```text
FastAPI stdout -> Docker logs -> Alloy -> Loki
Next.js stdout -> Docker logs -> Alloy -> Loki
```

Grafana 再连接 Loki 查询日志。

## 数据流关系

### 指标数据流

FastAPI、容器、主机等产生指标后，由 Prometheus 采集：

```text
FastAPI /metrics
        |
        v
Prometheus
        |
        v
Grafana Dashboard
```

如果加入主机和容器指标，常见关系是：

```text
node-exporter /metrics
cadvisor /metrics
FastAPI /metrics
        |
        v
Prometheus
        |
        v
Grafana
```

说明：

- `node-exporter` 用于采集宿主机 CPU、内存、磁盘、网络指标。
- `cadvisor` 用于采集 Docker 容器级别的 CPU、内存、网络、文件系统指标。
- 这两个组件不是四件套之一，但在真实部署中很常见。

### 日志数据流

FastAPI 和 Next.js 将日志打印到容器标准输出：

```text
FastAPI stdout/stderr
Next.js stdout/stderr
        |
        v
Docker container logs
        |
        v
Grafana Alloy
        |
        v
Loki
        |
        v
Grafana Explore / Dashboard
```

所以对业务服务来说，日志最佳实践是：

- 不要只写到容器内部文件。
- 优先输出到标准输出和标准错误。
- 日志中带上服务名、环境、请求 ID、错误信息。
- 后端建议使用结构化 JSON 日志，后续更容易在 Loki 中查询。

## FastAPI 服务如何接入

FastAPI 需要做两类输出：指标和日志。

### 指标

FastAPI 推荐暴露 `/metrics` 接口。

常见做法是使用 `prometheus-fastapi-instrumentator` 或 `prometheus_client`。

暴露后，Prometheus 配置 scrape：

```yaml
scrape_configs:
  - job_name: "fastapi-backend"
    metrics_path: "/metrics"
    static_configs:
      - targets:
          - "backend:8000"
```

这样 Prometheus 就会定期访问：

```text
http://backend:8000/metrics
```

常见后端指标包括：

- 请求总数。
- 请求耗时。
- HTTP 状态码分布。
- 异常数量。
- Python 进程指标。

### 日志

FastAPI 日志应该直接输出到终端。

例如容器中启动命令：

```text
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

Uvicorn 默认会将访问日志和应用日志输出到标准输出或标准错误，Docker 可以直接收集。

Alloy 再读取 Docker 容器日志并发送到 Loki。

## Next.js 服务如何接入

Next.js 前端也有两种常见部署形态。

### 静态站点形态

如果 Next.js 构建成静态文件，并由 Nginx 容器托管：

```text
frontend-nextjs build -> nginx container
```

日志主要来自 Nginx：

- 访问日志。
- 错误日志。

这些日志输出到容器标准输出后，可以被 Alloy 采集到 Loki。

指标方面，静态前端本身通常没有业务指标接口。可以先通过以下方式观察：

- Nginx 访问日志进入 Loki。
- 容器 CPU、内存由 cAdvisor 采集。
- 主机 CPU、内存、磁盘由 node-exporter 采集。

### Node.js 服务形态

如果 Next.js 以 Node.js 服务方式运行：

```text
next start -p 3000
```

日志来自 Node.js 进程，应该输出到标准输出。

指标可以后续再做，常见选择：

- 暂时只采集容器指标和日志。
- 给 Next.js 增加自定义 `/metrics` 接口。
- 在网关层统计请求量、状态码和响应时间。

个人项目早期不建议一开始就给前端做复杂指标，先把后端指标、容器指标、日志链路打通更重要。

## 单机 Docker Compose 中的容器关系

一个典型的单机结构如下：

```text
                 +----------------+
                 |    Grafana     |
                 |  :3000         |
                 +-------+--------+
                         |
          +--------------+--------------+
          |                             |
          v                             v
  +---------------+             +---------------+
  |  Prometheus   |             |     Loki      |
  |  :9090        |             |    :3100      |
  +-------+-------+             +-------+-------+
          ^                             ^
          |                             |
          |                             |
  +-------+-------+             +-------+-------+
  | FastAPI       |             | Grafana Alloy |
  | /metrics      |             | Docker logs   |
  +---------------+             +-------+-------+
                                        ^
                                        |
                          +-------------+-------------+
                          |                           |
                          v                           v
                    FastAPI logs                Next.js logs
```

容器职责：

| 容器 | 职责 | 是否必须 |
| --- | --- | --- |
| `backend` | FastAPI 后端服务 | 是 |
| `frontend` | Next.js 前端服务 | 是 |
| `prometheus` | 采集并存储指标 | 是 |
| `grafana` | 展示指标和日志 | 是 |
| `alloy` | 采集 Docker 日志并发送到 Loki | 是 |
| `loki` | 存储和查询日志 | 是 |
| `node-exporter` | 采集宿主机指标 | 推荐 |
| `cadvisor` | 采集容器指标 | 推荐 |

## Docker Compose 示例结构

下面是说明性结构，不是必须直接复制运行的最终配置。

```yaml
services:
  backend:
    image: ghcr.io/your-name/your-backend:latest
    networks:
      - app-net

  frontend:
    image: ghcr.io/your-name/your-frontend:latest
    networks:
      - app-net

  prometheus:
    image: prom/prometheus:latest
    volumes:
      - ./prometheus/prometheus.yml:/etc/prometheus/prometheus.yml:ro
      - prometheus-data:/prometheus
    ports:
      - "9090:9090"
    networks:
      - app-net

  loki:
    image: grafana/loki:latest
    volumes:
      - ./loki/loki.yml:/etc/loki/local-config.yaml:ro
      - loki-data:/loki
    ports:
      - "3100:3100"
    networks:
      - app-net

  alloy:
    image: grafana/alloy:latest
    volumes:
      - ./alloy/config.alloy:/etc/alloy/config.alloy:ro
      - /var/run/docker.sock:/var/run/docker.sock:ro
      - /var/lib/docker/containers:/var/lib/docker/containers:ro
    command:
      - run
      - /etc/alloy/config.alloy
    networks:
      - app-net

  grafana:
    image: grafana/grafana:latest
    volumes:
      - grafana-data:/var/lib/grafana
    ports:
      - "3000:3000"
    networks:
      - app-net

networks:
  app-net:

volumes:
  prometheus-data:
  loki-data:
  grafana-data:
```

实际生产部署时，建议只有网关暴露公网端口。Prometheus、Loki、Grafana 是否暴露到公网，要根据安全策略决定。个人服务器更推荐只暴露 Grafana，并给 Grafana 加登录、HTTPS 和强密码。

## Prometheus 配置示例

Prometheus 通过 `prometheus.yml` 配置采集目标。

```yaml
global:
  scrape_interval: 15s

scrape_configs:
  - job_name: "prometheus"
    static_configs:
      - targets:
          - "prometheus:9090"

  - job_name: "fastapi-backend"
    metrics_path: "/metrics"
    static_configs:
      - targets:
          - "backend:8000"

  - job_name: "node-exporter"
    static_configs:
      - targets:
          - "node-exporter:9100"

  - job_name: "cadvisor"
    static_configs:
      - targets:
          - "cadvisor:8080"
```

重点：

- `backend:8000` 是 Docker 网络内的服务名和端口。
- Prometheus 访问的是容器内部网络，不一定需要把后端的 `8000` 暴露到宿主机。
- `scrape_interval` 可以先用 `15s` 或 `30s`。

## Alloy 日志采集配置思路

Alloy 的核心目标是：

```text
读取 Docker 容器日志 -> 增加标签 -> 推送到 Loki
```

标签非常重要。没有标签，日志会很难查。

建议至少保留这些标签：

- `container`：容器名。
- `service`：服务名，例如 `backend`、`frontend`。
- `env`：环境，例如 `dev`、`prod`。
- `host`：机器名。

查询时可以在 Grafana 中写：

```logql
{service="backend"}
```

或者：

```logql
{service="backend"} |= "ERROR"
```

如果使用 Docker Compose，建议给业务容器加明确的 labels，方便 Alloy 识别：

```yaml
services:
  backend:
    labels:
      app.service: "backend"
      app.env: "prod"

  frontend:
    labels:
      app.service: "frontend"
      app.env: "prod"
```

## Grafana 中如何使用

Grafana 中需要配置两个数据源：

```text
Prometheus 数据源:
URL = http://prometheus:9090

Loki 数据源:
URL = http://loki:3100
```

配置完成后：

- 在 Dashboard 中用 Prometheus 查询指标。
- 在 Explore 中用 Loki 查询日志。
- 在告警规则中基于 Prometheus 指标设置告警。
- 后续也可以基于 Loki 日志设置错误日志告警。

常见 Dashboard：

- 主机资源 Dashboard。
- Docker 容器资源 Dashboard。
- FastAPI 接口请求 Dashboard。
- PostgreSQL Dashboard。
- Jenkins 构建 Dashboard。
- 应用错误日志 Dashboard。

## 在 Docker Swarm 中如何变化

如果后续启用 Docker Swarm，概念不变，但部署方式从 container 变成 service。

推荐理解：

```text
Prometheus: 通常 1 个副本
Grafana: 通常 1 个副本
Loki: 单机阶段 1 个副本
Alloy: 每台机器 1 个副本
FastAPI: 可以多个副本
Next.js: 可以多个副本
```

为什么 Alloy 推荐每台机器一个？

因为每台 Docker 宿主机都有自己的容器日志。Alloy 如果只部署在一台机器上，默认只能方便地读取这一台机器上的容器日志。多节点 Swarm 中，应该让每个节点都有一个 Alloy 实例采集本机日志。

Swarm 中可以用 `mode: global` 部署 Alloy：

```yaml
deploy:
  mode: global
```

这样每台节点都会运行一个 Alloy。

## 常见误区

### 误区一：Grafana 会自动采集日志和指标

不会。

Grafana 是展示和查询工具，需要连接 Prometheus 和 Loki。

### 误区二：Loki 会自动进入业务容器读取日志

不会。

Loki 需要 Alloy 这类采集器把日志发送过来。

### 误区三：应用只要打印日志，Grafana 就能看到

不完整。

完整链路必须是：

```text
应用打印日志 -> Docker 记录日志 -> Alloy 采集日志 -> Loki 存储日志 -> Grafana 查询日志
```

中间缺任何一个环节，Grafana 都看不到日志。

### 误区四：Prometheus 是日志系统

不是。

Prometheus 处理指标，Loki 处理日志。

### 误区五：所有组件都应该多副本

单机阶段不需要。

个人服务器上，Prometheus、Grafana、Loki 通常单副本即可。业务服务可以根据需要多副本。Alloy 在单机阶段一个副本，多机阶段每台机器一个副本。

## 推荐的第一阶段落地顺序

建议按下面顺序落地，不要一次性把所有复杂配置都做完：

1. 先让 FastAPI 和 Next.js 正常容器化运行。
2. 让 FastAPI 暴露 `/metrics`。
3. 启动 Prometheus，确认能抓到 FastAPI 指标。
4. 启动 Grafana，添加 Prometheus 数据源。
5. 启动 Loki。
6. 启动 Alloy，采集 Docker 容器日志并推送到 Loki。
7. 在 Grafana 添加 Loki 数据源。
8. 在 Grafana Explore 中确认能查到 `backend` 和 `frontend` 日志。
9. 再补充 node-exporter、cadvisor、PostgreSQL exporter。
10. 最后整理 Dashboard 和告警。

## 当前推荐架构

对于个人开发者单机部署，推荐当前采用：

```text
FastAPI:
  - 暴露 /metrics 给 Prometheus
  - 日志输出到 stdout/stderr

Next.js:
  - 日志输出到 stdout/stderr
  - 指标先依赖容器指标和网关日志

Prometheus:
  - 采集 FastAPI、主机、容器、数据库指标

Alloy:
  - 采集 Docker 容器日志
  - 将日志发送到 Loki

Loki:
  - 存储应用日志

Grafana:
  - 连接 Prometheus 看指标
  - 连接 Loki 查日志
```

最终形成的排障方式是：

```text
Grafana 发现接口错误率升高
        |
        v
查看 Prometheus 中的请求指标和资源指标
        |
        v
跳到 Loki 查询同一时间段的 backend 日志
        |
        v
定位具体错误、接口、请求 ID 或数据库问题
```

这就是 Prometheus、Grafana、Alloy、Loki 在 FastAPI + Next.js 服务中的基本搭配方式。
