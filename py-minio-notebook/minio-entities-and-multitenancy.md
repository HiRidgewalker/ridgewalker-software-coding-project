# MinIO 实体概念与多租户设计笔记

> 基于当前仓库中的 `minio/.env.example` 和 `minio/docker-compose.yml` 整理。

## 1. 当前 Docker Compose MinIO 连接信息

当前示例配置中，MinIO 暴露了两个端口：

| 用途 | 地址 |
| --- | --- |
| S3 API | `http://localhost:9000` |
| Web 控制台 / Object Browser | `http://localhost:9001` |

示例 root 管理员凭证来自 `minio/.env.example`：

```env
MINIO_ROOT_USER=admin
MINIO_ROOT_PASSWORD=your-secure-password-here
```

Python 代码如果在宿主机或本地 notebook 中运行，可以这样连接：

```python
from minio import Minio

client = Minio(
    "localhost:9000",
    access_key="admin",
    secret_key="your-secure-password-here",
    secure=False,
)
```

如果 Python 代码运行在和 MinIO 同一个 Docker Compose 网络里的其他容器中，endpoint 通常使用服务名：

```python
client = Minio(
    "minio:9000",
    access_key="admin",
    secret_key="your-secure-password-here",
    secure=False,
)
```

创建 bucket 示例：

```python
bucket_name = "test-bucket"

if not client.bucket_exists(bucket_name):
    client.make_bucket(bucket_name)
```

注意：仓库中目前只有 `.env.example`，没有实际 `.env`。如果启动容器时修改过密码，应以实际 `.env` 或容器环境变量为准。

## 2. `access_key` 与 `secret_key`

MinIO 兼容 S3 API，所以程序连接时使用的是 `access_key` 和 `secret_key`，而不是传统意义上的 account/password。

### 2.1 Root 超管凭证

对于 root 管理员：

```python
access_key = "admin"                    # MINIO_ROOT_USER
secret_key = "your-secure-password-here" # MINIO_ROOT_PASSWORD
```

这里的 `secret_key` 可以理解为 root 管理员密码。

### 2.2 普通 MinIO 用户

如果通过 `mc` 创建普通用户：

```bash
mc admin user add local tenant-a tenant-a-password
```

那么连接时：

```python
client = Minio(
    "localhost:9000",
    access_key="tenant-a",
    secret_key="tenant-a-password",
    secure=False,
)
```

这里的 `secret_key` 是创建用户时设置的密码。

### 2.3 Service Account / Access Key

更推荐给业务程序使用 service account 或 access key，而不是直接使用 root 密码或用户登录密码。

例如为已有用户创建 access key：

```bash
mc admin accesskey create local/ tenant-a
```

`mc` 会输出一对新的：

```text
Access Key: xxx
Secret Key: yyy
```

业务代码应该使用这对新生成的凭证。

## 3. Web UI 与 `mc`

当前较新的开源版 MinIO Web UI 更偏向 Object Browser，也就是对象和 bucket 浏览管理。很多过去 UI 中的管理能力已经不再作为开源 Web UI 的主要能力提供。

因此，以下管理动作更应该使用 `mc`：

| 管理动作 | 推荐工具 |
| --- | --- |
| 创建用户 | `mc admin user add` |
| 创建 access key | `mc admin accesskey create` |
| 创建 policy | `mc admin policy create` |
| 绑定 policy 到 user/group | `mc admin policy attach` |
| 查看服务配置 | `mc admin config` |
| 管理 bucket/object | Web UI、`mc`、SDK 都可以 |

`mc` 不是 MinIO 服务端实体，而是 MinIO Client 命令行工具。

常见初始化命令：

```bash
mc alias set local http://localhost:9000 admin your-secure-password-here
```

这里的 `local` 是 `mc` 本地配置中的 alias，表示某个 MinIO/S3 服务连接配置。

## 4. 多租户对象存储推荐模型

开源 MinIO 没有 `Tenant` 这个一等服务端实体。多租户通常是业务系统自己的概念，然后映射到 MinIO 的用户、bucket 和 policy。

推荐模型：

```text
Root User(admin)
  -> 创建 User(tenant-a)
  -> 创建 Bucket(tenant-a-bucket)
  -> 创建 Policy(只允许访问 tenant-a-bucket)
  -> 给 User 或 Service Account 绑定 Policy
  -> 租户程序使用自己的 Access Key / Secret Key 访问对象
```

示例权限策略：

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "s3:ListBucket",
        "s3:GetBucketLocation"
      ],
      "Resource": [
        "arn:aws:s3:::tenant-a-bucket"
      ]
    },
    {
      "Effect": "Allow",
      "Action": [
        "s3:GetObject",
        "s3:PutObject",
        "s3:DeleteObject"
      ],
      "Resource": [
        "arn:aws:s3:::tenant-a-bucket/*"
      ]
    }
  ]
}
```

创建租户资源的大致流程：

```bash
mc alias set local http://localhost:9000 admin your-secure-password-here

mc mb local/tenant-a-bucket

mc admin user add local tenant-a tenant-a-password

mc admin policy create local tenant-a-policy tenant-a-policy.json

mc admin policy attach local tenant-a-policy --user tenant-a
```

实际系统中，更建议由后端控制平面统一创建 bucket、user、policy、access key，而不是允许租户直接自由创建 bucket。

## 5. 超管与多租户安全边界

如果多个租户共用同一个 MinIO 部署，root 超管账号理论上可以访问所有租户的 bucket 和 object。

这意味着 MinIO 的 `User + Bucket + Policy` 适合做逻辑多租户：

| 隔离目标 | 是否适合 |
| --- | --- |
| 租户之间不能互相访问对象 | 适合 |
| 业务程序只能访问自己的 bucket | 适合 |
| 平台管理员也不能查看租户对象内容 | 单靠 MinIO IAM 不够 |

如果目标是“平台管理员也不能看租户数据”，需要额外设计：

- 每个租户独立 MinIO 实例或独立集群；
- 租户侧加密，MinIO 只存密文；
- 使用外部 KMS，并确保平台管理员没有解密权限；
- 租户自带密钥，服务端只负责对象存取。

## 6. MinIO 主要实体与概念

### 6.1 数据层

| 概念 | 含义 |
| --- | --- |
| `Bucket` | 存储桶，类似顶层目录 |
| `Object` | 真正存储的数据或文件 |
| `Object Key` | 对象路径名，例如 `images/a.png` |
| `Prefix` | 对象 key 的前缀，类似目录，但不是传统文件夹 |
| `Metadata` | 对象元数据，例如 `Content-Type` |
| `Tag` | 对象标签，可用于分类、生命周期规则等 |
| `Version` | bucket 开启版本控制后，同一个 key 的不同版本 |

### 6.2 身份与权限层

| 概念 | 含义 |
| --- | --- |
| `Root User` | 超管账号，由 `MINIO_ROOT_USER` 和 `MINIO_ROOT_PASSWORD` 配置 |
| `User` | MinIO 内置用户，例如 `tenant-a` |
| `Group` | 用户组，可以统一授权 |
| `Policy` | 权限策略，定义允许或拒绝哪些动作 |
| `Access Key / Secret Key` | S3 API 访问凭证 |
| `Service Account` | 某个用户下面的应用访问凭证 |
| `STS Temporary Credentials` | 临时凭证，常用于更高级的身份集成 |

### 6.3 Bucket 配置层

| 概念 | 含义 |
| --- | --- |
| `Bucket Policy` | bucket 级别访问策略，常用于公开读等场景 |
| `IAM Policy` | 用户或用户组级别权限，更适合多租户隔离 |
| `Lifecycle Rule` | 生命周期规则，例如定期删除对象 |
| `Versioning` | bucket 版本控制 |
| `Object Lock` | 对象锁，防止对象被修改或删除 |
| `Retention` | 数据保留策略 |
| `Quota` | bucket 容量限制 |
| `Replication` | bucket 复制 |
| `Event Notification` | 对象变更事件通知 |

### 6.4 管理与工具层

| 概念 | 含义 |
| --- | --- |
| `Config` | MinIO 服务配置，例如 region、KMS、日志、通知等 |
| `mc` | MinIO Client 命令行工具 |
| `Console / Object Browser` | Web UI，当前开源版主要偏对象浏览 |
| `Alias` | `mc` 本地连接配置，不是服务端实体 |
| `SDK` | Python、Java、Go 等程序访问 MinIO 的客户端库 |

## 7. 对当前学习阶段最重要的概念

如果目标是基于 MinIO 做一个多租户对象存储系统，优先掌握这些概念：

```text
Root User
User
Service Account / Access Key
Policy
Bucket
Object
Object Key / Prefix
```

最核心的关系：

```text
User 或 Service Account
  -> 绑定 Policy
  -> Policy 允许访问指定 Bucket
  -> Bucket 中保存 Object
  -> Object 通过 Object Key 定位
```
