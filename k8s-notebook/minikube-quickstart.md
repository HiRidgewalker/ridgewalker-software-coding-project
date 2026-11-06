# Minikube Quickstart

目标：用一篇文档快速掌握 `minikube` 是什么、适合做什么、常用命令怎么用，以及如何在本地跑通一个最小 Kubernetes 集群。

适合人群：

- 刚开始接触 Kubernetes，想先会用
- 已经装好了 `minikube`，想尽快进入实操
- 在本地开发环境里需要一个轻量级 K8s 集群

本文默认你已经安装好了：

- `minikube`
- `kubectl`
- `docker`

如果你当前环境是 `WSL2 + Docker Desktop + Ubuntu`，安装与启动方式可以参考仓库里的 `在wsl2 + dockerdesktop + ubuntu24中安装minikube教程.md`。

---

## 1. Minikube 是什么

一句话理解：

`minikube` 是一个帮你在本地电脑上快速跑起 Kubernetes 集群的工具。

它的定位不是生产环境，而是：

- 学习 Kubernetes
- 本地开发联调
- 演示和实验
- 快速验证 YAML、Deployment、Service、Ingress 等对象

你可以把它先粗暴理解成：

“一键在本地起一个可用的 K8s 小集群”

### 1.1 它解决什么问题

如果你直接学习 Kubernetes，通常会遇到这些门槛：

- 搭集群很麻烦
- 机器资源有限
- 生产级安装方式太重
- 只想练 `kubectl` 和 YAML，不想先折腾一堆基础设施

`minikube` 的价值就在于：

- 启动简单
- 环境隔离
- 支持常见插件
- 可反复删除和重建
- 非常适合“边学边试”

### 1.2 它和 Docker 是什么关系

很多初学者会混淆这两者：

- `Docker` 主要解决“如何把应用打包成镜像、如何运行容器”
- `Kubernetes` 主要解决“如何管理大量容器和服务”
- `minikube` 则是“让 Kubernetes 能在你的本地跑起来”

所以它们不是互相替代，而是不同层次的工具。

### 1.3 它和 kind、kubeadm 的区别

可以先这样理解：

| 工具 | 定位 | 适合场景 |
| --- | --- | --- |
| `minikube` | 本地学习和开发 | 初学 K8s、本地联调、体验插件和 Dashboard |
| `kind` | 用容器快速起 K8s 集群 | CI、测试、多集群实验 |
| `kubeadm` | 更接近手工搭建正式集群 | 深入理解集群安装流程、生产前演练 |

如果你的目标是“快速掌握 Kubernetes 基本使用”，优先学 `minikube` 是合理的。

### 1.4 什么时候适合用 Minikube

适合：

- 本地验证一个 Deployment 是否能跑
- 学 `kubectl`
- 测试 `Service`、`Ingress`、`ConfigMap`、`Secret`
- 体验 Dashboard、metrics-server、ingress 等 addon

不适合：

- 真正的生产环境
- 高可用集群
- 大规模性能测试

---

## 2. 先建立最小认知

在真正开始用之前，先记住这几个概念。

### 2.1 Driver

`driver` 决定 `minikube` 用什么方式在本地创建节点。

常见 driver：

- `docker`
- `virtualbox`
- `qemu`
- `hyperv`

在 `WSL2 + Docker Desktop` 下，最常见的组合是：

```bash
minikube start --driver=docker --container-runtime=containerd
```

### 2.2 Profile

`profile` 可以理解成“一个独立的 minikube 集群实例”。

例如：

- `minikube` 默认 profile
- `dev` profile
- `test` profile

你可以同时维护多个本地实验集群。

### 2.3 Addon

`addon` 是 `minikube` 提供的一些开箱即用组件，例如：

- `dashboard`
- `metrics-server`
- `ingress`

这也是 `minikube` 很适合初学者的原因之一。

### 2.4 Kubectl Context

当你执行：

```bash
kubectl get pods -A
```

`kubectl` 实际上是根据当前 context 去连某个 Kubernetes 集群。

所以你最好习惯先看一下：

```bash
kubectl config current-context
```

确认自己操作的是不是当前 `minikube` 集群。

---

## 3. 最小上手流程

这一节只做一件事：先把一个本地集群跑起来。

### 3.1 启动集群

推荐命令：

```bash
minikube start --driver=docker --container-runtime=containerd --cpus=2 --memory=4096
```

这条命令的含义：

- `--driver=docker`：用 Docker 作为底层 driver
- `--container-runtime=containerd`：节点里使用 `containerd`
- `--cpus=2 --memory=4096`：给节点明确分配资源

### 3.2 检查状态

```bash
minikube status
kubectl get nodes
kubectl get pods -A
```

你至少应该看到：

- `minikube` 状态为 `Running`
- 节点状态为 `Ready`

### 3.3 停止、恢复、删除

```bash
minikube stop
minikube start
minikube delete
```

理解这三个命令很重要：

- `stop`：停掉集群，但保留状态
- `start`：重新启动已有集群
- `delete`：彻底删除当前集群

如果你把本地环境玩坏了，最省时间的处理方式通常是：

```bash
minikube delete
minikube start --driver=docker --container-runtime=containerd --cpus=2 --memory=4096
```

---

## 4. Minikube 常用命令

这一节尽量按“生命周期”来记，不要死记硬背。

### 4.1 集群生命周期

| 命令 | 作用 |
| --- | --- |
| `minikube start` | 启动集群 |
| `minikube stop` | 停止集群 |
| `minikube pause` | 暂停 Kubernetes 组件 |
| `minikube unpause` | 恢复被暂停的组件 |
| `minikube status` | 查看集群状态 |
| `minikube delete` | 删除集群 |

常见示例：

```bash
minikube start --driver=docker --container-runtime=containerd
minikube stop
minikube status
```

### 4.2 查看信息与排障

| 命令 | 作用 |
| --- | --- |
| `kubectl get nodes` | 看节点状态 |
| `kubectl get pods -A` | 看所有命名空间的 Pod |
| `kubectl describe pod <pod> -n <ns>` | 看 Pod 详细事件 |
| `minikube logs` | 看 minikube 日志 |
| `minikube ssh` | 进入 minikube 节点 |

常见示例：

```bash
kubectl get pods -A
kubectl describe pod -n kubernetes-dashboard kubernetes-dashboard-xxxxx
minikube logs
minikube ssh
```

### 4.3 访问服务

| 命令 | 作用 |
| --- | --- |
| `minikube service <svc> --url` | 获取某个 Service 的访问地址 |
| `minikube service <svc>` | 直接尝试打开该服务 |
| `minikube dashboard --url` | 获取 Dashboard 地址 |
| `minikube dashboard` | 直接打开 Dashboard |
| `minikube tunnel` | 为 `LoadBalancer` 类型服务创建访问通道 |

说明：

- 本地学习时，`minikube service --url` 很实用
- 如果你用了 `Service type=LoadBalancer`，通常需要配合 `minikube tunnel`

### 4.4 插件管理

| 命令 | 作用 |
| --- | --- |
| `minikube addons list` | 查看所有 addon |
| `minikube addons enable <name>` | 启用 addon |
| `minikube addons disable <name>` | 禁用 addon |

常用 addon：

```bash
minikube addons enable dashboard
minikube addons enable metrics-server
minikube addons enable ingress
```

### 4.5 镜像与本地开发

| 命令 | 作用 |
| --- | --- |
| `minikube image load <image>` | 把本地镜像导入 minikube |
| `minikube image ls` | 查看节点中的镜像 |
| `kubectl set image` | 给 Deployment 更新镜像 |

这组命令在本地开发里很常用，因为你往往不想每次都推远程仓库。

### 4.6 Profile 与配置

```bash
minikube profile list
minikube start -p dev
minikube start -p test
minikube config set driver docker
```

如果你后面需要同时保留多个实验环境，`profile` 很重要。

---

## 5. 实践案例

下面这几组案例的目标不是“讲全”，而是让你尽快形成手感。

### 案例一：启动集群并发布一个 Nginx

这是最小可运行案例。做完这组命令，你就能把本地集群和最基本的部署流程串起来。

#### 第一步：启动集群

```bash
# 启动一个本地 minikube 集群
# --driver=docker：底层用 Docker 容器来模拟 minikube 节点
# --container-runtime=containerd：K8s 节点内部用 containerd 运行 Pod
# --cpus=2 --memory=4096：给这个本地集群分配 2 核 CPU 和 4G 内存
minikube start --driver=docker --container-runtime=containerd --cpus=2 --memory=4096
```

如果你想在启动后立刻确认集群是否正常，可以接着执行：

```bash
# 看 minikube 自己的组件状态，确认 host、kubelet、apiserver 是否正常
minikube status

# 看当前集群里有哪些节点
# 对单节点 minikube，通常只会看到 1 个 Ready 节点
kubectl get nodes

# 看所有命名空间里的 Pod
# -A 等价于 --all-namespaces，便于一次看到系统组件是否也都正常启动
kubectl get pods -A
```

#### 第二步：创建 Deployment

```bash
# 创建一个名为 web 的 Deployment
# 使用 nginx:1.27 镜像，默认先起 1 个 Pod
kubectl create deployment web --image=nginx:1.27

# 查看 Deployment 是否创建成功
kubectl get deployments

# 查看 Pod 是否已经进入 Running 状态
kubectl get pods
```

#### 第三步：暴露 Service

```bash
# 为 Deployment web 创建一个 Service
# --type=NodePort：把集群内 80 端口映射成节点上的一个高位端口，方便从宿主机访问
# --port=80：Service 对外暴露 80 端口，并转发到后端 Pod
kubectl expose deployment web --type=NodePort --port=80

# 查看 Service 分配到了哪个 ClusterIP 和 NodePort
kubectl get svc
```

#### 第四步：获取访问地址

```bash
# 输出访问 web 这个 Service 的 URL
# 在 WSL2 + Docker driver 环境里，这个命令常常会启动一个临时访问通道
# 因此它可能会占住当前终端；按 Ctrl+C 后，这条临时通道会断开
minikube service web --url
```

把返回的 URL 打开，你应该能看到 Nginx 欢迎页。

#### 第五步：做几个常见动作

扩容：

```bash
kubectl scale deployment web --replicas=3
kubectl get pods
```

查看详细信息：

```bash
kubectl describe deployment web
kubectl describe svc web
```

删除：

```bash
kubectl delete svc web
kubectl delete deployment web
```

这一组操作你最好手敲一遍，因为它几乎覆盖了最基础的本地开发流。

### 案例二：打开 Kubernetes Dashboard

Dashboard 的意义不是替代 `kubectl`，而是帮助你建立更直观的资源视角。

#### 第一步：启用插件

```bash
# 启用 Kubernetes Dashboard 插件
minikube addons enable dashboard

# 启用 metrics-server，Dashboard 里很多资源指标依赖它
minikube addons enable metrics-server
```

#### 第二步：确认 Pod 状态

```bash
kubectl get pods -n kubernetes-dashboard
kubectl get pods -n kube-system | grep metrics-server
```

#### 第三步：拿访问地址

```bash
# 输出 Dashboard 的访问地址
# 和 minikube service --url 类似，这个命令也可能以前台代理方式运行
# 所以终端看起来像“卡住”，实际上是在维持访问通道
minikube dashboard --url
```

如果你希望直接打开浏览器，可以用：

```bash
minikube dashboard
```

#### 第四步：如果卡住怎么查

如果命令停在：

```text
Verifying proxy health ...
```

通常说明 Dashboard 对应的 Pod 没有正常跑起来。先查：

```bash
kubectl get pods -n kubernetes-dashboard
kubectl describe pod -n kubernetes-dashboard <pod-name>
```

如果你看到的是：

```text
ImagePullBackOff
```

说明镜像拉取失败，需要继续看 `Events`。

### 案例三：把本地镜像导入 Minikube

这是本地开发最有价值的能力之一。

假设你当前目录里有一个应用镜像，已经在本机构建完成：

```bash
docker build -t demo-app:v1 .
```

把它导入 minikube：

```bash
minikube image load demo-app:v1
minikube image ls | grep demo-app
```

然后你的 Deployment 就可以直接引用这个镜像：

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: demo-app
spec:
  replicas: 1
  selector:
    matchLabels:
      app: demo-app
  template:
    metadata:
      labels:
        app: demo-app
    spec:
      containers:
        - name: demo-app
          image: demo-app:v1
          imagePullPolicy: IfNotPresent
          ports:
            - containerPort: 8080
```

这里的关键点是：

- `minikube image load`：把镜像送进节点
- `imagePullPolicy: IfNotPresent`：避免 Kubernetes 强制去远程拉

这样你本地改代码、重建镜像、重新加载、再更新 Deployment，就能完成一个高频开发闭环。

---

## 6. 常见问题

这一节只放最容易踩的坑。

### 6.1 `ImagePullBackOff`

含义：Kubernetes 拉镜像失败了。

先查：

```bash
kubectl describe pod <pod-name> -n <namespace>
```

重点看 `Events`。

常见原因：

- 镜像名写错
- 网络不通
- 私有仓库未登录
- Docker Hub 拉取限流

### 6.2 `429 Too Many Requests`

如果你看到类似错误：

```text
toomanyrequests: You have reached your unauthenticated pull rate limit
```

说明你命中了 Docker Hub 未登录拉取限流。

这在 Dashboard 相关镜像上非常常见。

处理思路：

- 在宿主机执行 `docker login`
- 删除失败的 Pod，让它重新拉取
- 或者手动把镜像提前拉到本地/节点里

### 6.3 `minikube dashboard --url` 一直卡住

先不要盯着 URL 命令本身，先看 Pod 是否正常：

```bash
kubectl get pods -n kubernetes-dashboard
```

如果 Dashboard Pod 不是 `Running`，那就不是代理命令的问题，而是后端服务没起来。

### 6.4 `minikube start` 启动失败

如果你在 `WSL2 + Docker Desktop` 环境里遇到奇怪问题，优先试：

```bash
minikube delete
minikube start --driver=docker --container-runtime=containerd --cpus=2 --memory=4096
```

很多问题并不是 Kubernetes 对象本身有问题，而是本地运行时组合不稳定。

---

## 7. 推荐学习路径

如果你的目标是“快速掌握 minikube 是什么和如何使用”，建议按这个顺序练：

1. 先把集群成功启动起来
2. 跑通一个 `Deployment + Service`
3. 学会用 `kubectl get`、`describe`、`logs`
4. 打开 Dashboard 看资源关系
5. 练一次本地镜像加载
6. 最后再去看 `Ingress`、`ConfigMap`、`Secret`

不要一开始就追求学全。

最有效的路径是：

- 先会启动
- 再会部署
- 再会访问
- 再会排障

---

## 8. 一页速记

如果你只想先记住最关键的内容，先记这几个命令：

```bash
minikube start --driver=docker --container-runtime=containerd --cpus=2 --memory=4096
minikube status
kubectl get nodes
kubectl get pods -A
kubectl create deployment web --image=nginx:1.27
kubectl expose deployment web --type=NodePort --port=80
minikube service web --url
minikube addons enable dashboard
minikube dashboard --url
minikube delete
```

如果你能理解并跑通上面这几条命令，已经足够开始用 `minikube` 学 Kubernetes。
