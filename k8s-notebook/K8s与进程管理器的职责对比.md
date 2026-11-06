# 常见问题

## 1. 如果我的应用服务都使用 K8s 来管理了，Web 服务是否就不再需要 `systemd`、`supervisor`、`pm2` 这些进程管理工具了？

一般来说，是的。

如果你的 Web 服务已经运行在 Kubernetes 里，通常就不再需要用 `systemd`、`supervisord`、`pm2` 这类进程管理器去管理这个应用进程了。

原因是它们原来负责的很多事，已经被 Kubernetes 接管了：

- 进程拉起和异常重启：`kubelet + container runtime`
- 保证副本数：`Deployment` / `StatefulSet`
- 挂掉后重新调度：Kubernetes 控制器
- 滚动发布和回滚：`Deployment`
- 健康检查和摘流量：`livenessProbe` / `readinessProbe`
- 扩缩容：`HPA` 或手动调副本数

所以在 K8s 里，推荐模式是：

- 一个容器尽量只跑一个主进程
- 这个进程以前台方式运行
- 不要在容器里再套一层 `systemd` / `supervisord`
- Node.js 服务通常直接跑 `node app.js`，而不是 `pm2 start app.js`

你可以这样理解职责边界：

- 在传统服务器上：`systemd` / `supervisord` / `pm2` 管应用进程
- 在 Kubernetes 里：Kubernetes 管容器和 Pod，应用自己专注于前台运行

### 例外情况

下面这些情况仍然可能会用到传统进程管理器：

- 如果服务不在 K8s 里，而是直接跑在普通 Linux 主机上，仍然需要 `systemd` 之类托管
- 某些历史项目会在容器里继续使用 `pm2`，虽然能跑，但通常不是推荐做法
- `systemd` 在 K8s 节点主机层仍然会存在，用来管理 `kubelet`、`containerd` 等系统服务，但不是用来管理你的业务 Pod
- 如果确实存在多进程编排需求，优先考虑拆成多个容器、sidecar，或者使用 K8s 原生对象，而不是在一个容器里再塞一层 supervisor

### 对 Web 服务更推荐的 K8s 做法

- 用 `Deployment` 管副本和发布
- 用 `Service` 暴露服务
- 用 `Ingress` 做入口
- 用探针做健康检查
- 用标准输出记录日志，而不是依赖 `pm2` 一类本地守护器

## 2. `systemd` / `supervisor` / `pm2` 和 Kubernetes 的职责对照表

| 能力 | `systemd` / `supervisor` / `pm2` | Kubernetes |
| --- | --- | --- |
| 启动应用进程 | 负责 | 负责启动容器中的主进程 |
| 进程退出后自动拉起 | 负责 | 负责，通过 Pod 重建或容器重启 |
| 保证多个实例运行 | 一般不擅长，需手工或额外脚本 | 原生支持，`Deployment` 直接控制副本数 |
| 跨机器调度 | 不负责 | 负责，由调度器决定 Pod 跑在哪个节点 |
| 服务发现 | 不负责 | 负责，通过 `Service`、DNS |
| 负载均衡 | 不负责或能力很弱 | 负责，通过 `Service`、`Ingress` |
| 滚动发布 | 一般需要脚本配合 | 原生支持，`Deployment` 支持滚动更新 |
| 回滚版本 | 一般需要手工处理 | 原生支持 |
| 健康检查 | 部分支持，但偏本机进程级别 | 原生支持，`livenessProbe` / `readinessProbe` |
| 自动扩缩容 | 几乎不负责 | 支持，`HPA` / 手工扩容 |
| 日志管理 | 一般能做本机日志托管 | 更推荐输出到标准输出，由日志系统统一采集 |
| 适用场景 | 单机或少量主机上的进程托管 | 容器化应用的集群管理 |

### 一句话总结

- `systemd` / `supervisor` / `pm2` 更像“单机进程管理员”
- Kubernetes 更像“集群级应用编排系统”

如果应用已经放进 Kubernetes，通常应当让 Kubernetes 负责运行和维护，而不是在容器内部再叠加一层传统进程管理器。
