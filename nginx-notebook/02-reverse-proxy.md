# Nginx 反向代理

## 2.1 什么是反向代理？

```
客户端 → Nginx (反向代理) → 后端服务器
         (对外可见)          (对外隐藏)
```

| | 正向代理 | 反向代理 |
|------|---------|---------|
| 谁在用 | 客户端（如公司内网代理上网） | 服务端（为后端服务提供统一入口） |
| 隐藏谁 | 隐藏客户端 | 隐藏服务端 |
| 典型场景 | 翻墙、公司内网 | 负载均衡、SSL 终结、API 网关 |

**反向代理的核心价值**：后端只需要关心业务逻辑，Nginx 负责接收请求、SSL、限流、缓存等横切关注点。

## 2.2 `proxy_pass` — 反向代理的核心指令

### 基本用法

```nginx
server {
    listen 80;
    server_name api.example.com;

    location / {
        proxy_pass http://127.0.0.1:8000;
    }
}
```

效果：请求 `http://api.example.com/items` → Nginx 转发给 `http://127.0.0.1:8000/items`

### 路径拼接规则（重要，容易踩坑）

```nginx
# 规则：proxy_pass 末尾有 / = 截断匹配路径，没有 / = 拼接完整路径

# 场景一：proxy_pass 不带 /
location /api/ {
    proxy_pass http://backend:8000;
}
# 请求 /api/items → 转发到 http://backend:8000/api/items

# 场景二：proxy_pass 带 /
location /api/ {
    proxy_pass http://backend:8000/;
}
# 请求 /api/items → 转发到 http://backend:8000/items（注意 /api 被截断了）

# 场景三：带子路径
location /api/ {
    proxy_pass http://backend:8000/v2/;
}
# 请求 /api/items → 转发到 http://backend:8000/v2/items
```

**记住**：带 `/` = 替换，不带 `/` = 追加。

## 2.3 传递客户端真实信息

默认情况下，后端只能看到 Nginx 的 IP，不知道真实客户端是谁：

```nginx
location /api/ {
    proxy_pass http://backend:8000;

    # 传递客户端真实 IP
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;    # http 还是 https
    proxy_set_header X-Forwarded-Host $host;
}
```

### 各 Header 的含义

| Header | 含义 | 示例值 |
|--------|------|--------|
| `Host` | 原始请求的域名 | `api.example.com` |
| `X-Real-IP` | 客户端真实 IP | `1.2.3.4` |
| `X-Forwarded-For` | 代理链（经过的每个代理追加 IP）| `1.2.3.4, 10.0.0.1` |
| `X-Forwarded-Proto` | 原始协议（http/https）| `https` |

### 后端如何读取真实 IP（以 FastAPI 为例）

```python
from fastapi import FastAPI, Request

app = FastAPI()

@app.get("/api/whoami")
def whoami(request: Request):
    return {
        "client_ip": request.headers.get("x-real-ip"),
        "forwarded_for": request.headers.get("x-forwarded-for"),
        "proto": request.headers.get("x-forwarded-proto"),
    }
```

## 2.4 超时配置

```nginx
location /api/ {
    proxy_pass http://backend:8000;

    # 连接后端超时（默认 60s）
    proxy_connect_timeout 10s;

    # 向后端发送请求的超时（默认 60s）
    proxy_send_timeout 30s;

    # 等待后端响应的超时（默认 60s）
    proxy_read_timeout 60s;
}
```

### 各超时适用场景

| 参数 | 什么情况下调大 |
|------|---------------|
| `proxy_connect_timeout` | 后端启动慢 |
| `proxy_send_timeout` | 上传大文件 |
| `proxy_read_timeout` | 后端处理慢、长轮询、SSE、大文件下载 |

### 长连接场景（SSE/Streaming）

```nginx
location /api/stream/ {
    proxy_pass http://backend:8000;

    proxy_read_timeout 3600s;          # 1 小时超时
    proxy_buffering off;               # 关闭缓冲，实时输出
    proxy_cache off;                   # 不缓存流式响应

    # SSE 需要的 Header
    proxy_set_header Connection '';
    proxy_http_version 1.1;            # HTTP/1.1 支持长连接
    chunked_transfer_encoding off;
}
```

## 2.5 Buffering（缓冲）

Nginx 默认会缓冲后端的响应，收完再发给客户端：

```nginx
location /api/ {
    proxy_pass http://backend:8000;

    # 默认开启缓冲（适合大多数场景）
    proxy_buffering on;                # 默认值
    # proxy_buffer_size 4k;           # 响应头缓冲区大小
    # proxy_buffers 8 4k;             # 响应体缓冲区（数量 × 大小）

    # 关闭缓冲（适合实时响应、大文件下载）
    # proxy_buffering off;
}
```

| 场景 | 建议 |
|------|------|
| 普通 API 响应 | 保持默认 on |
| SSE/WebSocket | 关闭 buffering |
| 大文件下载 | 关闭 buffering，配合 `proxy_max_temp_file_size` |

## 2.6 WebSocket 代理

```nginx
location /ws/ {
    proxy_pass http://backend:8000;
    proxy_http_version 1.1;             # WebSocket 需要 HTTP/1.1

    # WebSocket 必需的 Header
    proxy_set_header Upgrade $http_upgrade;
    proxy_set_header Connection "upgrade";

    # 长连接
    proxy_read_timeout 3600s;
    proxy_send_timeout 3600s;
}
```

## 2.7 完整反向代理配置模板

```nginx
# /etc/nginx/sites-available/api

upstream backend {
    server 127.0.0.1:8000;
    keepalive 32;    # 保持到后端的连接池
}

server {
    listen 80;
    server_name api.example.com;

    # 客户端请求体最大大小（上传文件）
    client_max_body_size 100M;

    access_log /var/log/nginx/api_access.log;
    error_log /var/log/nginx/api_error.log;

    location /api/ {
        proxy_pass http://backend;
        proxy_http_version 1.1;

        # 客户端信息
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;

        # 连接池
        proxy_set_header Connection "";

        # 超时
        proxy_connect_timeout 10s;
        proxy_send_timeout 30s;
        proxy_read_timeout 60s;

        # 不缓冲上传的文件（直接透传）
        proxy_request_buffering off;
    }
}
```

---

**下一步**：[03-load-balancing.md](./03-load-balancing.md) — 负载均衡配置