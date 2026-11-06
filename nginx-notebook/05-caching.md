# Nginx 缓存

Nginx 缓存分为三个层面：

```
1. 浏览器缓存 → 告诉浏览器"这个文件你可以存多久"
2. 代理缓存   → Nginx 把后端响应存起来，下次直接返回
3. FastCGI 缓存 → 缓存 PHP/Python 应用的动态页面
```

## 5.1 浏览器缓存（静态资源）

### 基本原理

通过响应头告诉浏览器哪些资源可以缓存、缓存多久：

```
首次请求:  浏览器 ──GET /logo.png──→ Nginx ──→ 返回文件 + Cache-Control: max-age=86400
后续请求:  浏览器 ──直接从本地缓存读取──→ 瞬间返回（0ms）
```

### 配置

```nginx
server {
    listen 80;

    location /static/ {
        root /var/www/app;

        # 缓存 30 天
        expires 30d;

        # 更精细的控制
        add_header Cache-Control "public, max-age=2592000, immutable";
    }

    # 按文件类型设置不同的缓存时间
    location ~* \.(jpg|jpeg|png|gif|ico|svg)$ {
        expires 1y;                                      # 图片缓存 1 年
        add_header Cache-Control "public, immutable";
    }

    location ~* \.(css|js)$ {
        expires 7d;                                      # CSS/JS 缓存 7 天
        add_header Cache-Control "public";
    }

    location ~* \.(html)$ {
        expires -1;                                      # HTML 不缓存
        add_header Cache-Control "no-cache, must-revalidate";
    }
}
```

### Cache-Control 指令速查

| 指令 | 含义 |
|------|------|
| `public` | 可被浏览器和中间代理缓存 |
| `private` | 只能被浏览器缓存 |
| `max-age=3600` | 缓存 3600 秒后过期 |
| `immutable` | 资源内容永不改变（可直接用缓存，不发验证请求）|
| `no-cache` | 可以用缓存，但必须先向服务器验证 |
| `no-store` | 完全不缓存 |
| `must-revalidate` | 过期后必须向服务器验证 |

### 最佳实践：文件名 Hash + 永久缓存

前端构建工具（Vite/Webpack）会给文件加 hash：

```
build/
├── index.html                       ← 不缓存
├── assets/index-a3f8b2c.js         ← 永久缓存（内容变了 hash 就变）
└── assets/style-d9e1a4f.css        ← 永久缓存
```

```nginx
location / {
    try_files $uri /index.html;
}

location /assets/ {
    expires 1y;
    add_header Cache-Control "public, immutable";
}
```

文件名 hash 保证了"内容变 → URL 变 → 新请求不会命中旧缓存"，这是最佳的前端缓存策略。

## 5.2 代理缓存（Proxy Cache）

Nginx 作为反向代理时，可以把后端的响应缓存起来：

```
请求 /api/hot-items
    │
    ▼
Nginx → 缓存里有没有？
    ├─ 有 → 直接返回（不惊动后端）
    └─ 没有 → 代理到后端 → 把响应存缓存 → 返回
```

### 配置

```nginx
http {
    # ========== 定义缓存区 ==========
    # levels: 缓存文件目录层级
    # keys_zone: 缓存区名称:内存大小（存 key 和元数据）
    # max_size: 磁盘最大占用
    # inactive: 多久没访问就删除
    proxy_cache_path /var/cache/nginx/proxy
                     levels=1:2
                     keys_zone=my_cache:10m
                     max_size=10g
                     inactive=60m
                     use_temp_path=off;

    server {
        listen 80;

        location /api/ {
            proxy_pass http://backend;

            # 启用缓存
            proxy_cache my_cache;

            # 缓存的条件：只看 GET 和 HEAD，200 和 302 缓存 10 分钟
            proxy_cache_valid 200 302 10m;
            proxy_cache_valid 404      1m;    # 404 也缓存，但只缓存 1 分钟

            # 缓存的 key（不同 URL 不同缓存条目）
            proxy_cache_key "$scheme$request_method$host$request_uri";

            # 哪些请求不缓存
            proxy_no_cache $http_pragma $http_authorization;
            proxy_cache_bypass $http_pragma $http_authorization;

            # 返回缓存命中状态（方便调试）
            add_header X-Cache-Status $upstream_cache_status;
        }
    }
}
```

### `X-Cache-Status` 响应头含义

| 值 | 含义 |
|------|------|
| `MISS` | 缓存没有，请求了后端 |
| `HIT` | 缓存命中，直接返回 |
| `EXPIRED` | 缓存过期，请求后端验证后返回 |
| `STALE` | 后端挂了，返回过期缓存（救命）|
| `UPDATING` | 缓存过期，正在更新，先返回旧缓存 |
| `REVALIDATED` | 用 `If-Modified-Since` 验证，后端返回 304 |
| `BYPASS` | 主动跳过缓存（如 Authorization 请求）|

### 缓存的精细化控制

```nginx
location /api/ {
    proxy_pass http://backend;
    proxy_cache my_cache;

    # 按响应时间分级缓存
    proxy_cache_valid 200 1h;          # 正常响应缓存 1 小时
    proxy_cache_valid 302 10m;         # 重定向缓存 10 分钟
    proxy_cache_valid 404 1m;          # 404 缓存 1 分钟
    proxy_cache_valid any 1m;          # 其他状态码缓存 1 分钟

    # 后端返回这些 Header 时，按后端的指示缓存
    # proxy_cache_valid 会覆盖后端的 Cache-Control（除非开启下面）
    # proxy_cache_revalidate on;

    # 忽略后端响应中的 Set-Cookie（带 cookie 的不缓存）
    proxy_ignore_headers Set-Cookie;

    # 缓存锁定：同一资源并发请求只发 1 次给后端
    proxy_cache_lock on;
    proxy_cache_lock_age 5s;           # 最多等 5 秒
    proxy_cache_lock_timeout 3s;       # 超过 3 秒直接发请求

    # 后端挂了也用过期缓存（宁可给旧数据也不要 502）
    proxy_cache_use_stale error timeout updating http_500 http_502 http_503;

    # 不缓存大于 10MB 的响应
    proxy_max_temp_file_size 10m;
}
```

### `proxy_cache_lock` — 缓存击穿保护

热门资源缓存过期时，可能有 100 个请求同时到达：

```
没有 lock：100 个请求 → 100 次后端调用（击穿）
有 lock：   100 个请求 → 第 1 个去后端，其余 99 个等待 → 共享同一结果
```

## 5.3 FastCGI 缓存

如果有 PHP 应用（WordPress）或 Python（通过 uWSGI），可以用 FastCGI 缓存动态页面：

```nginx
http {
    # 定义 FastCGI 缓存区
    fastcgi_cache_path /var/cache/nginx/fastcgi
                       levels=1:2
                       keys_zone=fcgi_cache:10m
                       max_size=1g
                       inactive=60m;

    server {
        location ~ \.php$ {
            fastcgi_pass unix:/var/run/php/php8.1-fpm.sock;
            fastcgi_cache fcgi_cache;

            # 缓存 200 响应 10 分钟
            fastcgi_cache_valid 200 10m;

            # 缓存 key 包含请求方法和 URI
            fastcgi_cache_key "$scheme$request_method$host$request_uri";

            # 跳过登录用户的缓存
            fastcgi_no_cache $http_cookie;
            fastcgi_cache_bypass $http_cookie;

            add_header X-FastCGI-Cache $upstream_cache_status;
        }
    }
}
```

## 5.4 缓存清理

Nginx 开源版不提供主动清理缓存的 API。解决方案：

### 方式一：根据条件自动过期

```nginx
proxy_cache_valid 200 10m;   # 10 分钟后自动过期
```

### 方式二：手动删除缓存文件

```bash
# 找到并删除特定 URL 的缓存文件
grep -r "GET/api/hot-items" /var/cache/nginx/proxy/
rm /var/cache/nginx/proxy/xxx/yyy/zzz
```

### 方式三：使用 ngx_cache_purge 模块（需编译）

```nginx
location ~ /purge(/.*) {
    allow 127.0.0.1;
    deny all;
    proxy_cache_purge my_cache "$scheme$request_method$host$1";
}
# DELETE /purge/api/hot-items → 清理对应缓存
```

### 方式四：业务层主动失效（推荐）

后端数据更新时，改变 URL 或让前端带上版本号查询参数：

```
GET /api/items?v=123    ← 版本变了，缓存自然失效
```

## 5.5 缓存策略总结

| 资源类型 | 策略 | 配置 |
|---------|------|------|
| 带 hash 的静态文件 | 永久缓存 | `expires 1y; immutable` |
| HTML 文件 | 不缓存 | `expires -1; no-cache` |
| API 热数据 | 代理缓存 5-10 分钟 | `proxy_cache_valid 200 10m` |
| API 用户数据 | 不缓存 | `proxy_cache_bypass` |
| 图片/视频 | 长缓存 | `expires 30d` |
| 404/错误页 | 短缓存 | `proxy_cache_valid 404 1m` |

### 一个综合示例

```nginx
http {
    proxy_cache_path /var/cache/nginx levels=1:2
                     keys_zone=api_cache:100m max_size=10g inactive=30m;

    upstream backend {
        server 127.0.0.1:8000;
    }

    server {
        listen 80;

        # 静态资源：浏览器缓存
        location /assets/ {
            root /var/www/app;
            expires 1y;
            add_header Cache-Control "public, immutable";
        }

        # HTML：不缓存
        location / {
            root /var/www/app;
            try_files $uri /index.html;
            expires -1;
            add_header Cache-Control "no-cache";
        }

        # 公共 API（热门列表等）：服务端缓存 5 分钟
        location /api/public/ {
            proxy_pass http://backend;
            proxy_cache api_cache;
            proxy_cache_valid 200 5m;
            proxy_cache_key "$request_uri";
            add_header X-Cache-Status $upstream_cache_status;
        }

        # 用户 API（个人数据）：不缓存
        location /api/user/ {
            proxy_pass http://backend;
            proxy_no_cache 1;
            proxy_cache_bypass 1;
        }
    }
}
```

---

## 回到目录

[README.md](./README.md) — Nginx 配置详解总览