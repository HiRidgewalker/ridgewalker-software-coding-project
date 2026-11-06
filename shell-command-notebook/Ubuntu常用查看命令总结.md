# Ubuntu 常用查看命令总结

## 内存

- `free -h` — 查看内存使用情况，重点关注 `available`（可用内存）

## CPU / 进程

- `top` / `htop` — 实时查看进程资源占用（htop 更好用，需 `sudo apt install htop`）
  - htop 快捷键：F6 排序、F9 结束进程、q 退出

## 按资源占用排序进程

- `ps aux --sort=-%mem | head -20` — 按内存占用排序
- `ps aux --sort=-%cpu | head -20` — 按 CPU 占用排序
- `ps aux | grep <关键词>` — 搜索特定进程（如 node、python、vscode）

## 硬盘容量

- `df -h` — 查看磁盘分区使用情况，`df -h /` 只看根目录
- `du -sh .` — 查看当前目录占用
- `du -h --max-depth=1 | sort -hr` — 查看当前目录下各文件夹大小并排序

## 磁盘 IO

- `iostat -xz 1` — 实时监控磁盘 IO（需 `sudo apt install sysstat`）

## 系统负载

- `uptime` — 查看系统负载均值（load average），数值超过 CPU 核心数说明压力偏高

## 进程树

- `pstree -p` / `ps -ef --forest` — 查看进程父子关系（需 `sudo apt install psmisc`）

## 端口占用

- `ss -tunlp` — 查看端口占用情况
- `ss -tunlp | grep <端口号>` — 查看特定端口

## 日常最常用的几条

```bash
free -h                              # 内存
df -h                                # 磁盘
top                                  # 实时进程
ps aux --sort=-%mem | head -20       # 内存占用 Top20
ps aux --sort=-%cpu | head -20       # CPU 占用 Top20
du -h --max-depth=1 | sort -hr       # 目录大小排序
```

> 快速判断系统是否扛不住：看 `free -h`、`top`、`df -h /` 这三条即可。
