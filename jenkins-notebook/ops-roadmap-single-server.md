# 个人单机 DevOps 运维路线

本文档记录当前确认的个人运维技术路线，以及暂时全部部署到一台服务器时的推荐服务器配置。

## 运维路线总览

当前确认使用以下组件：

- Docker：容器运行环境。
- Docker Compose：单机多容器编排，适合本地和单服务器部署。
- Docker Swarm：Docker 原生集群编排，前期可单节点运行，后续可加入更多服务器。
- Portainer：Docker、Compose、Swarm 的可视化管理面板。
- Jenkins：CI/CD 平台，负责拉代码、测试、构建镜像、推送镜像和部署。
- GHCR：GitHub Container Registry，作为远程镜像仓库。
- PostgreSQL：业务数据库。
- Prometheus：指标采集和存储。
- Grafana：监控数据和日志数据的可视化面板。
- Grafana Alloy：统一采集器，用于采集日志、指标等数据并转发到后端。
- Loki：日志存储和查询系统。

## 单机部署阶段定位

当前阶段先将所有服务部署到同一台服务器上：

- Docker 作为基础运行环境。
- Docker Compose 用于管理单机上的服务编排。
- Docker Swarm 先以单节点模式运行，为后续多服务器扩展做准备。
- Portainer 用于可视化查看和管理 Docker、Compose、Swarm 资源。
- Jenkins 负责 CI/CD 流程。
- GHCR 负责存储构建完成后的 Docker 镜像。
- PostgreSQL 存储业务数据。
- Prometheus 采集主机、容器和业务服务指标。
- Grafana 展示 Prometheus 指标和 Loki 日志。
- Grafana Alloy 从 Docker 容器标准输出、宿主机或服务端点采集数据。
- Loki 存储应用日志，并供 Grafana 查询。

这个阶段的目标不是高可用，而是先形成完整、可维护、可观测、可回滚的个人 DevOps 闭环。

## 推荐服务器配置

不要只按“能跑起来”选择配置，需要考虑 Jenkins 构建 Docker 镜像、前端构建、PostgreSQL 缓存、Prometheus 指标写入、Loki 日志写入和 Grafana 查询时的峰值资源。

| 使用场景 | CPU | 内存 | 硬盘 |
| --- | ---: | ---: | ---: |
| 勉强学习/低频使用 | 4 核 | 8 GB | 150-200 GB SSD |
| 个人开发者推荐起步 | 4-8 核 | 16 GB | 300-500 GB SSD/NVMe |
| 长期更稳的配置 | 8 核 | 32 GB | 500 GB-1 TB NVMe |

当前更推荐选择：

```text
8 核 CPU
32 GB 内存
500 GB NVMe SSD
```

预算有限时，最低建议：

```text
4 核 CPU
16 GB 内存
300 GB SSD
```

不建议选择 `2C4G` 或 `2C8G`。这类配置虽然可以启动部分服务，但 Jenkins 构建、日志查询、指标查询和数据库访问同时发生时容易卡顿或内存不足。

## 硬盘空间规划

如果服务器硬盘为 `500 GB`，可以按下面方式预估：

| 用途 | 建议空间 |
| --- | ---: |
| 系统、Docker、基础镜像缓存 | 80-120 GB |
| Jenkins 数据和构建缓存 | 50-100 GB |
| PostgreSQL 数据 | 100-150 GB |
| Prometheus 指标数据 | 30-80 GB |
| Loki 日志数据 | 100-150 GB |
| 预留空间 | 50 GB 以上 |

实际占用会根据业务数据量、日志量、指标采集频率和构建频率变化。磁盘不能长期接近满载，否则 PostgreSQL、Prometheus、Loki 和 Docker 都可能出现异常。

## 保留策略建议

为了避免单机磁盘被日志、指标、镜像和构建记录占满，建议从一开始就设置保留策略：

- Jenkins 构建记录保留最近 `20-50` 次。
- Docker 本地镜像定期清理，只保留需要回滚的版本。
- GHCR 镜像保留最近 `5` 个版本，用于回滚。
- Prometheus 指标保留 `15-30` 天。
- Loki 日志保留 `7-30` 天。
- PostgreSQL 不能只依赖容器卷，必须单独做定期备份。

## 后续扩展方向

当后续新增服务器时，可以逐步从单机模式扩展：

- 将新服务器安装 Docker，并加入 Docker Swarm 集群。
- 使用 Portainer 查看和管理多节点 Swarm 集群。
- 将前端、后端、数据库、监控等服务按节点标签和资源情况调度到不同服务器。
- Jenkins 继续负责构建和部署，不需要替换。
- GHCR 继续作为统一镜像仓库。
- 数据库优先考虑主从、备份或迁移到托管数据库，不要简单地在多台机器上同时运行多个独立 PostgreSQL 实例。
- 监控和日志可以先保持单节点存储，数据量增长后再考虑远程存储或专门的日志/指标服务。

## 当前结论

当前最适合的路线是：

```text
Docker + Docker Compose + Docker Swarm + Portainer
+ Jenkins + GHCR
+ PostgreSQL
+ Prometheus + Grafana + Grafana Alloy + Loki
```

单机阶段推荐服务器配置：

```text
8C / 32G / 500GB NVMe
```

这套配置适合个人开发者长期运行多个前后端服务、CI/CD、数据库、监控和日志系统，并为后续扩展到多服务器 Swarm 集群保留空间。
