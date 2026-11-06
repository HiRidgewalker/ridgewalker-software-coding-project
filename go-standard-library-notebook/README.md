# Go 标准库学习项目

这是一个 Go 语言标准库的学习项目，通过示例代码讲解 Go 标准库中常用包的使用方法。

## 项目结构

| 章节 | 内容 |
|------|------|
| `01_fmt_standard_library` | fmt 包：格式化输入输出 |
| `02_os_standard_library` | os 包：操作系统功能 |
| `03_time_standard_library` | time 包：时间处理 |
| `04_log_standard_library` | log 包：日志记录 |
| `05_errors_standard_library` | errors 包：错误处理 |
| `06_bytes_standard_library` | bytes 包：字节操作 |
| `07_io_standard_library` | io 包：输入输出抽象 |
| `08_ioutil_standard_library` | ioutil 包：IO 工具函数 |
| `11_sort_standard_library` | sort 包：排序算法 |
| `13_go_redis_standard_library` | Redis 客户端集成 |

## 主要内容

- **fmt**：格式化打印、Scan 扫描输入
- **os**：文件操作、环境变量、系统信息
- **time**：时间获取、格式化、计时器、定时器
- **log**：日志输出、Panic/Fatal 日志
- **errors**：错误创建与处理
- **bytes/strings**：字节和字符串操作
- **io**：Reader/Writer 接口、文件 IO
- **ioutil**：读取写入工具函数
- **sort**：排序接口、切片排序
- **redis**：Go-Redis 客户端使用

## 运行示例

```bash
cd 01_fmt_standard_library
go run 02_fmt_quickstart.go
```

## 前提条件

- Go 1.22+
