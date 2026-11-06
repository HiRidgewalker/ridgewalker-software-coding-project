# 第 1 步：CI/CD 核心概念

## 1.1 没有 CI/CD 时，我们怎么发布代码？

```
开发者 push 代码 → 手动拉取 → 手动安装依赖 → 手动测试 → 手动打包 → 手动部署到服务器
```

**问题**：
- 每次发布都要重复这些步骤，容易出错
- 没人知道这次部署能不能成功，要等上线了才发现问题
- 多人协作时，合并代码经常冲突，没人提前检查

## 1.2 什么是 CI/CD？

### CI — 持续集成（Continuous Integration）

> 频繁地将代码合并到主干，每次合并都自动构建和测试。

**核心动作**：每当有人 push 代码 → 自动拉取 → 自动安装依赖 → 自动跑测试 → 自动做代码检查

**目的**：尽早发现问题，而不是等到发布那天。

### CD — 持续交付 / 持续部署

| 术语 | 含义 | 部署到生产 |
|------|------|-----------|
| 持续交付 | 代码随时处于可发布状态 | **手动**触发 |
| 持续部署 | 通过测试后自动上线 | **自动**触发 |

两者的区别只是最后一步：部署到生产环境是按按钮还是全自动。

### 一张图看清 CI/CD 全流程

```
  Push 代码
     │
     ▼
┌─────────┐
│ 检出代码 │  ← git clone / checkout
└────┬────┘
     ▼
┌─────────┐
│ 安装依赖 │  ← uv sync / npm ci
└────┬────┘
     ▼
┌─────────┐
│ 代码检查 │  ← lint（ruff, eslint）
└────┬────┘
     ▼
┌─────────┐
│ 运行测试 │  ← pytest, vitest   ← CI 到此为止
└────┬────┘
     ▼
┌─────────┐
│ 构建镜像 │  ← docker build
└────┬────┘
     ▼
┌─────────┐
│   部署   │  ← docker compose up  ← CD 部分
└─────────┘
```

## 1.3 Jenkins 是什么？

Jenkins 是一个开源的**自动化服务器**，它做的事情就是：

> 监听代码变更 → 按你写好的流水线一步步执行 → 告诉你结果

### 同类工具对比

| 工具 | 类型 | 适合 |
|------|------|------|
| Jenkins | 自托管，最灵活 | 需要完全控制流水线的团队 |
| GitHub Actions | 托管在 GitHub | 代码在 GitHub 上的项目 |
| GitLab CI | 内置在 GitLab | 代码在 GitLab 上的项目 |
| Drone CI | 轻量，容器原生 | 以容器为中心的团队 |

**为什么学 Jenkins？**
- 它是 CI/CD 领域的"老大哥"，很多公司还在用
- 插件生态最丰富（1800+ 插件）
- 可以部署在任何地方（本地、服务器、Kubernetes）
- 理解了 Jenkins，其他 CI 工具一通百通

## 1.4 Jenkins 核心概念

### Job（任务）

Jenkins 中最小的执行单元。一个 Job 定义了一个具体的自动化任务。

### Pipeline（流水线）

比 Job 更强大，用代码（Jenkinsfile）定义整个 CI/CD 流程。Pipeline 由多个 Stage 组成。

### 核心术语图解

```
┌───────────────  Pipeline（流水线）──────────────────┐
│                                                      │
│  ┌──────── Stage ────────┐  ┌──────── Stage ────────┐│
│  │  Step1    Step2       │  │  Step1    Step2       ││
│  │  (checkout) (install) │  │  (test)   (lint)     ││
│  └───────────────────────┘  └───────────────────────┘│
│                                                      │
│  Node（节点）= 执行这些 Stage 的机器                   │
│  Agent（代理）= 具体跑任务的进程/容器                   │
└──────────────────────────────────────────────────────┘
```

**术语速查**：
- **Node**：运行 Jenkins 的机器（物理机/虚拟机/容器）
- **Agent/Executor**：在 Node 上执行具体任务的代理
- **Stage**：流水线的一个阶段，比如"构建"、"测试"、"部署"
- **Step**：Stage 里的单个操作，比如运行一条 shell 命令
- **Workspace**：Jenkins 检出代码后存放的目录

## 1.5 Declarative Pipeline vs Scripted Pipeline

Jenkins 支持两种 Pipeline 写法：

### Declarative Pipeline（声明式）— 推荐新手使用

```groovy
pipeline {
    agent any                          // 在任何可用的节点上执行
    stages {
        stage('Build') {               // 一个阶段
            steps {
                sh 'echo "building..."' // 具体执行步骤
            }
        }
        stage('Test') {
            steps {
                sh 'echo "testing..."'
            }
        }
    }
}
```

### Scripted Pipeline（脚本式）— 更灵活但复杂

```groovy
node {
    stage('Build') {
        sh 'echo "building..."'
    }
    stage('Test') {
        sh 'echo "testing..."'
    }
}
```

**建议**：本教程全部使用 Declarative Pipeline，语法更清晰，也满足 90% 的场景。

## 1.6 你的第一个 CI/CD 流程长什么样？

以我们的 FastAPI + React 项目为例：

```
push 代码到 GitHub
       │
       ▼
  Jenkins 检测到变更
       │
       ▼
  ┌─ Stage: Checkout ── 拉取最新代码
  │
  ├─ Stage: Lint ────── ruff 检查 Python / eslint 检查前端
  │
  ├─ Stage: Test ────── pytest / vitest 跑测试
  │
  ├─ Stage: Build ───── docker build 后端镜像 + 前端镜像
  │
  └─ Stage: Deploy ──── docker compose up -d 启动服务
```

---

**下一步**：[02-jenkins-installation.md](./02-jenkins-installation.md) — 在本地安装 Jenkins
