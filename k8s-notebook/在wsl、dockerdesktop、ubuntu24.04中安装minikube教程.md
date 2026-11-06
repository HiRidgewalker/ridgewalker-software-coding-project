# 在 WSL2 + Docker Desktop + Ubuntu 24 中安装 minikube 教程

本文基于以下环境整理：

- Windows + WSL2
- Docker Desktop
- Ubuntu 24.04
- 在 WSL 的 Ubuntu 终端中安装和运行 `minikube`

目标是用一套尽量稳定、少踩坑的方式，在当前环境里安装 `minikube` 并开始学习 Kubernetes。

## 一、环境说明

这套环境的关键点是：

- `minikube` 运行在 WSL2 的 Ubuntu 中
- `minikube` 使用 `docker` 作为 driver
- 但集群内部的 container runtime 推荐使用 `containerd`

推荐组合：

```bash
minikube start --driver=docker --container-runtime=containerd
```

原因很简单：

- 这条路径更贴近当前 Kubernetes 的主流运行方式
- 在 `WSL2 + Docker Desktop` 环境里更稳定
- 可以避开 `docker.service is masked` 一类常见问题

## 二、前置准备

### 1. Windows 侧确认 Docker Desktop 已正确配置

打开 Docker Desktop，确认以下设置已经开启：

1. `Settings -> General -> Use the WSL 2 based engine`
2. `Settings -> Resources -> WSL Integration -> Enable integration with your Ubuntu`

### 2. 在 Ubuntu 中检查基础命令

先确认下面这些命令是否存在：

```bash
which docker
which kubectl
which minikube
```

如果 `docker` 和 `kubectl` 已有，只需要安装 `minikube` 即可。

## 三、安装 minikube

在 Ubuntu 24 中执行：

```bash
curl -LO https://storage.googleapis.com/minikube/releases/latest/minikube-linux-amd64
sudo install minikube-linux-amd64 /usr/local/bin/minikube
rm minikube-linux-amd64
```

安装完成后检查版本：

```bash
minikube version
kubectl version --client
docker version
```

## 四、如果 docker 权限有问题

如果执行 `docker version` 时出现类似错误：

```text
permission denied while trying to connect to the docker API at unix:///var/run/docker.sock
```

可以先把当前用户加入 `docker` 组：

```bash
sudo usermod -aG docker $USER
newgrp docker
```

如果仍然不行，可以在 Windows PowerShell 里重启 WSL：

```powershell
wsl --shutdown
```

然后重新打开 Ubuntu，再执行：

```bash
docker version
```

## 五、推荐的启动方式

不要直接依赖默认行为，建议明确指定 driver 和 container runtime：

```bash
minikube start --driver=docker --container-runtime=containerd --cpus=2 --memory=4096
```

启动成功后验证：

```bash
minikube status
kubectl get nodes
kubectl get pods -A
```

正常情况下应该能看到：

- `minikube` 状态为 `Running`
- 节点状态为 `Ready`

## 六、为什么 `minikube start` 会失败，而显式指定 `containerd` 会成功

很多人会遇到这种情况：

```bash
minikube start
```

启动失败，但下面这条命令却能成功：

```bash
minikube start --driver=docker --container-runtime=containerd --cpus=2 --memory=4096
```

原因是这两个命令走的启动路径不同。

### 1. `minikube start` 依赖默认值

你的 `minikube v1.38.1` 在启动时日志已经提示：

```text
Starting v1.39.0, minikube will default to "containerd" container runtime.
```

这说明在你当前版本里，默认 runtime 还没有切到 `containerd`。  
因此：

```bash
minikube start
```

更接近于：

```bash
minikube start --driver=docker --container-runtime=auto
```

而在你的环境里，这个 `auto` 实际上落到了 `docker` runtime 这条路径上。

### 2. 失败点在于 minikube 试图处理 docker.service

你日志里的关键错误是：

```text
Failed to enable unit: Unit file /lib/systemd/system/docker.service is masked.
Exiting due to RT_DOCKER_RESTART
```

这表示：

- `minikube` 在节点容器内部试图调整并重启 `docker.service`
- 但你当前是 `WSL2 + Docker Desktop`
- 在这种环境里，相关 `docker.service` 并不是一个标准、可自由启停的本地 Docker Engine 服务
- 于是这条启动路径失败

### 3. 显式指定 `containerd` 后，绕开了失败路径

当你执行：

```bash
minikube start --driver=docker --container-runtime=containerd --cpus=2 --memory=4096
```

含义是：

- 外层仍然用 `docker` driver
- 但集群内部的 container runtime 使用 `containerd`

这样 `minikube` 就不会再走那条需要处理 `docker.service` 的路径，因此能够成功启动。

### 4. `--cpus=2` 和 `--memory=4096` 不是根本原因

这两个参数的作用主要是资源分配更明确，能让运行更稳一些，但这次成功的核心原因并不是 CPU 或内存，而是：

```text
--container-runtime=containerd
```

## 七、container-runtime 不同有什么区别

`container-runtime` 决定了 Kubernetes 节点里由谁来负责：

- 拉取镜像
- 创建容器
- 启动 Pod

对学习 Kubernetes 来说，最重要的差异不在于 `Pod`、`Deployment`、`Service` 这些资源怎么写，而在于：

- 集群能不能稳定启动
- 镜像如何进入集群
- 出问题时应该用什么方式排查

### 1. `containerd`

这是当前 Kubernetes 最主流的运行时之一。

特点：

- 更贴近 Kubernetes 当前主流实现
- 结构更简单
- 与 CRI 对接更自然
- 在 `minikube + docker driver` 场景下更推荐

### 2. `cri-o`

也是原生 CRI 运行时，定位更偏 Kubernetes-only。

特点：

- 更专注 Kubernetes
- 常见于某些企业发行版或特定平台
- 本地学习环境里通常没有 `containerd` 通用

### 3. `docker`

很多人最熟悉的是 Docker，但要注意：

- 从 Kubernetes `v1.24` 开始，`dockershim` 已移除
- Kubernetes 不再像过去那样直接内建对 Docker 的老式对接
- 因此在现代 Kubernetes 里，`docker` runtime 并不是最推荐的默认学习路径

### 4. 实际使用差异

如果用 `containerd`，更建议通过 Kubernetes 方式和 `minikube` 方式管理集群，例如：

```bash
kubectl get pods -A
minikube status
```

如果你本地构建了镜像：

```bash
docker build -t myapp:dev .
```

更稳妥的做法是把镜像显式导入到 minikube：

```bash
minikube image load myapp:dev
```

不要默认假设宿主机里 `docker build` 出来的镜像一定能直接被集群看到。

### 5. 当前环境该怎么选

对 `WSL2 + Docker Desktop + Ubuntu 24 + minikube --driver=docker` 这套环境，建议直接使用：

```bash
minikube config set driver docker
minikube config set container-runtime containerd
```

这样以后只执行：

```bash
minikube start
```

通常也会走你已经验证过的成功路径。

## 八、建议设置默认配置

为了避免每次都写完整参数，建议设置默认值：

```bash
minikube config set driver docker
minikube config set container-runtime containerd
```

之后再启动：

```bash
minikube start --cpus=2 --memory=4096
```

或者直接：

```bash
minikube start
```

如果你机器资源比较紧张，建议还是明确写上资源参数。

## 九、常用学习命令

### 1. 查看集群状态

```bash
minikube status
kubectl get nodes
kubectl get pods -A
```

### 2. 打开 dashboard

```bash
minikube dashboard
```

如果只想获取访问地址：

```bash
minikube dashboard --url
```

### 3. 启用常用 addon

```bash
minikube addons enable metrics-server
minikube addons enable ingress
```

### 4. 部署一个简单测试服务

```bash
kubectl create deployment hello --image=nginx
kubectl expose deployment hello --type=NodePort --port=80
minikube service hello
```

## 十、常见问题排查

### 1. 报错 `docker.service is masked`

这通常不是镜像下载问题，而是 `docker` runtime 路径在当前环境中不兼容。  
优先改为：

```bash
minikube delete
minikube start --driver=docker --container-runtime=containerd --cpus=2 --memory=4096
```

### 2. 报错 `permission denied while trying to connect to docker.sock`

说明当前用户不能正常访问 Docker socket。  
处理方式：

```bash
sudo usermod -aG docker $USER
newgrp docker
```

必要时执行：

```powershell
wsl --shutdown
```

然后重新打开 Ubuntu。

### 3. 日志里出现 `Local proxy ignored`

例如：

```text
Local proxy ignored: not passing HTTP_PROXY=http://127.0.0.1:7897 to docker env.
```

这通常不是本次启动失败的主因。  
它的意思是：

- 你当前设置的是本地回环地址代理 `127.0.0.1`
- 这个地址对 minikube 节点容器内部不一定可见
- 所以 minikube 没把它直接传进去

如果以后遇到 Pod 拉镜像失败，再单独处理代理问题。

### 4. 启动失败后先清理再重试

```bash
minikube delete
minikube start --driver=docker --container-runtime=containerd
```

## 十一、推荐学习顺序

装好 minikube 后，可以按下面顺序学习：

1. `kubectl get / describe / logs / exec`
2. `Pod / Deployment / ReplicaSet`
3. `Service / NodePort / ClusterIP`
4. `Namespace`
5. `ConfigMap / Secret`
6. `Ingress`
7. `Volume / PVC`
8. `Helm`

## 十二、总结

对于当前环境：

- `WSL2 + Docker Desktop + Ubuntu 24`
- 使用 `minikube`
- 推荐 `docker` 作为 driver
- 推荐 `containerd` 作为集群内部 runtime

最实用、最稳妥的启动命令是：

```bash
minikube start --driver=docker --container-runtime=containerd --cpus=2 --memory=4096
```

建议同时设置默认配置：

```bash
minikube config set driver docker
minikube config set container-runtime containerd
```

这样更符合当前 Kubernetes 的主流运行方式，也能避开你已经遇到的 `docker.service is masked` 问题。

## 参考资料

- Minikube Docker driver  
  https://minikube.sigs.k8s.io/docs/drivers/docker/
- Minikube start 命令  
  https://minikube.sigs.k8s.io/docs/commands/start/
- Minikube config 文档  
  https://minikube.sigs.k8s.io/docs/handbook/config/
- Kubernetes 容器运行时  
  https://kubernetes.io/zh/docs/setup/production-environment/container-runtimes/
- Dockershim 移除影响说明  
  https://kubernetes.io/docs/tasks/administer-cluster/migrating-from-dockershim/check-if-dockershim-removal-affects-you
- 相关问题参考  
  https://github.com/kubernetes/minikube/issues/17942
