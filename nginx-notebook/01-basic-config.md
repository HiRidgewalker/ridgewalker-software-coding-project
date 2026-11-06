# Nginx 基础配置

## 1.1 安装与目录结构

```bash
# Ubuntu/Debian
sudo apt install nginx

# 常用命令
sudo systemctl start nginx
sudo systemctl stop nginx
sudo systemctl reload nginx   # 热重载配置（不中断服务）
sudo nginx -t                  # 测试配置文件语法是否正确
```

### 关键目录

```
/etc/nginx/
├── nginx.conf              # 主配置文件
├── sites-available/        # 所有可用的站点配置
├── sites-enabled/          # 已启用的站点（软链接到 sites-available）
├── conf.d/                 # 额外的配置片段
└── snippets/               # 可复用的配置片段（如 SSL 参数）
```

## 1.2 最小可用的 nginx.conf

```nginx
# /etc/nginx/nginx.conf

user www-data;                          # worker 进程运行用户
worker_processes auto;                  # worker 数 = CPU 核心数
pid /run/nginx.pid;

events {
    worker_connections 1024;            # 每个 worker 最大并发连接数
    use epoll;                          # Linux 下高效 I/O 模型
}

http {
    include       /etc/nginx/mime.types;
    default_type  application/octet-stream;

    # 日志格式
    log_format main '$remote_addr - $remote_user [$time_local] '
                    '"$request" $status $body_bytes_sent '
                    '"$http_referer" "$http_user_agent"';

    access_log /var/log/nginx/access.log main;
    error_log  /var/log/nginx/error.log warn;

    sendfile on;                        # 零拷贝传输文件
    tcp_nopush on;                      # 合并发送头和数据
    keepalive_timeout 65;               # 长连接超时时间

    include /etc/nginx/conf.d/*.conf;
    include /etc/nginx/sites-enabled/*;
}
```

### 核心参数解析

| 参数 | 作用 | 建议值 |
|------|------|--------|
| `worker_processes auto` | worker 进程数 | auto（自动匹配 CPU 核数）|
| `worker_connections` | 单 worker 最大连接数 | 1024-4096 |
| `sendfile on` | 用内核零拷贝发文件，静态文件性能大幅提升 | on |
| `tcp_nopush on` | 等数据包满了再发，减少网络包数量 | on |
| `keepalive_timeout` | HTTP 长连接保持时间（秒）| 60-75 |

### 最大并发计算

```
最大并发 = worker_processes × worker_connections

4 核 × 1024 = 4096 并发连接

如果是反向代理（每个客户端占用 2 个连接）：
实际并发 = 4096 / 2 = 2048
```

## 1.3 虚拟主机（Server Block）

一个 Nginx 可以托管多个网站，通过 `server_name` 区分：

```nginx
# /etc/nginx/sites-available/example.com

server {
    listen 80;
    server_name example.com www.example.com;

    root /var/www/example.com;          # 网站根目录
    index index.html index.htm;

    # 日志（每个站点单独记录）
    access_log /var/log/nginx/example.com_access.log;
    error_log  /var/log/nginx/example.com_error.log;

    # 匹配 / 路径
    location / {
        try_files $uri $uri/ =404;      # 先找文件，再找目录，都找不到返回 404
    }

    # 匹配 /api/ 路径（通常用于反向代理，见后续章节）
    location /api/ {
        proxy_pass http://localhost:8000;
    }

    # 禁止访问隐藏文件
    location ~ /\. {
        deny all;
    }
}
```

### `try_files` 详解

这是 Nginx 中最重要的指令之一：

```nginx
# 常用于 SPA（React/Vue）应用
location / {
    try_files $uri $uri/ /index.html;
    # 效果：访问 /about → 没这个文件 → 返回 index.html（前端路由接管）
}

# 静态网站
location / {
    try_files $uri $uri/ =404;
    # 效果：访问 /about → 有 about.html 就返回 → 没有返回 404
}
```

**执行顺序**：从左到右依次尝试，最后一个参数是"全都没找到时的行为"。

## 1.4 location 匹配规则

```nginx
# 匹配优先级从高到低：

# 1. 精确匹配（最高优先级）
location = /exact/path { }

# 2. 前缀匹配（带 ^~，匹配后不再检查正则）
location ^~ /images/ { }

# 3. 正则匹配（按出现顺序，~ 区分大小写，~* 不区分）
location ~ \.(jpg|png|gif)$ { }
location ~* \.(pdf|doc)$ { }

# 4. 普通前缀匹配（最低优先级，最长前缀胜出）
location / { }
```

### 实际例子

```nginx
server {
    listen 80;

    # 静态资源直接返回
    location ^~ /static/ {
        root /var/www/app;
        expires 30d;                    # 浏览器缓存 30 天
        add_header Cache-Control "public, immutable";
    }

    # API 代理到后端
    location /api/ {
        proxy_pass http://backend:8000;
    }

    # 前端 SPA
    location / {
        root /var/www/app/dist;
        try_files $uri /index.html;
    }
}
```

## 1.5 Gzip 压缩

配置后，服务器先压缩再返回，减少传输量：

```nginx
http {
    # 开启 Gzip
    gzip on;
    gzip_vary on;                       # 响应头加 Vary: Accept-Encoding

    # 压缩级别（1-9，6 是性价比最高的）
    gzip_comp_level 6;

    # 只压缩这些类型（文本压缩率高，图片/视频本身已压缩，不要再压）
    gzip_types
        text/plain
        text/css
        text/javascript
        application/javascript
        application/json
        application/xml
        image/svg+xml;

    # 小于 1KB 的文件不压缩（压了反而变大）
    gzip_min_length 1024;

    # 代理请求也压缩（适用于反向代理场景）
    gzip_proxied any;
}
```

**压缩效果**：HTML/JSON/JS 文件通常能减少 60%-80% 的体积。

## 1.6 日志配置

### 自定义日志格式

```nginx
http {
    # 详细格式：记录请求耗时、上游响应时间
    log_format detailed '$remote_addr - $remote_user [$time_local] '
                        '"$request" $status $body_bytes_sent '
                        '"$http_referer" "$http_user_agent" '
                        'rt=$request_time uct=$upstream_connect_time '
                        'urt=$upstream_response_time';

    access_log /var/log/nginx/access.log detailed;

    # 不记录静态资源的访问日志
    location /static/ {
        access_log off;
    }
}
```

### 常用日志变量

| 变量 | 含义 |
|------|------|
| `$remote_addr` | 客户端 IP |
| `$time_local` | 本地时间 |
| `$request` | 请求行（如 `GET /api/items HTTP/1.1`）|
| `$status` | 响应状态码 |
| `$body_bytes_sent` | 响应体大小（字节）|
| `$request_time` | 请求处理总时间（秒）|
| `$upstream_response_time` | 上游服务器响应时间（秒）|
| `$http_referer` | 来源页面 |
| `$http_user_agent` | 浏览器标识 |

---

**下一步**：[02-reverse-proxy.md](./02-reverse-proxy.md) — 反向代理配置