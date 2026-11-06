# Nginx 负载均衡

## 3.1 什么是负载均衡？

```
 客户端请求
    │
    ▼
┌─────────────────┐
│     Nginx       │  ← 负载均衡器（入口）
└───────┬─────────┘
        │ 分发请求
   ┌────┼────┐
   ▼    ▼    ▼
┌────┐┌────┐┌────┐
│ S1 ││ S2 ││ S3 │   ← 后端服务器集群
└────┘└────┘└────┘
```

## 3.2 `upstream` 块定义后端集群

```nginx
http {
    upstream backend {
        # 后端服务器列表
        server 192.168.1.10:8000;
        server 192.168.1.11:8000;
        server 192.168.1.12:8000;
    }

    server {
        listen 80;
        location /api/ {
            proxy_pass http://backend;    # 引用 upstream 名称
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
        }
    }
}
```

## 3.3 负载均衡算法

### 3.3.1 轮询（Round Robin）— 默认

每个请求按顺序轮流分配给后端服务器：

```nginx
upstream backend {
    server 10.0.0.1:8000;
    server 10.0.0.2:8000;
    server 10.0.0.3:8000;
}
# 请求1→S1, 请求2→S2, 请求3→S3, 请求4→S1 ...
```

### 3.3.2 加权轮询（Weighted Round Robin）

性能强的服务器多承担流量：

```nginx
upstream backend {
    server 10.0.0.1:8000 weight=3;   # 承担 50% 请求
    server 10.0.0.2:8000 weight=2;   # 承担 33% 请求
    server 10.0.0.3:8000 weight=1;   # 承担 17% 请求
}
# weight 总和 = 6，每 6 个请求中 S1 处理 3 个
```

### 3.3.3 IP 哈希（IP Hash）

同一客户端的请求始终发到同一台服务器（解决 Session 问题）：

```nginx
upstream backend {
    ip_hash;
    server 10.0.0.1:8000;
    server 10.0.0.2:8000;
    server 10.0.0.3:8000;
}
```

**原理**：对客户端 IP 取哈希，确定分配到哪台服务器。

**注意**：如果某台服务器宕机，该 IP 的请求会被重新分配到其他服务器（不影响其他客户端）。

### 3.3.4 最少连接（Least Connections）

请求发给当前活动连接数最少的服务器：

```nginx
upstream backend {
    least_conn;
    server 10.0.0.1:8000;
    server 10.0.0.2:8000;
    server 10.0.0.3:8000;
}
```

**适合场景**：请求处理时间不均匀（有的请求很快，有的很慢）。

### 3.3.5 一致性哈希（Hash）

按自定义 key（如请求路径、Header）分配：

```nginx
upstream backend {
    hash $request_uri consistent;     # 同一 URI 始终到同一服务器
    server 10.0.0.1:8000;
    server 10.0.0.2:8000;
    server 10.0.0.3:8000;
}
```

`consistent` 表示使用一致性哈希环——增减服务器时，只有少部分请求重新分配。

### 算法选择速查

| 算法 | 适用场景 |
|------|---------|
| 轮询（默认）| 服务器性能相同，请求处理时间均匀 |
| 加权轮询 | 服务器性能不同 |
| IP Hash | 需要 Session 粘性（但推荐用 Redis 替代）|
| 最少连接 | 请求处理时间差异大 |
| 一致性哈希 | 需要请求级别的缓存命中（如 CDN）|

## 3.4 健康检查

### 被动健康检查（默认启用）

后端返回错误时，Nginx 自动标记为不可用：

```nginx
upstream backend {
    server 10.0.0.1:8000 max_fails=3 fail_timeout=30s;
    server 10.0.0.2:8000 max_fails=3 fail_timeout=30s;
}
```

| 参数 | 含义 |
|------|------|
| `max_fails=3` | 30 秒内失败 3 次，标记为 down |
| `fail_timeout=30s` | 标记为 down 后，30 秒再尝试 |

### 主动健康检查（需 plus 版或第三方模块）

开源的 nginx 不带主动健康检查。替代方案：

```nginx
upstream backend {
    server 10.0.0.1:8000;
    server 10.0.0.2:8000;
    server 10.0.0.3:8000 down;    # 手动标记下线（维护中）
}
```

### 备用服务器（backup）

```nginx
upstream backend {
    server 10.0.0.1:8000;
    server 10.0.0.2:8000;
    server 10.0.0.3:8000 backup;   # 只有其他服务器都挂了才启用
}
```

## 3.5 会话保持（Session Persistence）

### 方式一：IP Hash（见 3.3.3）

最简单，但客户端 IP 变了就失效（移动网络、代理）。

### 方式二：Cookie 粘性（需要 plus 版或 nginx-sticky-module）

```nginx
upstream backend {
    sticky cookie srv_id expires=1h domain=.example.com path=/;
    server 10.0.0.1:8000;
    server 10.0.0.2:8000;
}
```

Nginx 会在响应中插入 cookie `srv_id`，后续请求根据 cookie 路由到同一台服务器。

### 方式三（推荐）：不用会话保持，用 Redis 存 Session

应用层解决更好：

```python
# FastAPI 中使用 redis 存储 session
from fastapi import FastAPI
from starlette.middleware.sessions import SessionMiddleware

app = FastAPI()
app.add_middleware(SessionMiddleware, secret_key="your-secret")
```

这样无论请求到哪台服务器，Session 都能从 Redis 读出来。

## 3.6 连接池（Keepalive to Backend）

默认情况下，Nginx 到后端每个请求都新建 TCP 连接，开销大：

```nginx
upstream backend {
    server 10.0.0.1:8000;
    server 10.0.0.2:8000;

    keepalive 32;                   # 保持 32 个空闲连接复用
    keepalive_timeout 60s;          # 空闲连接 60 秒后关闭
    keepalive_requests 1000;        # 单连接最多处理 1000 个请求
}

server {
    location /api/ {
        proxy_pass http://backend;
        proxy_http_version 1.1;              # 必须用 1.1
        proxy_set_header Connection "";      # 清空 Connection，让 Nginx 管理
    }
}
```

**效果**：高并发场景下，延迟减少 30%-50%。

## 3.7 灰度发布（流量切分）

利用 `split_clients` 实现按比例分流：

```nginx
# 定义分流比例
split_clients "${remote_addr}${date_local}" $backend_variant {
    10%     canary;      # 10% 流量到灰度环境
    *       stable;      # 剩余到稳定版
}

upstream canary {
    server 10.0.0.1:8001;    # 新版本
}

upstream stable {
    server 10.0.0.1:8000;    # 旧版本
}

server {
    location /api/ {
        proxy_pass http://$backend_variant;
    }
}
```

---

**下一步**：[04-https-tls.md](./04-https-tls.md) — HTTPS/TLS 配置