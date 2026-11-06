# Jenkins CI/CD 学习教程

## 目标

为 **零 CI/CD 经验** 的 Python + FastAPI + React + Tailwind 开发者设计，学完后能在本地（WSL2/Docker）搭建一套完整的 Jenkins CI/CD 流水线。

## 前置要求

| 要求 | 说明 |
|------|------|
| Git 基础 | clone / commit / push / branch |
| Docker 基础 | 会写 Dockerfile、docker-compose，会拉取运行镜像 |
| Python 基础 | 虚拟环境、pip、pytest |
| Node.js 基础 | npm、vite |
| WSL2 环境 | 本教程基于 WSL2 + Docker Desktop |

## 学习路线

```
第 1 步: 理解 CI/CD 概念（30 分钟）
   ↓
第 2 步: 本地安装 Jenkins（30 分钟）
   ↓
第 3 步: 创建 FastAPI + React 示例项目（1 小时）
   ↓
第 4 步: 编写 Jenkins Pipeline（1.5 小时）★ 核心
   ↓
第 5 步: 配置自动化触发 & Webhook（30 分钟）
   ↓
第 6 步: 了解实际项目最佳实践（30 分钟）
```

**总学习时间：约 4-5 小时**

## 教程文件

| 文件 | 内容 |
|------|------|
| [01-cicd-concepts.md](./01-cicd-concepts.md) | CI/CD 核心概念 |
| [02-jenkins-installation.md](./02-jenkins-installation.md) | Jenkins 本地安装与配置 |
| [03-sample-project.md](./03-sample-project.md) | 创建 FastAPI + React 示例项目 |
| [04-jenkins-pipeline.md](./04-jenkins-pipeline.md) | Jenkins Pipeline 实战 |
| [05-automation.md](./05-automation.md) | Webhook 自动化触发 |
| [06-real-world-patterns.md](./06-real-world-patterns.md) | 实际开发最佳实践 |

## 学完后你能做什么

- 在本地运行 Jenkins，创建和管理 Pipeline Job
- 编写 Jenkinsfile 实现代码检出 → 测试 → 构建 → 部署全流程
- Push 代码后自动触发构建和部署
- 理解 CI/CD 在实际团队协作中的价值和最佳实践