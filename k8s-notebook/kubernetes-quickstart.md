# Kubernetes Quickstart

目标：用一篇文档快速掌握 Kubernetes 是什么、常见对象分别负责什么、它们之间如何协作，以及控制面核心组件是怎么工作的。

适合人群：

- 刚开始接触 Kubernetes，想先建立整体认知
- 已经会用 `minikube`，但还分不清 `Node`、`Pod`、`Deployment`、`Service` 是什么
- 想从“会敲命令”过渡到“看懂 K8s 在干什么”

这篇文档的思路不是一上来堆术语，而是按三个层次来讲：

1. 先看最常见对象是什么
2. 再看这些对象是怎么配合起来工作的
3. 最后再看控制面组件是怎么驱动整个系统的

---

## 1. Kubernetes 是什么

一句话理解：

Kubernetes 是一个用来管理容器化应用的编排平台。

它最核心的价值，不是“帮你启动一个容器”，而是：

- 帮你声明应用应该怎么运行
- 帮你持续维持这个目标状态
- 帮你做扩缩容、发布、回滚、服务发现、健康检查

你可以把它先粗暴理解成：

“一个负责管理应用生命周期的集群操作系统”

### 1.1 它解决什么问题

如果没有 Kubernetes，你通常要手工处理这些事：

- 应用挂了怎么拉起来
- 应用要跑几个实例
- 请求怎么打到多个实例上
- 发布新版本时怎么不停机
- 应用配置怎么注入
- 机器多了以后怎么调度服务

Kubernetes 就是把这些问题系统化地解决掉。

### 1.2 最重要的 3 个思想

先记住这 3 个思想，比背对象名称更重要。

#### 1. 声明式

你不是告诉系统“先做 A，再做 B，再做 C”，而是告诉系统：

“我想要 3 个副本的这个应用在运行”

Kubernetes 会自己想办法把实际状态变成你声明的目标状态。

#### 2. 控制循环

Kubernetes 不会只执行一次命令就结束，它会不断比较：

- 期望状态
- 实际状态

如果不一致，就继续调整。

#### 3. 通过对象管理系统

你在 K8s 里通常不是直接管理进程，而是管理对象，比如：

- `Deployment`
- `Service`
- `Ingress`
- `ConfigMap`

对象之间有明确职责，这就是 K8s 的核心抽象。

---

## 2. 先建立最小认知

在理解每个对象之前，先建立一个最小地图。

### 2.1 集群是什么

Kubernetes 不是一台机器，而是一组机器组成的集群。

一个集群通常由两部分组成：

- 控制面：负责决策和管理
- 工作节点：负责真正运行你的应用

### 2.2 Node 是什么

`Node` 就是一台加入 Kubernetes 集群的机器。

它可以是：

- 物理机
- 虚拟机
- 云主机
- 本地 `minikube` 提供的节点

Node 的作用很简单：

- 提供 CPU、内存、磁盘、网络
- 运行 Pod
- 上报自身和 Pod 的状态

可以先把它理解成：

“Kubernetes 用来承载应用的执行机器”

### 2.3 Pod 是什么

`Pod` 是 Kubernetes 里最小的调度单位。

你可以先把它粗略理解成：

“一组一起运行的容器”

但在大多数开发场景里，你可以先近似理解为：

“一个应用实例”

需要记住几点：

- Pod 不是固定机器
- Pod 会被删除和重建
- Pod 的名字通常不稳定
- 不要把 Pod 当成长期固定存在的东西

### 2.4 为什么不是直接管理容器

因为 K8s 不是单纯的容器运行器，而是集群调度和编排系统。

它要考虑的不只是“启动一个容器”，还包括：

- 放到哪台 Node 上
- 需要几个副本
- 宕机了怎么恢复
- 怎么被服务发现
- 怎么更新版本

所以它用 Pod 和更高层对象来管理应用。

---

## 3. 最常见业务对象

这一节是整篇文档最重要的部分。先把这些对象记住，后面很多概念自然就顺了。

### 3.1 Node

#### 它是什么

Node 是集群中的计算节点，也就是实际运行 Pod 的机器。

#### 它的作用

- 承载业务 Pod
- 承载系统组件
- 提供计算资源
- 接受调度结果

#### 你需要记住什么

- 应用最终是跑在 Node 上的
- Pod 不是直接“漂浮”在集群里，而是被调度到某个 Node 上
- 一个集群可以有多个 Node

常见命令：

```bash
kubectl get nodes
kubectl describe node <node-name>
```

### 3.2 Pod

#### 它是什么

Pod 是 K8s 中最小的调度单位，里面可以包含一个或多个容器。

#### 它的作用

- 作为应用运行的基本实例
- 承载容器和网络身份
- 作为 Service 选中的后端目标

#### 你需要记住什么

- 绝大多数业务应用，通常一个 Pod 里先放一个主容器
- Pod 可能会被替换，不要依赖 Pod 名称和 IP 长期不变
- 真正对外服务时，一般不直接依赖 Pod，而是通过 Service

常见命令：

```bash
kubectl get pods
kubectl describe pod <pod-name>
kubectl logs <pod-name>
```

### 3.3 Deployment

#### 它是什么

`Deployment` 是最常见的无状态应用管理对象。

你部署 Web 服务时，最常用的就是它。

#### 它的作用

- 管理 Pod 副本数
- 支持滚动更新
- 支持回滚
- 保证期望数量的 Pod 持续存在

#### 你需要记住什么

- 你通常不是直接创建 Pod，而是创建 Deployment
- Deployment 不直接处理流量，它主要负责“有多少 Pod、运行什么版本”
- Deployment 底下实际还会管理 `ReplicaSet`

常见命令：

```bash
kubectl get deployments
kubectl describe deployment <name>
kubectl rollout status deployment/<name>
kubectl rollout undo deployment/<name>
```

### 3.4 ReplicaSet

#### 它是什么

`ReplicaSet` 是用来保证指定数量 Pod 持续运行的对象。

#### 它的作用

- 维持 Pod 副本数
- 如果某些 Pod 挂了，就补回来

#### 你需要记住什么

- 日常开发里通常不直接操作 ReplicaSet
- 它通常由 Deployment 间接管理
- 但理解它有助于你看懂对象层级

对象关系可以先记成：

`Deployment -> ReplicaSet -> Pod`

### 3.5 Service

#### 它是什么

`Service` 是一组 Pod 的稳定访问入口。

因为 Pod 会重建、IP 会变化，所以不能直接靠 Pod IP 访问。

#### 它的作用

- 给一组 Pod 提供稳定地址
- 把流量转发到匹配的 Pod
- 提供服务发现能力

#### 你需要记住什么

- Service 不负责创建 Pod
- Service 不负责管理副本数
- Service 的核心是“选中后端 Pod 并给出稳定入口”

最常见的类型：

- `ClusterIP`：只能集群内部访问
- `NodePort`：通过节点端口对外暴露
- `LoadBalancer`：通常在云环境中暴露外部地址

常见命令：

```bash
kubectl get svc
kubectl describe svc <service-name>
kubectl get endpoints <service-name>
```

### 3.6 Ingress

#### 它是什么

`Ingress` 是 HTTP/HTTPS 的入口规则对象。

#### 它的作用

- 把外部请求转发给不同 Service
- 支持基于域名和路径的路由
- 统一管理 Web 入口

#### 你需要记住什么

- Ingress 本身只是规则
- 真正处理请求的通常是 Ingress Controller
- Ingress 面向七层 HTTP/HTTPS 路由，不是所有 TCP/UDP 都靠它

一个最常见的链路是：

`外部请求 -> Ingress -> Service -> Pod`

### 3.7 ConfigMap

#### 它是什么

`ConfigMap` 用来保存普通配置数据。

#### 它的作用

- 给 Pod 注入环境变量
- 给容器挂载配置文件
- 把配置和镜像解耦

#### 你需要记住什么

- 普通配置放 `ConfigMap`
- 不要把敏感信息放进去

### 3.8 Secret

#### 它是什么

`Secret` 用来保存敏感信息。

#### 它的作用

- 保存密码
- 保存 Token
- 保存证书等敏感数据

#### 你需要记住什么

- `Secret` 和 `ConfigMap` 的使用方式很像
- 差别主要在于语义和敏感数据管理
- 但它不是“绝对安全保险箱”，仍然要结合权限控制

### 3.9 Namespace

#### 它是什么

`Namespace` 是 Kubernetes 里的逻辑隔离空间。

#### 它的作用

- 让不同环境或不同业务相互隔离
- 方便资源归类和权限控制

#### 你需要记住什么

- `default` 是默认命名空间
- 很多对象在不同 Namespace 下可以重名
- 排障时一定要看自己当前操作的是哪个 Namespace

常见命令：

```bash
kubectl get ns
kubectl get pods -n kube-system
kubectl get pods -A
```

### 3.10 Volume 和 PersistentVolumeClaim

#### 它们是什么

Pod 本身是易失的，Pod 重建后，容器内的数据可能会丢。

为了让数据可持久化，K8s 提供了卷相关机制。

#### 它们的作用

- `Volume`：给 Pod 提供存储挂载
- `PersistentVolumeClaim`：Pod 对持久化存储资源的申请

#### 你需要记住什么

- 无状态应用常用 `Deployment`
- 有持久化数据需求时，通常要考虑卷和 PVC

### 3.11 StatefulSet

#### 它是什么

`StatefulSet` 是用来管理有状态应用的对象。

#### 它的作用

- 给 Pod 稳定身份
- 给 Pod 稳定存储
- 适合数据库、消息队列等场景

#### 你需要记住什么

- 普通 Web 服务优先考虑 `Deployment`
- 数据库类应用再考虑 `StatefulSet`

### 3.12 Job 和 CronJob

#### 它们是什么

这两个对象不是长期跑服务，而是执行一次性或定时任务。

#### 它们的作用

- `Job`：执行一次任务，直到完成
- `CronJob`：按时间周期调度 Job

#### 你需要记住什么

- Web 服务不用它们
- 批处理、定时任务、脚本任务常用它们

---

## 4. 这些对象是怎么协作的

只认识单个对象还不够，更重要的是看懂它们之间怎么配合。

### 4.1 最常见对象关系图

先记住这一条链路：

`Deployment -> Pod`

`Service -> Pod`

`Ingress -> Service`

`ConfigMap/Secret -> Pod`

`PVC -> Pod`

### 4.2 Deployment 和 Pod 的关系

最容易混淆的一点是：

- Pod 是实际运行实例
- Deployment 是管理这些实例的上层对象

也就是说：

- 你想要 3 个实例，通常是改 Deployment
- 不是手工创建 3 个 Pod 长期维护

### 4.3 Service 和 Pod 的关系

Service 通过标签选择器找到一组 Pod。

例如：

- Pod 有标签 `app=web`
- Service 选择 `app=web`

这样请求打到 Service 时，就会被转发到这组 Pod。

最重要的一点：

Service 不关心 Pod 名字，它关心的是标签。

### 4.4 Ingress 和 Service 的关系

Ingress 通常不会直接把流量打到 Pod。

更常见的做法是：

- Ingress 匹配域名或路径
- 然后把请求转发给某个 Service
- Service 再把流量打到对应 Pod

### 4.5 ConfigMap / Secret 和 Pod 的关系

应用配置通常不是写死在镜像里，而是通过：

- 环境变量注入
- 文件挂载

这样可以做到：

- 同一个镜像在不同环境复用
- 配置和代码分离

### 4.6 PVC 和 Pod 的关系

如果 Pod 需要持久化数据，就不能只依赖容器内部临时文件系统。

这时一般会让 Pod 挂载 PVC，对应到后端存储。

### 4.7 一个最小 Web 服务链路

可以把一个最常见的发布链路理解成：

1. 用 Deployment 定义 Web 应用副本数
2. Deployment 创建 Pod
3. 用 Service 给这些 Pod 一个稳定访问入口
4. 用 Ingress 把外部 HTTP 请求导进来
5. 用 ConfigMap 和 Secret 注入配置

如果你先把这条链记住，已经够理解大多数业务场景。

---

## 5. K8s 控制面核心组件

到这里为止，你已经看到了“业务对象视角”的 K8s。下面开始看“系统内部视角”。

### 5.1 kube-apiserver

#### 它是什么

`kube-apiserver` 是 Kubernetes 的统一 API 入口。

#### 它的作用

- 接收 `kubectl` 和其他客户端请求
- 校验请求是否合法
- 读写集群状态
- 对外暴露 K8s API

#### 你可以怎么理解

它像整个 Kubernetes 的“前门”。

几乎所有操作都会经过它。

### 5.2 etcd

#### 它是什么

`etcd` 是 Kubernetes 的一致性键值存储。

#### 它的作用

- 保存集群配置
- 保存对象状态
- 保存期望状态和部分运行状态

#### 你可以怎么理解

它像 Kubernetes 的“数据库”。

### 5.3 scheduler

#### 它是什么

`scheduler` 是调度器。

#### 它的作用

- 决定新创建的 Pod 应该跑到哪个 Node 上

#### 它考虑什么

- 资源是否够
- 节点约束
- 亲和性和反亲和性
- 污点和容忍

#### 你可以怎么理解

它像“分配工位的人”。

### 5.4 controller-manager

#### 它是什么

`controller-manager` 负责运行各种控制器。

#### 它的作用

- 持续对比期望状态和实际状态
- 不一致时做纠正动作

例如：

- 你声明 Deployment 需要 3 个 Pod
- 实际只有 2 个
- 控制器就会推动系统补出第 3 个

#### 你可以怎么理解

它像“持续巡检并纠偏的人”。

### 5.5 kubelet

#### 它是什么

`kubelet` 是运行在每个 Node 上的代理程序。

#### 它的作用

- 接收控制面的调度结果
- 负责把 Pod 真正跑起来
- 上报节点和 Pod 状态

#### 你可以怎么理解

控制面决定“该做什么”，kubelet 负责在节点上“把它做出来”。

### 5.6 Container Runtime

#### 它是什么

容器运行时负责真正拉镜像、创建容器、运行容器。

常见实现有：

- `containerd`
- `CRI-O`

#### 它的作用

- 拉取镜像
- 启动容器
- 停止和销毁容器

#### 你可以怎么理解

它是执行容器生命周期的底层引擎。

### 5.7 kube-proxy

#### 它是什么

`kube-proxy` 是 Service 网络转发的重要组件之一。

#### 它的作用

- 帮助实现 Service 到后端 Pod 的流量转发

#### 你需要记住什么

- Service 之所以能有稳定访问入口，背后离不开节点网络规则和转发机制

### 5.8 CoreDNS

#### 它是什么

`CoreDNS` 是集群里的 DNS 组件。

#### 它的作用

- 让服务之间可以通过名字访问

例如：

- 一个 Pod 可以通过 Service 名称访问另一个服务

---

## 6. 一个请求进入 K8s 后发生了什么

这一节很重要，因为它能把前面的概念串起来。

假设你部署了一个 Web 服务：

- `Deployment: web`
- `Service: web-svc`
- `Ingress: example.com`

当用户访问 `http://example.com` 时，可以粗略理解成下面这条链：

1. 请求先到 Ingress Controller
2. Ingress 规则判断这个域名和路径该转发到 `web-svc`
3. Service 根据标签找到后端 Pod
4. 流量被转发到某个匹配的 Pod
5. Pod 中的容器处理请求并返回响应

这个链路背后还依赖：

- Pod 由 Deployment 创建和维护
- Pod 被 scheduler 调度到某个 Node
- kubelet 在该 Node 上把容器跑起来
- container runtime 拉镜像并启动容器
- kube-proxy 和网络组件处理转发
- CoreDNS 提供服务发现

如果你能把这条请求链说清楚，说明你对 K8s 的核心结构已经建立起来了。

---

## 7. 一个 Deployment 被创建后发生了什么

再从“部署”这个角度看一遍流程。

当你执行：

```bash
kubectl apply -f deployment.yaml
```

大致会发生这些事：

1. `kubectl` 把 YAML 提交给 `kube-apiserver`
2. `apiserver` 校验并把对象状态写入 `etcd`
3. `controller-manager` 发现新的 Deployment，需要满足期望状态
4. Deployment 相关控制器创建 ReplicaSet
5. ReplicaSet 发现需要一定数量的 Pod，于是创建 Pod
6. `scheduler` 发现这些 Pod 还没绑定 Node，于是选择合适节点
7. 节点上的 `kubelet` 看到分配给自己的 Pod，开始创建容器
8. `container runtime` 拉镜像并启动容器
9. Pod 进入运行状态
10. 如果有 Service，它会基于标签把这些 Pod 纳入后端

这就是 K8s “声明式 + 控制循环” 的典型体现。

---

## 8. 初学者最容易混淆的点

### 8.1 Pod 和 Deployment 不是一回事

- Pod 是运行实例
- Deployment 是管理实例的对象

### 8.2 Service 不创建 Pod

Service 只是稳定入口和服务发现机制，不负责创建工作负载。

### 8.3 Ingress 不直接运行你的应用

Ingress 主要是入口规则，真正承载应用的还是 Pod。

### 8.4 ConfigMap 和 Secret 不是“应用本体”

它们只是配置来源，不负责运行应用。

### 8.5 Node 不是 Pod

- Node 是机器
- Pod 是跑在机器上的工作负载实例

### 8.6 K8s 不是 Docker 的替代品

Docker 主要解决容器打包和运行问题，K8s 解决的是大规模容器编排问题。

---

## 9. 初学者应该先记住什么

如果你现在只想记住最重要的内容，先记这几条：

1. `Pod` 是最小调度单位
2. `Deployment` 管无状态应用和副本
3. `Service` 给 Pod 提供稳定访问入口
4. `Ingress` 管 HTTP/HTTPS 入口规则
5. `ConfigMap` 放普通配置，`Secret` 放敏感配置
6. `Namespace` 用来做逻辑隔离
7. `Deployment -> Pod`
8. `Service -> Pod`
9. `Ingress -> Service`
10. `apiserver` 是入口，`etcd` 是存储，`scheduler` 负责调度，`kubelet` 负责在节点上真正运行 Pod

---

## 10. 推荐学习顺序

如果你想一步一步深入，建议按这个顺序学：

1. 先学 `Pod`、`Deployment`、`Service`
2. 再学 `Ingress`、`ConfigMap`、`Secret`
3. 再理解 `Namespace`、`Volume`、`PVC`
4. 然后补 `StatefulSet`、`Job`、`CronJob`
5. 最后再深入控制面组件和调度机制

不要一上来就把所有对象都背下来。

更有效的方法是：

- 先知道最常见对象是什么
- 再知道它们如何协作
- 最后理解系统内部机制

---

## 11. 一页速记

如果你只想先抓住主干，可以把 Kubernetes 粗略记成这样：

```text
Node 是机器
Pod 是应用实例
Deployment 管 Pod 副本和发布
Service 给 Pod 稳定入口
Ingress 管外部 HTTP 入口
ConfigMap/Secret 提供配置
PVC 提供持久化存储
apiserver 是总入口
etcd 保存状态
scheduler 决定 Pod 去哪台 Node
kubelet 在 Node 上真正把 Pod 跑起来
```

如果你能把上面这几行说清楚，已经完成了 Kubernetes 入门阶段最重要的一步。
