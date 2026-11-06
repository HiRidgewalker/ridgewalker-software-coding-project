# 第 6 步：实际开发中的最佳实践

## 6.1 环境分离

不要把所有环境混在一起。典型的项目有三个环境：

```
dev (开发)  →  staging (预发布)  →  prod (生产)
```

### 通过 Jenkinsfile 参数化实现

```groovy
pipeline {
    agent any

    parameters {
        choice(
            name: 'ENVIRONMENT',
            choices: ['dev', 'staging', 'prod'],
            description: '选择部署环境'
        )
    }

    stages {
        stage('Deploy') {
            steps {
                sh """
                    docker compose -f docker-compose.${params.ENVIRONMENT}.yml up -d
                """
            }
        }
    }
}
```

不同环境的 compose 文件可以定义不同的端口、资源限制、副本数。

## 6.2 敏感信息管理 — Jenkins Credentials

**绝对不要**把密码、API Key、Token 写在 Jenkinsfile 或代码里！

### 添加凭据

1. **Manage Jenkins → Credentials → System → Global credentials**
2. **Add Credentials**

常用凭据类型：

| 类型 | 用途 |
|------|------|
| Secret text | API Token、密码 |
| Username with password | Docker Hub、私有仓库登录 |
| SSH Username with private key | Git 拉取、服务器部署 |
| Secret file | kubeconfig、.env 文件 |

### 在 Pipeline 中使用凭据

```groovy
pipeline {
    agent any

    environment {
        // 方式一：直接绑定为环境变量
        DOCKER_HUB_CREDS = credentials('docker-hub-credentials-id')
    }

    stages {
        stage('Push Image') {
            steps {
                sh '''
                    # credentials() 会自动生成 _USR 和 _PSW 后缀变量。
                    # 不要 echo 密码，Jenkins 虽然会尽量脱敏，但日志里打印密钥不是好习惯。
                    echo "$DOCKER_HUB_CREDS_PSW" | docker login -u "$DOCKER_HUB_CREDS_USR" --password-stdin
                '''
            }
        }

        stage('Deploy with SSH') {
            steps {
                // 方式二：使用 withCredentials 块
                withCredentials([
                    string(credentialsId: 'api-secret-key', variable: 'API_KEY')
                ]) {
                    sh '''
                        # 这里演示如何把密钥传给部署命令，不要把密钥打印到日志。
                        ./deploy.sh
                    '''
                }
            }
        }
    }
}
```

## 6.3 Pipeline 复用 — Shared Library

当你有 10 个项目，每个都需要类似的 Pipeline（拉代码 → 测试 → 构建 → 部署），复制粘贴 Jenkinsfile 会变得很痛苦。

**解决方案**：Jenkins Shared Library。

### 创建 Shared Library

```
jenkins-shared-library/           # 单独的 Git 仓库
├── vars/
│   └── pythonServicePipeline.groovy   # 自定义步骤
└── src/
    └── org/demo/
        └── DockerUtils.groovy         # 可复用的工具类
```

### 定义可复用的 Pipeline 模板

`vars/pythonServicePipeline.groovy`:

```groovy
def call(Map config) {
    pipeline {
        agent any
        stages {
            stage('Checkout') {
                steps {
                    checkout scm
                }
            }
            stage('Test') {
                steps {
                    sh "cd ${config.servicePath} && uv sync --frozen && uv run pytest tests/ -v"
                }
            }
            stage('Build') {
                steps {
                    sh "docker build -t ${config.imageName} ${config.servicePath}"
                }
            }
        }
    }
}
```

### 在项目中引用

在 Jenkins 中配置好 Shared Library 后，每个项目的 Jenkinsfile 只需一行：

```groovy
@Library('my-shared-library') _

pythonServicePipeline(
    servicePath: 'backend',
    imageName: 'my-app-backend'
)
```

> 对初学者来说，先不用学 Shared Library。当你有 3 个以上项目时再来重构。

## 6.4 构建缓存优化

### Docker 构建缓存

```dockerfile
# ✅ 好的做法：先 COPY 依赖文件，再 COPY 源码
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev --no-install-project  # 这层只有依赖文件变才会重建
COPY . .                                # 源码变了不影响上面的缓存
```

```dockerfile
# ❌ 差的做法：每次源码变动都要重新安装依赖
COPY . .
RUN uv sync --frozen --no-dev          # 每次 build 都重装
```

### 多阶段构建（前端）

```dockerfile
# ✅ 构建在 node 镜像中，运行在 nginx 中，最终镜像很小
FROM node:20 AS builder
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build

FROM nginx:alpine
COPY --from=builder /app/dist /usr/share/nginx/html
# 最终镜像只有几十 MB
```

### npm/pip 依赖缓存

```groovy
stage('Install Dependencies') {
    steps {
        sh '''
            cd frontend
            npm ci --prefer-offline    # 优先用缓存
        '''
    }
}
```

挂载缓存卷到 Jenkins 容器：

```yaml
# docker-compose.yml for Jenkins
volumes:
  - npm_cache:/root/.npm
  - pip_cache:/root/.cache/pip
```

## 6.5 并行执行

测试和代码检查可以同时运行，节省时间：

```groovy
stage('Check & Test') {
    parallel {
        stage('Backend') {
            steps {
                sh 'cd backend && uv sync --frozen && uv run ruff check . && uv run pytest tests/ -v'
            }
        }
        stage('Frontend') {
            steps {
                sh 'cd frontend && npm ci && npm run test'
            }
        }
    }
}
```

## 6.6 常用插件推荐

| 插件 | 用途 |
|------|------|
| **Pipeline Graph View** | 当前推荐的 Pipeline 可视化插件之一 |
| **Docker Pipeline** | Pipeline 中使用 Docker |
| **GitHub Integration** | Webhook 触发 |
| **Slack Notification** | 构建结果推送到 Slack |
| **Timestamper** | 日志加时间戳 |
| **Build Timeout** | 构建超时自动中止 |
| **Workspace Cleanup** | 构建前后清理工作区 |
| **Pipeline Utility Steps** | 读取 JSON/YAML/CSV 等 |
| **Email Extension** | 构建失败邮件通知 |
| **Credentials Binding** | 安全管理凭据 |
| **NodeJS** | 如果不在 Jenkins 镜像中安装 Node.js，可用它管理 Node 版本 |

Blue Ocean 仍能使用，但官方已说明它不会再获得新功能增强，新项目建议优先使用 Jenkins 经典 UI、Pipeline Stage View 或 Pipeline Graph View。

## 6.7 总结：一条完整的真实项目 Pipeline

综合前面所有知识点，一条生产级 Pipeline 长这样：

```groovy
pipeline {
    agent any

    environment {
        REGISTRY = 'docker.io/myorg'
        BACKEND_IMAGE = "${REGISTRY}/demo-backend"
        FRONTEND_IMAGE = "${REGISTRY}/demo-frontend"
    }

    parameters {
        choice(name: 'ENV', choices: ['dev', 'prod'], description: '部署环境')
    }

    triggers {
        githubPush()
    }

    options {
        timeout(time: 30, unit: 'MINUTES')        // 30 分钟超时
        buildDiscarder(logRotator(numToKeepStr: '10'))  // 只保留最近 10 次构建
    }

    stages {
        stage('Checkout') {
            steps { checkout scm }
        }

        stage('Lint & Test') {
            parallel {
                stage('Backend') {
                    steps {
                        sh '''
                            mkdir -p reports
                            cd backend
                            uv sync --frozen
                            uv run ruff check .
                            uv run pytest tests/ --junitxml=../reports/be-test.xml
                        '''
                    }
                    post { always { junit 'reports/be-test.xml' } }
                }
                stage('Frontend') {
                    steps {
                        sh '''
                            mkdir -p reports
                            cd frontend
                            npm ci
                            npm run test -- --reporter=junit --outputFile=../reports/fe-test.xml
                        '''
                    }
                    post { always { junit 'reports/fe-test.xml' } }
                }
            }
        }

        stage('Build & Push') {
            when { branch 'main' }
            steps {
                sh 'docker build -t ${BACKEND_IMAGE}:${BUILD_NUMBER} ./backend'
                sh 'docker build -t ${FRONTEND_IMAGE}:${BUILD_NUMBER} ./frontend'
                sh 'docker push ${BACKEND_IMAGE}:${BUILD_NUMBER}'
                sh 'docker push ${FRONTEND_IMAGE}:${BUILD_NUMBER}'
            }
        }

        stage('Deploy') {
            when { branch 'main' }
            steps {
                sh 'docker compose -f docker-compose.${params.ENV}.yml up -d'
            }
        }
    }

    post {
        failure {
            // 发送通知（如配置了 Slack 插件）
            // slackSend(channel: '#alerts', message: "Pipeline failed: ${env.JOB_NAME} #${env.BUILD_NUMBER}")
        }
    }
}
```

---

## 学习完成！

你已完成 Jenkins CI/CD 学习教程。回顾一下你学到了什么：

1. CI/CD 的基本概念和 Jenkins 的角色
2. 用 Docker 在本地运行 Jenkins
3. FastAPI + React 项目的 Docker 化
4. 编写 Jenkinsfile 定义完整流水线
5. 配置 Webhook 实现 push 自动构建
6. 环境分离、凭据管理、缓存优化等实战技巧

**下一步建议**：
- 实际搭建一遍，遇到问题看日志，大部分问题 Google 一下都能解决
- 试着给你的真实项目加上 Jenkins Pipeline
- 学习 GitHub Actions 作为对比（概念相通，语法不同）
