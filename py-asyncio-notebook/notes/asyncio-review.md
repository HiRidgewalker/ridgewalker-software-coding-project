# Asyncio 复习讲义

## 1. 先建立最重要的运行模型

### 1.1 `async def` 不会自动执行
`async def` 定义的是协程函数。调用它时，不会立刻执行函数体，而是返回一个协程对象。

```python
async def main():
    print("hello")

result = main()
print(result)
```

这段代码只会得到一个协程对象，不会打印 `"hello"`。

### 1.2 真正驱动协程运行的是事件循环
离开 FastAPI 之后，最标准的异步入口是：

```python
import asyncio

async def main():
    ...

if __name__ == "__main__":
    asyncio.run(main())
```

`asyncio.run()` 会：
- 创建事件循环
- 运行顶层协程
- 在结束时清理资源

这就是“脱离框架后如何运行异步代码”的答案。

### 1.3 `await` 的作用不是“变快”，而是“让出控制权”
`await` 的意义是：当前协程暂时挂起，把执行权交还给事件循环，让别的任务先运行，等等待的对象准备好后再回来继续。

所以异步程序的收益来自：
- 当前任务在等 I/O
- 这段等待时间能让别的任务推进

如果没有等待点，或者等待的是阻塞同步代码，异步不会自动变快。

## 2. 协程、任务、并发之间的关系

### 2.1 协程不等于任务
- 协程：`async def` 调用后返回的对象
- 任务：事件循环中被调度执行的协程包装对象，通常由 `asyncio.create_task()` 或 `TaskGroup.create_task()` 创建

任务更接近“已经交给事件循环管理的工作单元”。

### 2.2 顺序 `await` 不是并发

```python
await task_a()
await task_b()
```

这是先等 `task_a()`，再等 `task_b()`。即使它们内部都有 `await`，这里也仍然是顺序组织。

真正的并发组织通常是：

```python
task1 = asyncio.create_task(task_a())
task2 = asyncio.create_task(task_b())
await task1
await task2
```

或者直接用 `TaskGroup`。

### 2.3 为什么 FastAPI 里看起来不用关心这些
因为框架已经帮你做了两件事：
- 它本身运行在事件循环之上
- 它负责安排请求对应的协程何时被调度

离开框架，你就需要自己写顶层入口、自己管理并发结构。

## 3. 什么时候该用 `async` / `await`

### 3.1 应该写成 `async def` 的情况
- 函数内部需要 `await` 异步 I/O
- 这个函数是异步调用链中的一环
- 这个函数需要参与异步任务编排

典型例子：
- 异步 HTTP 请求
- 异步数据库驱动
- 异步消息队列客户端
- 异步文件或流式 I/O

### 3.2 不该为了“看起来高级”而写成 `async def` 的情况
- 纯计算逻辑
- 字符串处理、列表转换、数据校验等纯同步逻辑
- 内部完全没有 `await`，只是机械地把同步代码包进异步函数

这类函数写成 `async def` 往往只有额外复杂度，没有收益。

### 3.3 一个稳定判断法
先问操作本质是什么：
- 如果主要在“等外部资源”，考虑异步
- 如果主要在“占用 CPU 计算”，不要指望异步提速

再问依赖库是否真的支持 asyncio：
- 如果库提供 `await client.get(...)` 这类接口，通常可以
- 如果库只有阻塞同步接口，即使你把它写在 `async def` 里，它还是阻塞

## 4. 异步为什么可能“没有异步效果”

最常见原因有四类：

### 4.1 把阻塞同步代码放进异步函数

```python
async def bad():
    time.sleep(2)
```

这会直接卡住事件循环。

### 4.2 连续 `await` 导致串行执行
你以为在“同时做很多事”，但实际上是在一个个等。

### 4.3 没有真正创建任务
只创建协程对象，不代表事件循环会主动并发执行它们。

### 4.4 工作本质是 CPU 密集
比如大规模计算、压缩、加密、图像处理。这里该考虑：
- `asyncio.to_thread()`
- `loop.run_in_executor()`
- 进程池

## 5. 任务编排：从能跑到能控

### 5.1 `create_task` 适合什么
适合需要并发推进的独立工作。

不适合的情况：
- 只是为了“显得异步”
- 创建后不追踪结果和异常

### 5.2 推荐优先用 `TaskGroup`
Python 3.11+ 中，`TaskGroup` 更适合结构化并发：
- 生命周期更清晰
- 失败传播更一致
- 不容易遗留失控后台任务

### 5.3 取消和超时是常态，不是边角功能
异步程序经常面对：
- 请求超时
- 上游取消
- 程序退出
- 批处理部分失败

所以要习惯：
- `asyncio.timeout()`
- `task.cancel()`
- `try/finally`
- 理解 `CancelledError`

## 6. 你后续写异步程序时的默认模板

```python
import asyncio

async def main():
    async with asyncio.TaskGroup() as tg:
        tg.create_task(...)
        tg.create_task(...)

if __name__ == "__main__":
    asyncio.run(main())
```

然后再逐步往里补：
- 初始化资源
- 超时控制
- 异常处理
- 关闭连接
- CPU 密集逻辑隔离

## 7. 复习时建议这样自测
每次看一个示例前，先回答：
- 这段代码里谁负责驱动事件循环？
- 这里到底是顺序还是并发？
- 这里有没有阻塞事件循环的点？
- 这里为什么要用 `async def`？
- 如果去掉 `create_task` 或 `TaskGroup`，行为会怎么变？

如果这几个问题都能稳定答出来，asyncio 就不再只是“框架里的语法糖”。

给你做一个压缩到“机制级别”的总结，直接抓核心：

一、asyncio 三类核心异步对象
1. Coroutine（协程对象）
2. Task（任务对象）
3. Future（未来结果对象）
关系
Coroutine  --被包装-->  Task
Task       ⊂           Future

👉 Task 是 Future 的子类

二、是否“会运行”的本质区别
类型	是否自动执行	本质
Coroutine	❌	只是“待执行代码”
Task	✅	被事件循环调度执行
Future	❌	只是“结果容器”
三、执行机制（关键理解）
1️⃣ Coroutine
coro = foo()   # 不执行
await coro     # 才执行

👉 必须 await 或交给 Task

2️⃣ Task（重点）
task = asyncio.create_task(foo())

👉 这一刻：

✔ 已经提交给事件循环
✔ 等待调度执行

不是 await 才执行

3️⃣ await task 的真实作用
result = await task

作用只有两个：

1. 等待任务完成
2. 获取返回结果

❗ 不负责启动任务

四、调度触发点（容易误解）

Task 虽然创建就“可运行”，但真正执行需要：

当前协程让出控制权（yield control）

比如：

await asyncio.sleep(0)
await xxx

👉 事件循环才有机会切换去执行 Task

五、一句话模型（最重要）
Coroutine：描述任务
Task：调度任务
Future：承载结果
六、最核心结论
Task 在 create_task 时就开始参与调度
await task 只是等待结果，不是启动执行

如果你下一步想深入，我建议你继续搞清这几个进阶点（都是 asyncio 的“坑位”）：

Task 和 gather / wait 的调度差异
TaskGroup（3.11+）的结构化并发
Future 在底层 IO（如 socket / loop.add_reader）中的作用
事件循环切换时机（真正的“并发点”）

可以继续往底层事件循环模型拆，我可以帮你画一版“调度时序图”。
