# Asyncio Study Project

这是一套围绕 Python 3.11+ `asyncio` 的复习材料，目标不是背 API，而是建立一套能独立写异步程序的运行模型。

## 学习顺序
1. 先读 [notes/asyncio-review.md](/Users/limber/Desktop/CodeHub/PythonProject/study-asyncio-project/notes/asyncio-review.md)
2. 再按顺序运行 `examples/` 里的示例
3. 每个示例先猜输出和耗时，再执行验证

## 运行方式
先激活虚拟环境：

```bash
source .venv/bin/activate
```

然后运行单个示例：

```bash
python examples/01_event_loop_entry.py
python examples/02_sequential_vs_concurrent.py
python examples/03_fake_async_blocking.py
python examples/04_taskgroup_timeout_cancel.py
python examples/05_cpu_bound_offload.py
```

## 你应该重点获得什么
- 知道脱离 FastAPI 后如何运行异步代码
- 知道什么情况下 `async`/`await` 有收益
- 能识别“看起来异步，其实仍然阻塞”的写法
- 能用 `TaskGroup`、超时、取消来组织任务
- 知道 CPU 密集工作不该直接丢给事件循环
