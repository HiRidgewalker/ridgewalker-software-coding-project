# 第 5 步：自动化触发 & Webhook

手动点 "Build Now" 太傻了。真正的 CI/CD 应该是 **push 代码 → 自动构建**。

## 5.1 两种触发方式

| 方式 | 原理 | 延迟 | 适用场景 |
|------|------|------|---------|
| **Poll SCM** | Jenkins 定时去检查 Git 仓库有没有新提交 | 有轮询间隔延迟 | 简单，不需要配置 Webhook |
| **Webhook** | GitHub 主动通知 Jenkins "有新代码了" | 几乎实时 | 正式项目 |

## 5.2 方式一：Poll SCM（简单，立即能用）

在 Jenkinsfile 中添加 `triggers` 块：

```groovy
pipeline {
    agent any

    triggers {
        // 每 5 分钟检查一次代码变更（H 是 Jenkins 的哈希，避免所有 Job 同时触发）
        pollSCM('H/5 * * * *')
    }

    stages { ... }
}
```

也可以配置更频繁的检查：

```groovy
pollSCM('* * * * *')  // 每分钟一次
```

**缺点**：有轮询延迟，且增加 Git 服务器负担。

## 5.3 方式二：Webhook（推荐）

### 原理

```
你 push 代码 → GitHub 发送 POST 请求到 Jenkins → Jenkins 触发构建
```

**问题**：你的 Jenkins 在本地 `localhost:8080`，GitHub 无法直接访问。

**解决方案**：用 ngrok 把本地端口暴露到公网。

### Step 1：安装 ngrok

```bash
# 方式一：snap（WSL2 中推荐）
sudo snap install ngrok

# 方式二：直接下载
wget https://bin.equinox.io/c/bNyj1mQVY4c/ngrok-v3-stable-linux-amd64.tgz
tar xzf ngrok-v3-stable-linux-amd64.tgz
sudo mv ngrok /usr/local/bin/
```

注册 ngrok 账号（免费），获取 authtoken：

```bash
ngrok config add-authtoken <你的token>
```

### Step 2：暴露 Jenkins 端口

```bash
ngrok http 8080
```

你会看到类似输出：

```
Forwarding  https://abc123.ngrok-free.app → http://localhost:8080
```

**记住这个 `https://abc123.ngrok-free.app`**，这就是 GitHub 能访问到的 Jenkins 地址。

### Step 3：配置 Jenkins 接收 Webhook

1. **Manage Jenkins → Configure System**
2. 找到 "GitHub" 部分 → "Add GitHub Server"
3. 名称随意，API URL 保持 `https://api.github.com`
4. 保存

### Step 4：在 GitHub 仓库配置 Webhook

1. 打开你的 GitHub 仓库 → **Settings → Webhooks → Add webhook**
2. Payload URL: `https://abc123.ngrok-free.app/github-webhook/`
   - **注意结尾的 `/github-webhook/`**，这是 Jenkins 的 Webhook 接收端点
3. Content type: `application/json`
4. Events: 选 "Just the push event"（push 代码即触发）
5. 点击 "Add webhook"

### Step 5：Pipeline 中添加 Webhook 触发器

更新 Jenkinsfile：

```groovy
pipeline {
    agent any

    triggers {
        // GitHub Webhook 触发（需要 GitHub Integration 插件）
        githubPush()
    }

    stages { ... }
}
```

### Step 6：测试 Webhook

```bash
# 做个小修改
echo "# test" >> README.md
git add README.md
git commit -m "test: trigger webhook"
git push
```

然后打开 Jenkins → 你的 Pipeline → 应该能看到**自动触发的构建**正在运行。

在 GitHub 仓库的 **Settings → Webhooks → Recent Deliveries** 中可以查看 Webhook 是否发送成功（状态码 200 = 成功）。

## 5.4 多分支 Pipeline（进阶）

如果你的项目有多个分支（main、dev、feature），可以为每个分支创建独立的 Pipeline。

### 创建 Multibranch Pipeline

1. **Dashboard → New Item** → 输入名称 → 选择 **Multibranch Pipeline**
2. **Branch Sources** → Git → 填入仓库地址
3. **Build Configuration** → Mode: by Jenkinsfile
4. 保存

Jenkins 会自动扫描仓库中的所有分支，为每个包含 `Jenkinsfile` 的分支创建子 Pipeline。

### 典型的 Git Flow + CI 流程

```
main 分支 push     → 自动构建 + 自动部署（生产）
develop 分支 push  → 自动构建 + 自动部署（测试环境）
feature/* 分支 push → 只构建 + 测试，不部署
```

可以用 Jenkinsfile 中的 `when` 条件实现：

```groovy
stage('Deploy') {
    when {
        branch 'main'  // 只有 main 分支才部署
    }
    steps {
        sh 'docker compose up -d'
    }
}
```

## 5.5 ngrok 的局限与替代方案

ngrok 免费版限制：
- 每次启动 URL 会变（可以固定一个，但免费版有限）
- 有连接时长限制

**正式环境替代方案**：
- 买台云服务器装 Jenkins（推荐学生的话用腾讯云/阿里云轻量服务器）
- 用内网穿透工具如 frp
- 直接用 GitHub Actions（如果不需要 Jenkins 的话）

---

**下一步**：[06-real-world-patterns.md](./06-real-world-patterns.md) — 实际开发最佳实践