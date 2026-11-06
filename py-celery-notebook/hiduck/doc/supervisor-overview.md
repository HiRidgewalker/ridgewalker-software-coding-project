# Supervisor、supervisord 与 supervisorctl

`Supervisor` 是一个用于管理后台进程的工具套件，而 `supervisord` 是其中的核心守护进程。

它们的关系如下：

- **Supervisor**：整个进程管理系统的名称。
- **supervisord**：服务端守护进程，负责启动、停止、重启并监控其他进程。
- **supervisorctl**：命令行客户端，用于向 `supervisord` 发送管理指令。
- **supervisord.conf**：Supervisor 通常使用的配置文件。

常用命令示例：

```bash
# 启动 Supervisor 守护进程
supervisord -c /etc/supervisor/supervisord.conf

# 查看被管理进程的状态
supervisorctl status

# 重启某个进程
supervisorctl restart celery-worker
```

`supervisod` 通常是 `supervisord` 的拼写错误。`supervisord` 末尾的 `d` 表示 **daemon（守护进程）**。
