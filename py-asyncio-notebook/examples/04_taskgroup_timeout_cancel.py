import asyncio


async def worker(name: str, delay: float) -> None:
    try:
        # 一个通用 worker，用来模拟“要等待一段时间的异步任务”。
        print(f"{name}: start")
        await asyncio.sleep(delay)
        print(f"{name}: finished normally")
    except asyncio.CancelledError:
        # 任务如果在 await 挂起点收到取消请求，会抛出 CancelledError。
        # 这里打印出来，是为了让你看到“任务确实被取消了”。
        print(f"{name}: cancelled")
        raise
    finally:
        # finally 用来演示：无论任务是正常结束、超时取消，还是手动取消，
        # 清理逻辑都应该在这里执行。
        print(f"{name}: cleanup")


async def timeout_demo() -> None:
    # 这个示例想体现：
    # 1. asyncio.timeout(...) 可以给一段异步操作加超时边界
    # 2. 当执行时间超过边界时，内部正在跑的任务会被取消
    # 3. 外层最终看到的是 TimeoutError
    print("=== timeout demo ===")
    try:
        async with asyncio.timeout(1.5):
            await worker("slow-worker", 3)
    except TimeoutError:
        # slow-worker 本质上是因为取消而停下来的，
        # 但 timeout 对外包装成 TimeoutError，方便调用方按“超时”处理。
        print("timeout reached")


async def taskgroup_demo() -> None:
    # 这个示例想体现：
    # 1. TaskGroup 是 Python 3.11+ 推荐的结构化并发方式
    # 2. create_task(...) 会把协程对象包装成任务，交给事件循环调度
    # 3. 离开 async with TaskGroup() 时，会等待组内任务全部结束
    print("=== taskgroup demo ===")
    async with asyncio.TaskGroup() as tg:
        tg.create_task(worker("fast-worker", 0.5))
        tg.create_task(worker("medium-worker", 1.0))


async def cancellation_demo() -> None:
    # 这个示例想体现：
    # 1. asyncio.create_task(...) 会创建一个独立调度的任务
    # 2. task.cancel() 是主动发起取消请求
    # 3. 调用方 await 这个任务时，可以明确观察到取消结果
    print("=== cancellation demo ===")
    task = asyncio.create_task(worker("manual-cancel-worker", 5))
    await asyncio.sleep(1)
    # 这里不是瞬间“杀死”任务，而是告诉任务：请取消。
    # 任务会在下一次 await 挂起点感知到取消。
    task.cancel()
    try:
        await task
    except asyncio.CancelledError:
        print("caller observed cancellation")


async def main() -> None:
    # 你现在把前两个示例先注释掉了，只运行手动取消示例。
    # 如果想完整观察这个文件的三个主题，可以依次放开下面两行。
    # await timeout_demo()
    print()
    # await taskgroup_demo()
    print()
    await cancellation_demo()


if __name__ == "__main__":
    # 总结：
    # 1. timeout_demo：演示“超时”本质上会触发内部任务取消
    # 2. taskgroup_demo：演示如何把多个任务作为一个结构化整体来管理
    # 3. cancellation_demo：演示如何手动取消任务，以及调用方如何感知取消
    #
    # 这个文件整体想说明的不是“如何让任务跑起来”，
    # 而是“异步任务在真实程序里，如何被超时、取消和清理正确管理”。
    asyncio.run(main())
