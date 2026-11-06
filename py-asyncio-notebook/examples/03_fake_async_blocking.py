import asyncio
import time


async def blocking_task() -> None:
    # 这个函数虽然写成 async def，
    # 但内部用了同步阻塞的 time.sleep(2)。
    # 它不会把控制权交回事件循环。
    print("blocking task: calling time.sleep(2)")
    time.sleep(2)
    print("blocking task: finished")


async def cooperative_task() -> None:
    for index in range(4):
        print(f"cooperative task tick {index}")
        # asyncio.sleep(...) 是“合作式等待”：
        # 当前协程在这里暂停，把控制权交回事件循环，
        # 事件循环就可以去推进别的任务。
        await asyncio.sleep(0.5)


async def main() -> None:
    started = time.perf_counter()
    # 这里把两个协程都作为任务交给事件循环管理。
    async with asyncio.TaskGroup() as tg:
        tg.create_task(blocking_task())
        tg.create_task(cooperative_task())
    elapsed = time.perf_counter() - started
    print(f"total elapsed: {elapsed:.2f}s")
    # 关键观察点：
    # cooperative_task 本来应该每 0.5 秒推进一次，
    # 但由于 blocking_task 里用了 time.sleep(2)，
    # 整个事件循环先被卡住了 2 秒，导致 cooperative_task 无法及时运行。
    #
    # 这个示例要说明：
    # 1. async def 不等于真正异步
    # 2. asyncio 的并发是合作式并发
    # 3. 只要某个任务里混入阻塞同步代码，整个事件循环都可能被拖住
    print("notice how cooperative_task could not make progress during time.sleep")


if __name__ == "__main__":
    # asyncio.run(...) 创建事件循环并运行顶层协程 main()。
    asyncio.run(main())
