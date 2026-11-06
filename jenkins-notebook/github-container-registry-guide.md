# GitHub Container Registry 使用说明

本文档说明 GitHub Container Registry 是什么、在哪里访问、如何登录、如何构建和推送镜像，以及如何在 Jenkins CI/CD 流程中使用它。

GitHub Container Registry 通常简称为 **GHCR**，镜像地址统一以 `ghcr.io` 开头。

## 官方网址

常用入口：

- GitHub Packages 首页：<https://github.com/features/packages>
- GitHub Container Registry 官方文档：<https://docs.github.com/en/packages/working-with-a-github-packages-registry/working-with-the-container-registry>
- GitHub Packages 权限说明：<https://docs.github.com/en/packages/learn-github-packages/about-permissions-for-github-packages>
- 将 package 关联到 repository：<https://docs.github.com/en/packages/learn-github-packages/connecting-a-repository-to-a-package>
- 创建 GitHub Personal Access Token：<https://github.com/settings/tokens>

## GHCR 是什么

GHCR 是 GitHub 提供的容器镜像仓库，属于 GitHub Packages 的一部分。

它可以用来存储 Docker 镜像和 OCI 镜像。例如：

```text
ghcr.io/cryptolimber/jenkins-demo-backend:1
ghcr.io/cryptolimber/jenkins-demo-frontend:1
ghcr.io/cryptolimber/jenkins-demo-backend:latest
```

在 CI/CD 流程中，GHCR 的定位是：

```text
Jenkins 构建镜像
        |
        v
推送镜像到 GHCR
        |
        v
服务器从 GHCR 拉取镜像
        |
        v
Docker Compose 或 Docker Swarm 启动服务
```

也就是说，GHCR 不负责构建，也不负责部署。它只负责保存镜像。

## 为什么需要镜像仓库

如果没有镜像仓库，Jenkins 构建出来的镜像只存在 Jenkins 所在机器上。

单机阶段虽然也能直接用本地镜像部署，但会有几个问题：

- 换服务器后镜像不存在。
- 多台服务器无法统一拉取镜像。
- 回滚依赖本机是否还保留旧镜像。
- 镜像版本没有统一管理入口。
- Jenkins 机器和部署机器分离后，部署会变麻烦。

使用 GHCR 后，每次构建都可以生成一个明确版本：

```text
ghcr.io/cryptolimber/jenkins-demo-backend:15
ghcr.io/cryptolimber/jenkins-demo-frontend:15
```

回滚时只需要把部署使用的 tag 改回旧版本。

## 镜像命名规则

GHCR 镜像名称格式：

```text
ghcr.io/<namespace>/<image-name>:<tag>
```

说明：

- `ghcr.io`：GitHub Container Registry 固定域名。
- `namespace`：你的 GitHub 用户名或组织名。
- `image-name`：镜像名称。
- `tag`：镜像版本。

例如当前项目可以使用：

```text
ghcr.io/cryptolimber/jenkins-demo-backend:1
ghcr.io/cryptolimber/jenkins-demo-frontend:1
```

也可以增加 `latest`：

```text
ghcr.io/cryptolimber/jenkins-demo-backend:latest
ghcr.io/cryptolimber/jenkins-demo-frontend:latest
```

推荐做法：

- 使用 Jenkins `BUILD_NUMBER` 或 Git commit SHA 作为不可变版本。
- 可以额外打一个 `latest`，但不要只依赖 `latest`。

推荐：

```text
ghcr.io/cryptolimber/jenkins-demo-backend:35
ghcr.io/cryptolimber/jenkins-demo-backend:latest
```

不推荐只用：

```text
ghcr.io/cryptolimber/jenkins-demo-backend:latest
```

因为 `latest` 每次都会变化，不适合精确回滚。

## 创建 GitHub Token

在本地 Docker 或 Jenkins 中推送 GHCR 镜像，需要 GitHub Personal Access Token。

GitHub 官方文档说明，使用命令行访问 GitHub Packages 时，通常使用 **Personal Access Token classic**。

创建入口：

```text
https://github.com/settings/tokens
```

推荐创建 classic token，并根据用途选择权限：

| 用途 | 权限 |
| --- | --- |
| 拉取私有镜像 | `read:packages` |
| 推送镜像 | `write:packages` |
| 删除镜像 | `delete:packages` |

如果只是 Jenkins 推送镜像，通常需要：

```text
write:packages
```

如果服务器要从私有 GHCR 拉取镜像，服务器登录 GHCR 的 token 至少需要：

```text
read:packages
```

不要把 token 写进代码仓库。

## 本地登录 GHCR

在本地或服务器上登录：

```bash
export CR_PAT=你的_GitHub_Token
echo $CR_PAT | docker login ghcr.io -u 你的GitHub用户名 --password-stdin
```

成功后会看到：

```text
Login Succeeded
```

例如：

```bash
export CR_PAT=ghp_xxxxxxxxxxxxxxxxxxxx
echo $CR_PAT | docker login ghcr.io -u cryptolimber --password-stdin
```

注意：

- `-u` 后面是 GitHub 用户名，不是邮箱。
- token 不要直接提交到 Git。
- 服务器拉取私有镜像前也需要登录 GHCR。

## 构建镜像

以后端为例，在有 Dockerfile 的目录构建：

```bash
docker build -t jenkins-demo-backend:1 ./backend
```

前端：

```bash
docker build -t jenkins-demo-frontend:1 ./frontend
```

如果直接构建成 GHCR 名称：

```bash
docker build -t ghcr.io/cryptolimber/jenkins-demo-backend:1 ./backend
docker build -t ghcr.io/cryptolimber/jenkins-demo-frontend:1 ./frontend
```

## 给镜像打 GHCR tag

如果已经有本地镜像：

```text
jenkins-demo-backend:1
jenkins-demo-frontend:1
```

可以给它们打上 GHCR tag：

```bash
docker tag jenkins-demo-backend:1 ghcr.io/cryptolimber/jenkins-demo-backend:1
docker tag jenkins-demo-frontend:1 ghcr.io/cryptolimber/jenkins-demo-frontend:1
```

也可以额外打 `latest`：

```bash
docker tag jenkins-demo-backend:1 ghcr.io/cryptolimber/jenkins-demo-backend:latest
docker tag jenkins-demo-frontend:1 ghcr.io/cryptolimber/jenkins-demo-frontend:latest
```

## 推送镜像到 GHCR

推送指定版本：

```bash
docker push ghcr.io/cryptolimber/jenkins-demo-backend:1
docker push ghcr.io/cryptolimber/jenkins-demo-frontend:1
```

推送 `latest`：

```bash
docker push ghcr.io/cryptolimber/jenkins-demo-backend:latest
docker push ghcr.io/cryptolimber/jenkins-demo-frontend:latest
```

推送成功后，可以在 GitHub 页面查看 package。

常见路径：

```text
GitHub 用户主页 -> Packages
GitHub 仓库主页 -> 右侧 Packages
```

## 拉取镜像

公开镜像可以直接拉取：

```bash
docker pull ghcr.io/cryptolimber/jenkins-demo-backend:1
```

私有镜像需要先登录：

```bash
echo $CR_PAT | docker login ghcr.io -u cryptolimber --password-stdin
docker pull ghcr.io/cryptolimber/jenkins-demo-backend:1
```

运行：

```bash
docker run -d --name backend -p 8000:8000 ghcr.io/cryptolimber/jenkins-demo-backend:1
```

## 在 Docker Compose 中使用 GHCR 镜像

原来本地镜像可能是：

```yaml
services:
  backend:
    image: jenkins-demo-backend:${BACKEND_TAG:-latest}

  frontend:
    image: jenkins-demo-frontend:${FRONTEND_TAG:-latest}
```

改成 GHCR 后：

```yaml
services:
  backend:
    image: ghcr.io/cryptolimber/jenkins-demo-backend:${BACKEND_TAG:-latest}
    ports:
      - "8000:8000"

  frontend:
    image: ghcr.io/cryptolimber/jenkins-demo-frontend:${FRONTEND_TAG:-latest}
    ports:
      - "3000:80"
    depends_on:
      - backend
```

部署指定版本：

```bash
BACKEND_TAG=15 FRONTEND_TAG=15 docker compose up -d
```

回滚到旧版本：

```bash
BACKEND_TAG=12 FRONTEND_TAG=12 docker compose up -d
```

如果镜像是私有的，执行 `docker compose up -d` 的服务器必须先登录 GHCR。

## 在 Jenkins 中使用 GHCR

Jenkins 使用 GHCR 时，一般需要做三件事：

1. 在 Jenkins 中保存 GitHub Token。
2. Jenkins 构建镜像。
3. Jenkins 登录 GHCR 并推送镜像。

### Jenkins 凭据配置

在 Jenkins 中添加凭据：

```text
Manage Jenkins
  -> Credentials
  -> System
  -> Global credentials
  -> Add Credentials
```

推荐类型：

```text
Username with password
```

填写：

```text
Username: GitHub 用户名，例如 cryptolimber
Password: GitHub Personal Access Token
ID: ghcr-credentials
```

Jenkinsfile 中通过 `credentialsId: 'ghcr-credentials'` 使用。

### Jenkinsfile 示例

示例：

```groovy
pipeline {
    agent any

    environment {
        REGISTRY = 'ghcr.io'
        GHCR_NAMESPACE = 'cryptolimber'
        BACKEND_IMAGE = 'jenkins-demo-backend'
        FRONTEND_IMAGE = 'jenkins-demo-frontend'
    }

    stages {
        stage('Build Images') {
            steps {
                sh '''
                    docker build -t ${REGISTRY}/${GHCR_NAMESPACE}/${BACKEND_IMAGE}:${BUILD_NUMBER} ./backend
                    docker build -t ${REGISTRY}/${GHCR_NAMESPACE}/${FRONTEND_IMAGE}:${BUILD_NUMBER} ./frontend

                    docker tag ${REGISTRY}/${GHCR_NAMESPACE}/${BACKEND_IMAGE}:${BUILD_NUMBER} ${REGISTRY}/${GHCR_NAMESPACE}/${BACKEND_IMAGE}:latest
                    docker tag ${REGISTRY}/${GHCR_NAMESPACE}/${FRONTEND_IMAGE}:${BUILD_NUMBER} ${REGISTRY}/${GHCR_NAMESPACE}/${FRONTEND_IMAGE}:latest
                '''
            }
        }

        stage('Push Images') {
            steps {
                withCredentials([usernamePassword(
                    credentialsId: 'ghcr-credentials',
                    usernameVariable: 'GHCR_USERNAME',
                    passwordVariable: 'GHCR_TOKEN'
                )]) {
                    sh '''
                        echo "${GHCR_TOKEN}" | docker login ${REGISTRY} -u "${GHCR_USERNAME}" --password-stdin

                        docker push ${REGISTRY}/${GHCR_NAMESPACE}/${BACKEND_IMAGE}:${BUILD_NUMBER}
                        docker push ${REGISTRY}/${GHCR_NAMESPACE}/${FRONTEND_IMAGE}:${BUILD_NUMBER}

                        docker push ${REGISTRY}/${GHCR_NAMESPACE}/${BACKEND_IMAGE}:latest
                        docker push ${REGISTRY}/${GHCR_NAMESPACE}/${FRONTEND_IMAGE}:latest
                    '''
                }
            }
        }

        stage('Deploy') {
            steps {
                sh '''
                    BACKEND_TAG=${BUILD_NUMBER} FRONTEND_TAG=${BUILD_NUMBER} docker compose up -d
                '''
            }
        }
    }
}
```

实际项目中，`Deploy` 阶段需要保证 `docker-compose.yml` 里的 image 已经改成 GHCR 地址。

## 推荐的 Jenkins 镜像版本策略

推荐每次构建推送两个 tag：

```text
ghcr.io/cryptolimber/jenkins-demo-backend:${BUILD_NUMBER}
ghcr.io/cryptolimber/jenkins-demo-backend:latest
```

其中：

- `${BUILD_NUMBER}` 用于精确部署和回滚。
- `latest` 用于查看当前最新版本，但不建议依赖它做回滚。

例如第 20 次构建：

```text
ghcr.io/cryptolimber/jenkins-demo-backend:20
ghcr.io/cryptolimber/jenkins-demo-backend:latest
```

第 21 次构建：

```text
ghcr.io/cryptolimber/jenkins-demo-backend:21
ghcr.io/cryptolimber/jenkins-demo-backend:latest
```

这时 `:20` 仍然存在，`:latest` 会指向第 21 次构建结果。

## Package 可见性

GHCR 镜像第一次推送后，默认可能是私有 package。

如果需要公开访问：

```text
GitHub -> 用户头像 -> Your packages
  -> 选择对应 package
  -> Package settings
  -> Change visibility
  -> Public
```

如果是私有 package：

- Jenkins 推送需要 `write:packages`。
- 服务器拉取需要 `read:packages`。
- 执行部署的服务器需要提前 `docker login ghcr.io`。

如果 package 关联了 GitHub 仓库，它可以继承仓库权限，也更容易被 GitHub Actions 或项目相关流程访问。

## Dockerfile 中添加镜像来源标签

建议在 Dockerfile 中添加 OCI label，用于让 GHCR package 更容易关联到仓库：

```dockerfile
LABEL org.opencontainers.image.source="https://github.com/cryptolimber/jenkins-demo"
LABEL org.opencontainers.image.description="Jenkins demo backend service"
```

前端 Dockerfile 可以写：

```dockerfile
LABEL org.opencontainers.image.source="https://github.com/cryptolimber/jenkins-demo"
LABEL org.opencontainers.image.description="Jenkins demo frontend service"
```

这不是运行必须项，但对镜像管理更清晰。

## 常见问题

### 1. `docker login ghcr.io` 失败

检查：

- 用户名是否是 GitHub 用户名。
- token 是否是 classic token。
- token 是否包含 `read:packages` 或 `write:packages`。
- token 是否过期。
- 如果组织启用了 SSO，token 是否授权了 SSO。

### 2. `docker push` 提示权限不足

检查：

- token 是否有 `write:packages`。
- 镜像 namespace 是否正确。
- 当前 GitHub 用户是否有权限向该 namespace 推送 package。
- package 是否已经存在，但没有给当前用户写权限。

### 3. 服务器 `docker compose up -d` 拉取失败

检查：

- 镜像地址是否写成了 `ghcr.io/...`。
- tag 是否存在。
- 私有镜像是否已经在服务器执行过 `docker login ghcr.io`。
- token 是否有 `read:packages`。

### 4. `latest` 为什么不适合回滚

因为 `latest` 会被每次新构建覆盖。

例如：

```text
第 10 次构建 -> latest 指向 10
第 11 次构建 -> latest 指向 11
```

如果只保留 `latest`，就很难明确回滚到第 10 次。

所以推荐同时保留：

```text
:latest
:BUILD_NUMBER
```

回滚时使用明确版本：

```bash
BACKEND_TAG=10 FRONTEND_TAG=10 docker compose up -d
```

## 当前项目推荐用法

对于当前 `jenkins-demo` 项目，推荐最终形成下面的流程：

```text
Jenkins 拉取代码
        |
        v
后端测试 + 前端测试
        |
        v
构建 backend/frontend 镜像
        |
        v
同时打 BUILD_NUMBER 和 latest 两个 tag
        |
        v
推送到 GHCR
        |
        v
服务器通过 docker compose 使用指定 BUILD_NUMBER 启动
```

推荐镜像：

```text
ghcr.io/cryptolimber/jenkins-demo-backend:${BUILD_NUMBER}
ghcr.io/cryptolimber/jenkins-demo-frontend:${BUILD_NUMBER}
```

推荐部署：

```bash
BACKEND_TAG=${BUILD_NUMBER} FRONTEND_TAG=${BUILD_NUMBER} docker compose up -d
```

推荐回滚：

```bash
BACKEND_TAG=上一个稳定版本 FRONTEND_TAG=上一个稳定版本 docker compose up -d
```

## 总结

GHCR 在当前 DevOps 路线中的位置是镜像仓库：

```text
Jenkins 负责构建
GHCR 负责存镜像
Docker Compose / Docker Swarm 负责运行
Portainer 负责可视化管理
```

对于个人开发者，GHCR 的优势是：

- 和 GitHub 账号、仓库天然集成。
- 不需要自己维护 Harbor 或 Docker Registry。
- 支持公开和私有镜像。
- 适合 Jenkins、Docker Compose、Docker Swarm 这条路线。
- 方便后续多服务器统一拉取镜像。
