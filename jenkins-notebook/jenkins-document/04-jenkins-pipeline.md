# 第 4 步：Jenkins Pipeline 实战

这是整个教程的**核心章节**。我们将一步步创建一条完整的 CI/CD Pipeline。

## 4.1 创建 Pipeline Job

### 方式一：通过经典 UI 创建（推荐）

1. **Dashboard → New Item**
2. 输入名称（如 `jenkins-demo`），选择 **Pipeline**
3. 在 "Pipeline" 配置段中：
   - Definition 选 "Pipeline script from SCM"
   - SCM 选 "Git"
   - Repository URL 填入你的仓库地址
   - Script Path 保持 `Jenkinsfile`
4. 保存

### 方式二：通过 Blue Ocean 创建（可选）

Blue Ocean 仍能展示 Pipeline，但官方已经说明它不会再获得新功能增强。因此新实践建议先熟悉 Jenkins 经典 UI 和 Pipeline Graph View。

1. 打开 `http://localhost:8080/blue`
2. 点击 "Create Pipeline"
3. 选择 Git，填入你的仓库地址（如 `https://github.com/你的用户名/jenkins-demo`）
4. 如果仓库是公开的，不需要凭据
5. Jenkins 会扫描仓库中的 `Jenkinsfile` 并自动创建 Pipeline

## 4.2 编写 Jenkinsfile

在项目根目录创建 `Jenkinsfile`：

```groovy
pipeline {
    // 在任何可用 agent 上执行
    agent any

    // 环境变量，整个 pipeline 都能用
    environment {
        DOCKER_COMPOSE_FILE = 'docker-compose.yml'
        BACKEND_IMAGE = 'jenkins-demo-backend'
        FRONTEND_IMAGE = 'jenkins-demo-frontend'
    }

    stages {
        // ========== Stage 1: 检出代码 ==========
        stage('Checkout') {
            steps {
                echo '📦 拉取代码...'
                checkout scm
            }
        }

        // ========== Stage 2: 后端检查与测试 ==========
        stage('Backend Lint & Test') {
            steps {
                echo '🔍 后端代码检查与测试...'
                sh '''
                    mkdir -p reports
                    cd backend
                    uv sync --frozen
                    uv run ruff check .
                    uv run pytest tests/ -v --junitxml=../reports/backend-test.xml
                '''
            }
            post {
                always {
                    // 收集测试报告，Jenkins UI 中可直接查看
                    junit 'reports/backend-test.xml'
                }
            }
        }

        // ========== Stage 3: 前端检查与测试 ==========
        stage('Frontend Test') {
            steps {
                echo '🧪 前端测试...'
                sh '''
                    mkdir -p reports
                    cd frontend
                    npm ci
                    npm run test -- --reporter=junit --outputFile=../reports/frontend-test.xml
                '''
            }
            post {
                always {
                    junit 'reports/frontend-test.xml'
                }
            }
        }

        // ========== Stage 4: 构建 Docker 镜像 ==========
        stage('Build Images') {
            steps {
                echo '🐳 构建后端镜像...'
                sh 'docker build -t ${BACKEND_IMAGE}:${BUILD_NUMBER} ./backend'
                echo '🐳 构建前端镜像...'
                sh 'docker build -t ${FRONTEND_IMAGE}:${BUILD_NUMBER} ./frontend'
            }
        }

        // ========== Stage 5: 部署 ==========
        stage('Deploy') {
            steps {
                echo '🚀 部署服务...'
                sh '''
                    # 停止旧容器
                    docker compose down --remove-orphans || true

                    # 用新镜像启动
                    BACKEND_TAG=${BUILD_NUMBER} FRONTEND_TAG=${BUILD_NUMBER} \
                    docker compose up -d
                '''
            }
        }
    }

    // ========== 构建后操作 ==========
    post {
        success {
            echo '✅ Pipeline 执行成功！'
            echo "后端: http://localhost:8000/api/health"
            echo "前端: http://localhost:3000"
        }
        failure {
            echo '❌ Pipeline 执行失败，请检查日志。'
        }
        always {
            // 清理旧镜像，避免磁盘占满
            sh 'docker image prune -f || true'
        }
    }
}
```

## 4.3 Pipeline 逐段解析

### `agent any`

指定这条 Pipeline 在哪里执行。`any` 表示 Jenkins 可以把任务分配给任意一个空闲的 agent。

可以先把几个词这样区分：

- **Jenkins Controller**：Jenkins 的大脑，负责管理页面、任务配置、调度 Pipeline。
- **Node**：一台可以执行任务的机器，可以是 controller 所在机器，也可以是另一台服务器、容器、Kubernetes Pod。
- **Agent**：运行在 Node 上、真正接收 Jenkins 指令并执行命令的执行环境。
- **Executor**：一个 Node 上可同时执行几个任务的槽位。
- **Workspace**：agent 检出代码、执行命令的工作目录。

所以 `agent any` 的意思不是“随便找一台生产服务器部署”，而是“找一个 Jenkins 认为可用的执行环境来跑后面的 `sh`、`docker build`、`docker compose` 等命令”。

如果 Jenkins 只有一台机器，那么 `agent any` 基本就会在这台机器上执行。如果 Jenkins 有多台 agent，`any` 可能把任务分配到任意一台空闲机器。生产环境通常会给不同机器打标签，然后显式指定：

```groovy
agent { label 'docker-builder' }
```

或者针对不同 stage 指定不同执行环境：

```groovy
pipeline {
    agent none

    stages {
        stage('Build') {
            agent { label 'docker-builder' }
            steps {
                sh 'docker build -t demo:${BUILD_NUMBER} .'
            }
        }

        stage('Deploy') {
            agent { label 'deploy-runner' }
            steps {
                sh 'docker compose up -d'
            }
        }
    }
}
```

也可以让某个 Stage 在临时 Docker 容器中执行，例如用 Python 镜像跑测试：

```groovy
agent {
    docker {
        image 'python:3.12'  // 在 Python 容器中执行
    }
}
```

### `environment`

定义环境变量，后续 Stage 中通过 `${变量名}` 引用。

`${BUILD_NUMBER}` 是 Jenkins 内置变量，每次构建递增。

### `checkout scm`

从 SCM（源代码管理，我们配的是 Git）拉取最新代码。

### `post` 块

定义 Stage 或 Pipeline 结束后的操作：
- `always`：不管成功失败都执行
- `success`：只有成功时执行
- `failure`：只有失败时执行

### `junit`

Jenkins 内置的测试报告收集指令。收集 JUnit XML 格式的测试结果，在 Jenkins UI 中展示测试趋势图。

## 4.4 调整 docker-compose.yml 支持动态镜像标签

```yaml
services:
  backend:
    image: jenkins-demo-backend:${BACKEND_TAG:-latest}
    ports:
      - "8000:8000"

  frontend:
    image: jenkins-demo-frontend:${FRONTEND_TAG:-latest}
    ports:
      - "3000:80"
    depends_on:
      - backend
```

这里的关键点是：前面的 Build Stage 已经执行过 `docker build -t jenkins-demo-backend:${BUILD_NUMBER} ./backend`，所以 compose 里直接引用已经构建好的镜像，不再写 `build:`。

Deploy Stage 中这句：

```bash
BACKEND_TAG=${BUILD_NUMBER} FRONTEND_TAG=${BUILD_NUMBER} docker compose up -d
```

等价于告诉 Docker Compose：

- 后端使用 `jenkins-demo-backend:${BUILD_NUMBER}`
- 前端使用 `jenkins-demo-frontend:${BUILD_NUMBER}`
- `-d` 表示后台启动容器

## 4.5 CD 阶段到底在哪里启动项目？

Jenkins 不会神奇地“启动项目”。CD 阶段本质上就是 Jenkins 在某个 agent 上执行部署命令。项目启动在哪里，取决于 Deploy Stage 的命令是在哪里执行的，以及这条命令操作的是哪个环境。

### 情况 1：CI/CD 和应用都在同一台机器

这是本教程的本地练习场景：

```
Jenkins agent 所在机器
├── 执行 docker build
├── 执行 docker compose down
└── 执行 docker compose up -d
```

这时 `docker compose up -d` 操作的是当前机器的 Docker。结果就是：旧容器被停止，新容器在同一台机器上启动。

流程是：

```text
push 代码
  -> Jenkins 拉代码
  -> 测试
  -> docker build 生成新镜像
  -> docker compose down 停旧容器
  -> docker compose up -d 用新镜像启动容器
```

如果 Jenkins 本身跑在 Docker 容器里，但挂载了宿主机的 `/var/run/docker.sock`，那么 Jenkins 容器里执行的 `docker compose up -d` 实际控制的是宿主机 Docker。也就是说，应用容器还是启动在宿主机 Docker 上。

### 情况 2：CI/CD 和应用在不同机器，但不是 Kubernetes

常见做法是：Jenkins 负责构建镜像并推送到镜像仓库，然后通过 SSH 登录部署机器执行启动命令。

```groovy
stage('Build & Push') {
    steps {
        sh '''
            docker build -t registry.example.com/demo/backend:${BUILD_NUMBER} ./backend
            docker build -t registry.example.com/demo/frontend:${BUILD_NUMBER} ./frontend
            docker push registry.example.com/demo/backend:${BUILD_NUMBER}
            docker push registry.example.com/demo/frontend:${BUILD_NUMBER}
        '''
    }
}

stage('Deploy') {
    steps {
        sshagent(['prod-ssh-key']) {
            sh '''
                ssh deploy@prod-server "
                  cd /opt/demo &&
                  BACKEND_TAG=${BUILD_NUMBER} FRONTEND_TAG=${BUILD_NUMBER} docker compose pull &&
                  BACKEND_TAG=${BUILD_NUMBER} FRONTEND_TAG=${BUILD_NUMBER} docker compose up -d
                "
            '''
        }
    }
}
```

这时要注意：

- `docker build` 发生在 Jenkins agent 上。
- `docker push` 把镜像传到镜像仓库。
- `ssh deploy@prod-server` 后面的 `docker compose up -d` 发生在部署服务器上。
- 应用最终启动在 `prod-server`，不是 Jenkins 机器。

### 情况 3：CI/CD 和应用在同一个集群，比如 Kubernetes

如果应用跑在 Kubernetes，Jenkins 通常不直接 `docker compose up`，而是更新 Kubernetes 资源：

```groovy
stage('Deploy') {
    steps {
        sh '''
            kubectl set image deployment/backend backend=registry.example.com/demo/backend:${BUILD_NUMBER}
            kubectl rollout status deployment/backend
        '''
    }
}
```

这时流程是：

```text
Jenkins 构建镜像
  -> 推送镜像到 registry
  -> kubectl 更新 Deployment
  -> Kubernetes 调度 Pod 到集群中的某些节点
```

在 Kubernetes 场景中，“启动项目”的动作不是 Jenkins 直接做的，而是 Jenkins 修改期望状态，Kubernetes 负责拉取新镜像、创建新 Pod、停止旧 Pod。

### 一句话总结

Deploy Stage 不是一个特殊魔法阶段，它只是执行命令：

- 同一台机器：直接 `docker compose up -d`。
- 不同机器：Jenkins 通过 SSH 让目标机器执行 `docker compose up -d`。
- Kubernetes 集群：Jenkins 执行 `kubectl` 或 Helm，真正的启动由 Kubernetes 完成。

## 4.6 执行 Pipeline

### 手动触发

1. 进入 Pipeline 页面
2. 点击 "Build Now"
3. 点击构建号（如 #1）→ **Console Output** 查看实时日志

### 查看 Pipeline 可视化

进入某次构建页面后，可以通过 Jenkins 自带的 Pipeline 阶段视图或 Pipeline Graph View 查看执行过程：

```
 ✓ Checkout ──→ ✓ Backend Lint & Test ──→ ✓ Frontend Test ──→ ✓ Build ──→ ✓ Deploy
                 (20s)                     (15s)               (45s)        (5s)
```

每个 Stage 点进去可以看到详细日志。

## 4.7 常见问题

### Q: Jenkins 容器里执行 docker 命令报 "docker: not found"

**原因**：Jenkins 容器内没有安装 Docker CLI。

**解决**：使用第 2 步中的 `Dockerfile.jenkins` 构建自定义 Jenkins 镜像。仅挂载 `docker.sock` 不够，容器内还必须安装 Docker CLI 和 Docker Compose 插件。

```bash
docker compose up -d --build
docker exec -it jenkins docker compose version
```

### Q: uv 命令找不到

确保 Jenkins 容器内有 `uv`。本教程的 `Dockerfile.jenkins` 已经从 `ghcr.io/astral-sh/uv` 复制了 `uv` 和 `uvx`，Pipeline 会通过 `uv sync --frozen` 在 `backend/.venv` 中安装 `pytest`、`ruff` 等项目依赖。

### Q: npm ci 报错说缺 package-lock.json

`npm ci` 要求项目中存在 `package-lock.json`。在 `frontend` 目录执行一次 `npm install`，然后把生成的 `package-lock.json` 提交到 Git。

### Q: npm ci 很慢

第一次构建后 Jenkins workspace 会被保留，`npm ci` 会清除 `node_modules` 重新安装。可以挂载 npm 缓存卷，或在真实项目中使用专门的 Node 构建 agent。

---

**下一步**：[05-automation.md](./05-automation.md) — 配置自动化触发
