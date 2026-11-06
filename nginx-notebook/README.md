# Nginx 常用配置详解

## 目录

| 文件 | 内容 |
|------|------|
| [01-basic-config.md](./01-basic-config.md) | 基础配置：核心参数、虚拟主机、日志、Gzip |
| [02-reverse-proxy.md](./02-reverse-proxy.md) | 反向代理：proxy_pass、Header 处理、超时配置 |
| [03-load-balancing.md](./03-load-balancing.md) | 负载均衡：算法、健康检查、会话保持 |
| [04-https-tls.md](./04-https-tls.md) | HTTPS/TLS：证书配置、HTTP/2、HSTS |
| [05-caching.md](./05-caching.md) | 缓存：静态资源缓存、代理缓存、FastCGI 缓存 |

## 前置知识

- 了解 HTTP 协议基本概念（请求/响应、状态码、Header）
- 有 Linux 命令行基础
- 建议在实际机器上跟着操作