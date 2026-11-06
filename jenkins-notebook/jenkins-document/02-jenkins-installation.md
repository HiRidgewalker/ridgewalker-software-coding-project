# 第 2 步：Jenkins 本地安装与配置

## 2.1 为什么用 Docker 安装 Jenkins？

- 一键启动，不污染宿主机环境
- 可以挂载 Docker socket，让 Jenkins 内部也能用 Docker 命令
- 出问题直接删容器重来，零残留

## 2.2 当前版本基线

截至 2026-06-15，Jenkins 官网下载页显示：

- 当前 LTS：`2.555.3`
- 当前 weekly：`2.568`
- Jenkins 2.555.1 LTS 及之后版本要求 Java 21 或 Java 25，不能再使用 Java 17 运行 controller。

本教程使用你指定的 weekly 镜像 `jenkins/jenkins:2.568-jdk21`。如果想回到 LTS，可以把基础镜像改成 `jenkins/jenkins:lts-jdk21`。

## 2.3 安装步骤

### Step 1：创建 Jenkins 工作目录

在合适的位置创建 Jenkins 的工作目录：

```bash
mkdir -p ~/jenkins_home && cd ~/jenkins_home
```

### Step 2：创建 Dockerfile.jenkins

官方 `jenkins/jenkins` 镜像只包含 Jenkins 本身，不包含 Docker CLI、Docker Compose、Python、Node.js、uv。我们的 Pipeline 会执行 `docker build`、`docker compose`、`uv sync`、`pytest`、`npm ci`，所以需要基于官方镜像做一个本地练习用的自定义镜像。

创建 `Dockerfile.jenkins`：

```dockerfile
FROM jenkins/jenkins:2.568-jdk21

USER root

ARG JENKINS_UC=https://updates.jenkins.io
ARG JENKINS_UC_DOWNLOAD=https://updates.jenkins.io/download
ARG JENKINS_PLUGIN_INFO=https://updates.jenkins.io/current/plugin-versions.json

ENV JENKINS_UC=${JENKINS_UC} \
    JENKINS_UC_DOWNLOAD=${JENKINS_UC_DOWNLOAD} \
    JENKINS_PLUGIN_INFO=${JENKINS_PLUGIN_INFO}

COPY --from=ghcr.io/astral-sh/uv:0.11.4 /uv /uvx /usr/local/bin/

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        ca-certificates \
        curl \
        git \
        gnupg \
        lsb-release \
        nodejs \
        npm \
        python3 && \
    install -m 0755 -d /etc/apt/keyrings && \
    curl -fsSL https://download.docker.com/linux/debian/gpg -o /etc/apt/keyrings/docker.asc && \
    chmod a+r /etc/apt/keyrings/docker.asc && \
    echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.asc] https://download.docker.com/linux/debian $(. /etc/os-release && echo "$VERSION_CODENAME") stable" > /etc/apt/sources.list.d/docker.list && \
    apt-get update && \
    apt-get install -y --no-install-recommends docker-ce-cli docker-compose-plugin && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

USER jenkins
```

插件不在镜像构建阶段安装。这样可以避免 `docker compose build` 卡在 Jenkins 插件下载阶段。Jenkins 启动完成后，先在初始化页面选择 **Install suggested plugins**，再按需安装下面这些插件。

可以保留一个 `plugins.txt` 作为清单：

```text
workflow-aggregator
git
github
github-branch-source
docker-workflow
junit
credentials-binding
pipeline-graph-view
ws-cleanup
timestamper
build-timeout
```

再创建 `.dockerignore`，避免构建 Jenkins 镜像时把 `jenkins_data`、`node_modules` 等目录发送进构建上下文：

```text
jenkins_data/
**/node_modules/
**/dist/
**/.venv/
**/__pycache__/
**/.pytest_cache/
**/.git/
```

### Step 3：创建 docker-compose.yml

创建 `docker-compose.yml`：

```yaml
services:
  jenkins:
    build:
      context: .
      dockerfile: Dockerfile.jenkins
    image: learning-jenkins-controller:2.568-jdk21
    container_name: jenkins
    restart: unless-stopped
    ports:
      - "8080:8080"                          # Web UI
      - "50000:50000"                        # 入站 Agent 通信端口；本地单机练习可保留
    volumes:
      - ./jenkins_data:/var/jenkins_home     # 持久化 Jenkins 数据
      - /var/run/docker.sock:/var/run/docker.sock  # 本地练习：让 Jenkins 调用宿主机 Docker
    environment:
      - TZ=Asia/Shanghai
    user: root                               # 避免文件权限问题
```

> 注意：挂载 `/var/run/docker.sock` 属于本地学习环境的简化做法。这样 Jenkins 容器可以控制宿主机 Docker，生产环境要更谨慎，通常会用专门的构建 agent、远程 Docker 主机或 Kubernetes。

### Step 4：启动 Jenkins

```bash
docker compose up -d --build
```

查看日志，等待初始密码出现：

```bash
docker logs -f jenkins
```

你会看到类似这样的输出：

```
Jenkins initial setup is required. ...
Please use the following password to proceed to installation:

abc123def456...

This may also be found at: /var/jenkins_home/secrets/initialAdminPassword
```

**复制这个密码**，一会儿要用。

### Step 5：打开 Jenkins Web UI

浏览器访问 `http://localhost:8080`，输入刚才复制的初始密码。

## 2.4 初始化配置

### 安装推荐插件

解锁后会看到两个选项：
- **Install suggested plugins** ← 选这个
- Select plugins to install

点击 "Install suggested plugins"，等待安装完成。

### 创建管理员用户

插件安装完成后，创建你的管理员账号：

| 字段 | 示例值 |
|------|--------|
| 用户名 | admin |
| 密码 | 自己设一个 |
| 全名 | Jenkins Admin |
| 邮箱 | 你的邮箱 |

### 实例配置

Jenkins URL 保持默认 `http://localhost:8080/`，点击 "Save and Finish" → "Start using Jenkins"。

## 2.5 安装必要插件

上面的 `Dockerfile.jenkins` 已经预装本教程需要的核心插件。初始化时选择 **Install suggested plugins** 后，如果仍缺插件，可以进入 **Dashboard → Manage Jenkins → Plugins → Available plugins** 搜索安装：

| 插件名 | 用途 |
|--------|------|
| **Docker Pipeline** | 在 Pipeline 中使用 Docker |
| **GitHub Integration** | 集成 GitHub |
| **Pipeline Graph View** | 当前推荐的 Pipeline 可视化插件之一 |
| **Workspace Cleanup** | 清理工作区 |
| **Timestamper** | 日志加时间戳 |
| **Build Timeout** | 构建超时自动中止 |

安装方式：勾选 → 点击 "Install without restart"。

Blue Ocean 仍可用，但官方插件页已说明它不会再获得新功能增强，所以本教程不再把 Blue Ocean 作为主路径。

## 2.6 让 Jenkins 能拉取 GitHub 代码

### 方式一：公开仓库（最简单，本次使用）

如果你的仓库是公开的，直接用 HTTPS 地址拉取即可，无需额外配置。

### 方式二：私有仓库（需要 SSH Key 或 Token）

在 Jenkins 容器内生成 SSH Key：

```bash
docker exec -it jenkins bash
ssh-keygen -t ed25519 -C "jenkins@local"
cat ~/.ssh/id_ed25519.pub   # 把这个添加到 GitHub 的 Deploy Keys
```

在 Jenkins UI 中配置凭据：
1. **Manage Jenkins → Credentials → System → Global credentials**
2. **Add Credentials** → Kind 选 "SSH Username with private key"
3. 填入私钥内容

## 2.7 验证安装

1. 浏览器访问 `http://localhost:8080`，能用管理员账号登录 ✓
2. Jenkins 容器运行正常 `docker ps | grep jenkins` ✓
3. 插件安装完成，没有报错 ✓
4. Jenkins 容器内能执行基础工具：

```bash
docker exec -it jenkins bash
docker version
docker compose version
python3 --version
uv --version
npm --version
```

## 2.8 常见问题

### Q: 构建时报 `failed to resolve source metadata` 或访问 `registry-1.docker.io` EOF

这个错误发生在 Dockerfile 第 1 行：

```dockerfile
FROM jenkins/jenkins:2.568-jdk21
```

它表示 Docker Engine 无法从 Docker Hub 拉取 Jenkins 基础镜像元数据。此时还没有真正开始执行 Dockerfile，问题通常是 Docker Desktop 访问 Docker Hub 的网络、代理或镜像源配置。

先单独验证基础镜像能否拉取：

```bash
docker pull jenkins/jenkins:2.568-jdk21
```

如果这里也失败，优先检查 Docker Desktop 的代理配置：

1. 打开 Docker Desktop
2. 进入 **Settings -> Resources -> Proxies**
3. 配置你的 HTTP/HTTPS 代理
4. Apply & Restart

如果你使用 Clash、v2rayN 等本机代理，注意 Docker Desktop 使用的是自己的 Linux VM，不能简单认为 WSL 里能联网就等于 Docker build 也能联网。

代理修好后重新执行：

```bash
docker compose build --no-cache --progress=plain jenkins
docker compose up -d
```

---

**下一步**：[03-sample-project.md](./03-sample-project.md) — 创建 FastAPI + React 示例项目
