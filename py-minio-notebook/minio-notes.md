# MinIO 学习笔记

> 整理时间：2026-07-15

---

## 1. MinIO 是什么

- **MinIO** 是一个高性能、开源的对象存储服务器，完全兼容 Amazon S3 API。
- 采用 Go 编写，单二进制文件，轻量易部署。
- 支持单机/分布式部署，提供 Kubernetes Operator，云原生友好。
- 典型场景：私有云存储、数据湖底座、开发测试本地 S3 模拟、AI/ML 训练数据访问。

---

## 2. S3 与阿里云 OSS / 腾讯云 COS 的关系

- **Amazon S3** 是对象存储的鼻祖，2006 年推出。
- S3 定义了对象存储的核心概念：Bucket（存储桶）、Object（对象）、Key（键）、Metadata（元数据）。
- S3 API 已成为**事实标准**。
- **阿里云 OSS**、**腾讯云 COS**、**MinIO**、**华为云 OBS** 等都是 **S3-like（类 S3）** 对象存储，兼容 S3 API。
- 用 AWS SDK（如 boto3）只需切换 `endpoint_url` 和密钥，即可对接不同厂商。

> **一句话**：S3 是对象存储的"普通话"，各家云厂商都在说这门语言。

---

## 3. 容器化部署 MinIO

### 3.1 最简 Docker 命令

```bash
docker run -d \
  --name minio \
  -p 9000:9000 \
  -p 9001:9001 \
  -e MINIO_ROOT_USER=admin \
  -e MINIO_ROOT_PASSWORD=your-strong-password \
  -v /your/host/data:/data \
  minio/minio server /data --console-address ":9001"
```

### 3.2 参数说明

| 参数 | 作用 |
|------|------|
| `-p 9000:9000` | S3 API 端口（程序调用） |
| `-p 9001:9001` | Web 控制台端口（浏览器管理） |
| `-e MINIO_ROOT_USER` | 管理员账号（≥3 字符） |
| `-e MINIO_ROOT_PASSWORD` | 管理员密码（≥8 字符） |
| `-v /宿主机路径:/data` | **数据持久化挂载**，容器删除数据不丢 |

### 3.3 Docker Compose（推荐）

```yaml
version: '3.8'

services:
  minio:
    image: minio/minio:latest
    container_name: minio
    restart: unless-stopped
    ports:
      - "9000:9000"
      - "9001:9001"
    environment:
      MINIO_ROOT_USER: admin
      MINIO_ROOT_PASSWORD: your-secure-password-here
    volumes:
      - /your/host/data:/data
    command: server /data --console-address ":9001"
```

启动：`docker compose up -d`

---

## 4. 凭证体系：两套 Token 的区别

| 凭证 | 设置时机 | 用途 | 类比 |
|------|---------|------|------|
| **MINIO_ROOT_USER / MINIO_ROOT_PASSWORD** | **容器启动时**通过环境变量设置 | 人类登录 Web 控制台、系统管理 | Linux root 账号 |
| **Access Key / Secret Key** | **运行后**在 Web 控制台或 `mc` CLI 创建 | 应用程序调用 S3 API | 应用程序 API Token |

### 4.1 创建 Access Key

**方式一：Web 控制台**
1. 访问 `http://localhost:9001`
2. 左侧菜单 → **Access Keys** → **Create Access Key**

**方式二：mc 命令行**
```bash
mc alias set local http://localhost:9000 admin password
mc admin user svcacct add local admin \
  --access-key "myapp-key" \
  --secret-key "myapp-secret"
```

### 4.2 程序代码中使用

```python
from minio import Minio

client = Minio(
    "localhost:9000",
    access_key="3T3xAMPLEkEY",      # ← Access Key
    secret_key="z4mP1eSeCr3tK3y",   # ← Secret Key
    secure=False
)
```

### 4.3 最佳实践

1. **不要把 Root 凭证直接写在程序代码里** —— 创建专用的 Access Key。
2. **为不同应用创建不同的 Access Key** —— 便于权限隔离和轮换。
3. **Access Key 可绑定 Policy（策略）** —— 限制只能访问特定 Bucket 或操作（只读、只写等）。
4. **Secret Key 只在创建时显示一次** —— 务必妥善保存。

---

## 5. 核心总结

- MinIO = 开源 + S3 兼容 + 轻量高性能。
- 容器部署核心是：**端口映射 + 数据卷挂载 + Root 环境变量**。
- 人用 **Root User/Password** 登录控制台；程序用 **Access Key/Secret Key** 调 API。
