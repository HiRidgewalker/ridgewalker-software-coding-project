# await 知识点总结

## 1. `await` 的本质是什么

`await` 的核心不是“把协程放进事件循环”，而是：

1. 等待一个可等待对象完成
2. 在等待期间暂停当前协程
3. 把控制权交还给事件循环
4. 等待目标完成后，再从当前位置继续执行

所以，`await` 更准确的理解是：

“当前协程先停一下，等这个东西完成后我再继续；在我等待的时候，事件循环可以去推进别的任务。”

## 2. `await` 不等于创建任务

这是最容易混淆的地方。

例如：

```python
await fake_io("A", 1)
```

这里发生的是：

1. `fake_io("A", 1)` 先创建一个协程对象
2. `await` 驱动这个协程执行，并等待它结束

但是这不等于“创建了一个独立并发运行的任务”。

真正创建任务通常是：

```python
task = asyncio.create_task(fake_io("A", 1))
```

或者：

```python
async with asyncio.TaskGroup() as tg:
    task = tg.create_task(fake_io("A", 1))
```

这里才是把协程对象包装成 `Task`，交给事件循环独立调度。

## 3. `await` 让出的不是“CPU 所有权”

“让出 CPU”这个说法有助于直觉理解，但不够准确。

更准确的说法是：

- `await` 让当前协程挂起
- 控制权回到事件循环
- 事件循环决定下一个推进哪个任务

所以不是某个协程真的“占有 CPU”，而是事件循环在单线程里轮流推进不同协程。

## 4. 三种常见情况

### 4.1 `await` 一个协程对象

```python
await fake_io("A", 1)
```

含义：
- 创建协程对象
- 立刻等待它执行完成

这通常是顺序执行，不代表并发。

### 4.2 `await` 一个任务对象

```python
task = asyncio.create_task(fake_io("A", 1))
await task
```

含义：
- 任务已经被事件循环调度
- 当前协程现在等待它完成

这里和直接 `await 协程对象` 的区别在于：任务可以先被调度运行，再在后面等待结果。

### 4.3 `await` 一个真正会挂起的操作

```python
await asyncio.sleep(1)
```

这时当前协程会暂停，事件循环可以去执行别的任务。

异步的收益通常就是在这种“等待期间，别的任务也能推进”的场景里产生的。

## 5. 一句话总结

- `await` 的本质是“暂停当前协程，等待某个可等待对象完成”
- `await` 不等于“创建任务”
- 真正的并发调度通常来自 `create_task()` 或 `TaskGroup`
- `await` 让出的是“当前协程的执行控制权”，不是字面意义上的“CPU 所有权”

## 6. 一个最短判断法

看到 `await xxx` 时，优先问自己两件事：

1. `xxx` 是什么？是协程对象、任务，还是别的可等待对象？
2. 这里是在顺序等待，还是前面已经把它作为任务调度出去了？

只要这两个问题能答清楚，`await` 基本就不会再混淆。

## 7. “让出执行控制权”是什么意思

“`await` 让出的是当前协程的执行控制权，不是字面意义上的 CPU 所有权” 这句话的意思是：

`await` 影响的是“程序接下来由谁继续执行”，不是在操作操作系统层面的 CPU 分配。

### 7.1 要分清两层概念

第一层是 Python `asyncio` 这一层，这里有：
- 协程
- 任务
- 事件循环

`await` 发生在这一层。它的效果是：
- 当前协程运行到 `await` 这里，先暂停
- 把“接下来该执行谁”的决定权交回事件循环
- 事件循环去看还有没有别的任务可以推进
- 等待的对象完成后，再回来继续当前协程

所以，“让出执行控制权”的意思是：

当前这个协程不再继续往下跑了，轮到事件循环安排别的协程。

第二层是操作系统和 CPU 这一层。

CPU 并不是“属于某个协程”的。协程不是操作系统线程，不会真的单独占有 CPU。实际执行 Python 字节码的，通常还是那个线程。

所以 `await` 不是在说：
- “把 CPU 从协程 A 手里拿走，再给协程 B”

而是在说：
- “协程 A 先停一下，事件循环来决定接下来执行哪个协程”

### 7.2 一个类比

- CPU 像一个工位
- 事件循环像调度员
- 协程像一张张待处理工单

那么 `await` 不是“把工位让出去”，而是：

“这张工单先挂起，调度员去拿下一张工单来处理。”

### 7.3 一个最小例子

```python
async def a():
    print("a1")
    await asyncio.sleep(1)
    print("a2")

async def b():
    print("b1")
    await asyncio.sleep(1)
    print("b2")
```

如果这两个协程都已经作为任务交给事件循环，那么运行过程更像这样：

1. 事件循环先推进 `a()`，打印 `a1`
2. `a()` 遇到 `await asyncio.sleep(1)`，暂停
3. 控制权回到事件循环
4. 事件循环去推进 `b()`，打印 `b1`
5. `b()` 也遇到 `await`，暂停
6. 等 1 秒后，再分别恢复它们

这里不是 `a()` 把“CPU 所有权”给了 `b()`，而是 `a()` 暂停了，事件循环改去推进 `b()`。

### 7.4 一句话压缩

- “CPU 所有权”是操作系统层面的说法
- “执行控制权”是 `asyncio` 调度层面的说法
- `await` 改变的是后者，不是前者

## 8. `async` 的作用是什么

`async` 最常见的用法是和 `def` 组合成 `async def`，它的作用不是“让函数自动变快”，而是：

1. 把这个函数定义成一个协程函数
2. 说明这个函数可以在内部使用 `await`
3. 说明这个函数的调用结果不是普通返回值，而是一个协程对象
4. 让这个函数能够参与 `asyncio` 的异步调度体系

例如：

```python
async def fetch_data():
    ...
```

这表示：
- `fetch_data` 是一个协程函数
- 调用 `fetch_data()` 时，不会立刻执行函数体
- 而是先返回一个协程对象
- 之后需要通过 `await fetch_data()`、`asyncio.create_task(fetch_data())` 或 `asyncio.run(fetch_data())` 之类的方式来驱动它运行

所以，`async` 的核心作用不是“执行”，而是“把函数声明为异步协程函数，让它能被异步框架或事件循环调度”。

### 8.1 `async` 不会自动带来性能收益

如果函数内部没有异步等待点，或者做的事情本质上是同步阻塞、CPU 密集计算，那么仅仅写成：

```python
async def work():
    ...
```

并不会天然带来异步收益。

真正的收益来自：
- 函数内部有合适的 `await`
- 等待期间事件循环可以去推进别的任务

## 9. 哪些情况下用 `async`，哪些情况下用 `await`

### 9.1 什么时候需要使用 `async`

通常在下面这些情况下把函数写成 `async def`：

1. 函数内部需要 `await` 其他异步操作
2. 这个函数本身就是异步调用链中的一环
3. 这个函数要被 `create_task()`、`TaskGroup.create_task()` 或异步框架调度
4. 这个函数处理的是 I/O 等待型工作，而不是纯计算工作

常见场景：
- 发起异步 HTTP 请求
- 调用异步数据库驱动
- 消费异步消息队列
- 处理异步 websocket 连接
- 异步 sleep、异步超时控制、异步锁
- 编写 FastAPI、aiohttp、异步爬虫、异步客户端里的处理函数

示例：

```python
async def fetch_user():
    data = await client.get("/users/1")
    return data
```

这里 `fetch_user` 需要写成 `async def`，因为内部需要 `await`。

### 9.2 哪些情况下通常不需要使用 `async`

下面这些情况通常不应该为了“看起来异步”而写成 `async def`：

1. 纯计算逻辑
2. 纯数据处理逻辑
3. 没有任何 `await` 的函数
4. 只是简单拼接字符串、转换列表、校验参数的函数
5. 内部调用的全都是同步阻塞库

常见例子：
- 排序、过滤、映射
- 字符串格式化
- JSON 数据整理
- 纯数学计算
- 本地 CPU 密集循环

这类函数更适合保持同步函数：

```python
def normalize_name(name: str) -> str:
    return name.strip().title()
```

### 9.3 什么时候需要使用 `await`

当你已经处在 `async def` 函数内部，并且要等待一个可等待对象完成时，就需要 `await`。

最常见的是等待：
- 协程对象
- 任务对象
- `asyncio.sleep(...)`
- `asyncio.to_thread(...)`
- 异步客户端返回的 awaitable 对象
- 异步上下文管理器或异步迭代过程中的异步操作

常见场景：

1. 等待异步 HTTP 响应

```python
data = await client.get(url)
```

2. 等待数据库查询结果

```python
row = await conn.fetch_one(query)
```

3. 等待任务完成

```python
task = asyncio.create_task(fetch_data())
result = await task
```

4. 主动挂起当前协程，让事件循环调度别的任务

```python
await asyncio.sleep(1)
```

5. 把阻塞同步函数转到线程执行

```python
result = await asyncio.to_thread(cpu_or_blocking_func)
```

### 9.4 哪些情况下不应该随便写 `await`

不应该对普通值使用 `await`，例如：

```python
value = 123
await value
```

这是错误的，因为 `123` 不是可等待对象。

也不要把 `await` 用在纯同步函数返回值上：

```python
def get_name():
    return "Tom"

await get_name()
```

这同样是错误的。

所以，`await` 不是“凡是函数调用都加上”，而是：

“只有当右侧对象是可等待对象，并且我确实要等待它完成时，才使用 `await`。”

## 10. 常用判断法

遇到一个函数时，可以按这个顺序判断：

### 10.1 这个函数要不要写成 `async def`

先问：
- 它内部有没有真正的异步等待操作？
- 它是不是异步调用链中的一部分？
- 它处理的是不是 I/O 等待型工作？

如果答案大多是“是”，可以考虑写成 `async def`。

如果它只是纯同步逻辑，就保持普通 `def`。

### 10.2 这里要不要写 `await`

再问：
- 右侧是不是可等待对象？
- 我现在是不是要等待它执行完成？

如果是，就写 `await`。

如果不是，就不要写。

## 11. 一段最短总结

- `async` 的作用是把函数定义成协程函数，使它能参与异步调度
- `async` 本身不自动带来性能提升
- 当函数内部需要等待异步操作时，通常要写成 `async def`
- 当你在异步函数内部等待一个可等待对象时，通常要使用 `await`
- I/O 等待型工作常适合异步
- 纯计算和纯同步逻辑通常不适合为了形式而强行写成异步

## 12. 异步迭代

异步迭代用于“每次取下一个元素时，都可能需要等待”的场景。

普通迭代是：

```python
for item in items:
    ...
```

异步迭代是：

```python
async for item in async_items:
    ...
```

区别在于：
- 普通 `for` 适合立即可用的数据
- `async for` 适合每次取值都可能涉及异步等待的数据流

### 12.1 什么时候需要异步迭代

常见场景：
- 按批次异步读取网络流
- 异步消费消息队列
- 异步逐条读取 websocket 消息
- 异步分页拉取远程数据
- 异步数据库游标遍历

这类场景的特点是：
- 数据不是一次性都准备好的
- 每次拿下一项时，可能都要等待 I/O

### 12.2 一个最小示例

```python
import asyncio


class AsyncCounter:
    def __init__(self, limit: int) -> None:
        self.current = 0
        self.limit = limit

    def __aiter__(self):
        return self

    async def __anext__(self):
        if self.current >= self.limit:
            raise StopAsyncIteration

        await asyncio.sleep(0.5)
        self.current += 1
        return self.current


async def main():
    async for item in AsyncCounter(3):
        print(item)


asyncio.run(main())
```

这段代码的输出会每隔 0.5 秒打印一个数字：

```python
1
2
3
```

### 12.3 这个示例想说明什么

这个示例想说明：

1. `async for` 遍历的不是普通可迭代对象，而是异步可迭代对象
2. 异步迭代器通过 `__aiter__()` 和 `__anext__()` 工作
3. `__anext__()` 可以是异步的，因此每次取下一个值时都可以 `await`
4. 当没有更多数据时，要抛出 `StopAsyncIteration`

### 12.4 异步迭代和普通迭代的本质区别

普通迭代：
- 下一个值可以立刻拿到
- 不需要等待

异步迭代：
- 下一个值可能暂时还没准备好
- 需要等待后才能拿到

所以 `async for` 很适合“边等边取”的数据流。

### 12.5 一个更贴近日常使用的想象场景

例如你在处理 websocket 消息：

```python
async for message in websocket:
    print(message)
```

这里的含义不是“消息已经都在本地列表里了”，而是：

- 每次循环都去等下一条消息到来
- 消息到了才继续执行循环体
- 没有消息时，当前协程会挂起，事件循环可以去推进别的任务

### 12.6 使用异步迭代时的判断法

如果你面对的是：
- 一次性拿齐的数据集合，用普通 `for`
- 逐个异步到来的数据流，用 `async for`

一句话总结：

异步迭代适合“每次取下一个元素都可能需要等待”的场景，本质上是把“等待下一项数据”这件事也纳入了 asyncio 的调度体系。
