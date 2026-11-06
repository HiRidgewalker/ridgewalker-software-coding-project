# 故障排查

前置阅读：[02-local-deployment.md](/home/hiyoungman/CodeProject/PythonProject/learning-vllm-notebook/docs/vllm/02-local-deployment.md)

## 是什么

这篇文档不是泛泛讲排障思路，而是记录当前仓库在 WSL2 + Ubuntu 24.04 + RTX 4060 Laptop GPU 环境下已经实际遇到过的问题和可执行修复方法。

## 工程中何时用

1. `vllm serve` 启动失败
2. `curl` 连不上本地服务
3. 依赖导入报错
4. 服务能起来但请求不通

## 核心 API / 用法

### 1. `ImportError: libcudart.so.12`

现象：

```text
ImportError: libcudart.so.12: cannot open shared object file
```

处理：

1. 在 WSL 中安装 CUDA Toolkit 12.9
2. 配置 `LD_LIBRARY_PATH=/usr/local/cuda-12.9/lib64:$LD_LIBRARY_PATH`

### 2. `huggingface-hub==1.x` 与 `transformers` 冲突

现象：

```text
huggingface-hub>=0.34.0,<1.0 is required ... but found 1.x
```

处理：

```bash
uv pip install --force-reinstall "huggingface_hub>=0.34,<1.0"
```

### 3. `Failed to find C compiler`

现象：

```text
RuntimeError: Failed to find C compiler
```

处理：

```bash
sudo apt-get update
sudo apt-get install -y build-essential gcc g++ make
```

### 4. `fatal error: Python.h: No such file or directory`

现象：

```text
fatal error: Python.h: No such file or directory
```

处理：

```bash
sudo apt-get update
sudo apt-get install -y python3.12-dev python3-dev
```

### 5. `502 Bad Gateway`

现象：

`curl` 访问本地服务时走了代理。

处理：

```bash
curl --noproxy '*' http://127.0.0.1:8000/v1/models
```

或：

```bash
unset http_proxy https_proxy HTTP_PROXY HTTPS_PROXY all_proxy ALL_PROXY
```

### 6. `Connection refused`

现象：

```text
curl: (7) Failed to connect to 127.0.0.1 port 8000
```

处理结论：

1. 不是请求格式问题
2. 而是 `8000` 端口当前没有监听进程
3. 回到服务端终端，确认 `vllm serve` 是否还在运行

### 7. 日志显示服务已启动，但访问仍被拒绝

现象：

1. 日志里已经出现 `Application startup complete.`
2. 但 `curl http://127.0.0.1:8000/health` 仍然报 `Connection refused`

处理：

启动服务时显式添加：

```bash
--host 0.0.0.0
```

完整示例：

```bash
vllm serve models/Qwen/Qwen3.5-2B \
  --host 0.0.0.0 \
  --port 8000 \
  --tensor-parallel-size 1 \
  --language-model-only \
  --max-model-len 4096 \
  --gpu-memory-utilization 0.80 \
  --enforce-eager
```

工程结论：

1. 在当前环境中，单靠默认绑定方式不够稳
2. 显式声明 `--host 0.0.0.0` 是当前仓库推荐做法

## 代码讲解

当前仓库的排障顺序固定如下：

1. 先确认系统依赖
2. 再确认 Python 依赖
3. 再确认模型能否离线加载
4. 再确认服务是否真的监听 `8000`
5. 最后才检查请求体格式

这个顺序能避免在错误层级上浪费时间。

## 运行结果说明

判断服务真的可用，只看三条：

1. `vllm serve ...` 进程不退出
2. `curl --noproxy '*' http://127.0.0.1:8000/health -v` 返回 `200 OK`
3. `curl --noproxy '*' http://127.0.0.1:8000/v1/models -v` 返回 JSON

## 工程最佳实践

✅ 推荐：先看错误最后一行，再做针对性修复  
✅ 推荐：先确认端口监听，再确认请求内容  
✅ 推荐：本地服务调试统一绕过代理  
❌ 避免：一出错就同时重装一堆依赖  
❌ 避免：服务未监听时反复改 `curl` 请求体  

## 与其他特性的关联

1. 这篇文档和 [02-local-deployment.md](/home/hiyoungman/CodeProject/PythonProject/learning-vllm-notebook/docs/vllm/02-local-deployment.md) 配合使用
2. 请求示例见 [09-curl-and-jq.md](/home/hiyoungman/CodeProject/PythonProject/learning-vllm-notebook/docs/vllm/09-curl-and-jq.md)
