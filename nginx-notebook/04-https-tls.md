# Nginx HTTPS/TLS 配置

## 4.1 为什么需要 HTTPS？

- 加密传输：中间人看不到请求内容
- 身份验证：确认你访问的是真正的服务器
- 数据完整性：防止内容被篡改
- SEO：Google 优先收录 HTTPS 站点
- HTTP/2：浏览器只支持 HTTPS 下的 HTTP/2

## 4.2 获取 SSL 证书

### 方式一：Let's Encrypt（免费，推荐）

```bash
# 安装 certbot
sudo apt install certbot python3-certbot-nginx

# 自动获取并配置证书（certbot 会自动修改 nginx 配置）
sudo certbot --nginx -d example.com -d www.example.com

# 证书自动续期（certbot 会自动添加 cron/systemd timer）
sudo certbot renew --dry-run   # 测试续期是否正常
```

### 方式二：自签名证书（本地开发/测试用）

```bash
# 生成自签名证书（有效期 365 天）
openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
  -keyout /etc/nginx/ssl/selfsigned.key \
  -out /etc/nginx/ssl/selfsigned.crt \
  -subj "/CN=localhost"
```

> 自签名证书浏览器会报不安全警告，仅用于本地测试和学习。

### 方式三：购买商业证书

从 DigiCert、GeoTrust 等 CA 购买，适合对安全有高要求的企业场景。

## 4.3 基础 HTTPS 配置

```nginx
# /etc/nginx/sites-available/example.com

server {
    # ========== HTTP → HTTPS 重定向 ==========
    listen 80;
    server_name example.com www.example.com;
    return 301 https://$server_name$request_uri;
}

server {
    # ========== HTTPS 主配置 ==========
    listen 443 ssl;
    http2 on;                                   # 启用 HTTP/2
    server_name example.com www.example.com;

    # 证书路径
    ssl_certificate     /etc/letsencrypt/live/example.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/example.com/privkey.pem;

    # ========== SSL 安全配置 ==========

    # 只启用 TLS 1.2 和 1.3（禁用老旧协议）
    ssl_protocols TLSv1.2 TLSv1.3;

    # 加密套件（优先使用现代强加密算法）
    ssl_ciphers 'ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256:'
                'ECDHE-ECDSA-AES256-GCM-SHA384:ECDHE-RSA-AES256-GCM-SHA384:'
                'ECDHE-ECDSA-CHACHA20-POLY1305:ECDHE-RSA-CHACHA20-POLY1305';

    # 优先使用服务端的加密套件顺序（而不是客户端的）
    ssl_prefer_server_ciphers on;

    # ========== 性能优化 ==========

    # SSL 会话缓存（减少重复握手开销）
    ssl_session_cache shared:SSL:10m;           # 10MB 共享缓存
    ssl_session_timeout 1d;                     # 会话复用 1 天

    # OCSP Stapling（减少客户端验证证书的延迟）
    ssl_stapling on;
    ssl_stapling_verify on;
    ssl_trusted_certificate /etc/letsencrypt/live/example.com/chain.pem;
    resolver 8.8.8.8 1.1.1.1 valid=300s;

    # ========== 安全 Header ==========

    # HSTS：告诉浏览器"以后必须用 HTTPS 访问我"
    add_header Strict-Transport-Security "max-age=63072000; includeSubDomains; preload" always;

    root /var/www/example.com;
    index index.html;

    location / {
        try_files $uri $uri/ =404;
    }
}
```

## 4.4 关键配置逐节解析

### SSL 协议版本

```nginx
# ❌ 不安全：允许老旧协议
ssl_protocols TLSv1 TLSv1.1 TLSv1.2;

# ✅ 安全：只允许 TLS 1.2+
ssl_protocols TLSv1.2 TLSv1.3;
```

TLS 1.0/1.1 已被主流浏览器废弃（2020 年起逐步禁用）。

### SSL 会话缓存

```
没有缓存：每次访问都要完整 TLS 握手（慢 ~300ms）
有缓存：复用上一次的会话参数，只需 ~50ms
```

```nginx
ssl_session_cache shared:SSL:10m;  # 共享内存中存约 40,000 个会话
ssl_session_timeout 1d;            # 会话 1 天后过期
```

### OCSP Stapling

正常情况下，浏览器拿到证书后要自己去 CA 验证证书是否被吊销（增加延迟）。OCSP Stapling 让 Nginx 代劳，把验证结果"订"在证书上发给浏览器：

```nginx
ssl_stapling on;
ssl_stapling_verify on;
```

### HSTS（HTTP Strict Transport Security）

```nginx
add_header Strict-Transport-Security "max-age=63072000; includeSubDomains; preload" always;
```

| 参数 | 含义 |
|------|------|
| `max-age=63072000` | 2 年内强制 HTTPS（秒）|
| `includeSubDomains` | 子域名也强制 HTTPS |
| `preload` | 可申请加入浏览器 HSTS 预加载列表 |

> 注意：开启 HSTS 后，浏览器不再尝试 HTTP 请求。**确保 HTTPS 配置无误后再开启**，否则站点可能无法访问。

## 4.5 HTTPS 反向代理（SSL 终结）

这是最常见的 Nginx 用途之一：Nginx 处理 HTTPS，后端用 HTTP：

```
浏览器 --HTTPS--> Nginx --HTTP--> 后端
       加密              明文（内网安全）
```

```nginx
upstream backend {
    server 127.0.0.1:8000;
}

server {
    listen 443 ssl http2;
    server_name api.example.com;

    ssl_certificate     /etc/letsencrypt/live/api.example.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/api.example.com/privkey.pem;

    location / {
        proxy_pass http://backend;
        proxy_set_header X-Forwarded-Proto https;  # 告诉后端"原始请求是 https"
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }
}
```

后端 FastAPI 可以通过 `X-Forwarded-Proto` 知道自己被 HTTPS 代理了，生成正确的 HTTPS 链接。

## 4.6 多站点 HTTPS（SNI）

同一 IP 上托管多个 HTTPS 站点，通过 SNI（Server Name Indication）区分：

```nginx
# Nginx 根据客户端请求的域名自动选择对应证书

server {
    listen 443 ssl;
    server_name site-a.com;
    ssl_certificate     /etc/nginx/ssl/site-a.crt;
    ssl_certificate_key /etc/nginx/ssl/site-a.key;
}

server {
    listen 443 ssl;
    server_name site-b.com;
    ssl_certificate     /etc/nginx/ssl/site-b.crt;
    ssl_certificate_key /etc/nginx/ssl/site-b.key;
}
```

SNI 在 TLS 握手阶段就传递域名，Nginx 据此选择证书。现代浏览器都支持。

## 4.7 安全检测工具

配置完成后用以下工具检测安全等级：

```bash
# SSL Labs（最权威）
# https://www.ssllabs.com/ssltest/analyze.html?d=your-domain.com

# 命令行快速检测
openssl s_client -connect your-domain.com:443 -tls1_2
nmap --script ssl-enum-ciphers -p 443 your-domain.com
```

目标：SSL Labs 评级 **A+** 以上。

## 4.8 完整 HTTPS 配置模板

```nginx
# 可复用 SSL 配置片段：/etc/nginx/snippets/ssl-params.conf
ssl_protocols TLSv1.2 TLSv1.3;
ssl_ciphers 'ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256:'
            'ECDHE-ECDSA-AES256-GCM-SHA384:ECDHE-RSA-AES256-GCM-SHA384:'
            'ECDHE-ECDSA-CHACHA20-POLY1305:ECDHE-RSA-CHACHA20-POLY1305';
ssl_prefer_server_ciphers on;
ssl_session_cache shared:SSL:10m;
ssl_session_timeout 1d;
ssl_session_tickets off;                          # 禁用 session ticket（有安全隐患）
ssl_stapling on;
ssl_stapling_verify on;
resolver 8.8.8.8 1.1.1.1 valid=300s;
add_header Strict-Transport-Security "max-age=63072000; includeSubDomains; preload" always;
add_header X-Frame-Options DENY always;
add_header X-Content-Type-Options nosniff always;

# 使用方式（在主配置中 include）：
# server {
#     listen 443 ssl;
#     include snippets/ssl-params.conf;
#     ssl_certificate     /path/to/cert.pem;
#     ssl_certificate_key /path/to/key.pem;
# }
```

---

**下一步**：[05-caching.md](./05-caching.md) — 缓存配置