import asyncio
import time


async def fake_io(name: str, delay: float) -> str:
    print(f"{name}: start")
    # asyncio.sleep(...) 返回一个可等待对象；await 会把控制权交回事件循环。
    await asyncio.sleep(delay)
    print(f"{name}: done")
    return name


async def run_sequential() -> None:
    started = time.perf_counter()
    # fake_io("A", 1) 这里会先创建一个协程对象，
    # 然后被 await 立刻交给当前事件循环执行。
    await fake_io("A", 1)
    # 这一行同样会先创建协程对象，再被 await；
    # 因为是写在上一行之后，所以整体效果是串行执行。
    await fake_io("B", 1)
    elapsed = time.perf_counter() - started
    print(f"sequential elapsed: {elapsed:.2f}s")


async def run_concurrent() -> None:
    started = time.perf_counter()
    # TaskGroup 用来在当前事件循环里管理一组并发任务。
    async with asyncio.TaskGroup() as tg:
        # fake_io("A", 1) 先创建协程对象；
        # tg.create_task(...) 再把这个协程对象包装成 Task，
        # 交给当前事件循环调度。
        task_a = tg.create_task(fake_io("A", 1))
        # 这一行做的是同样的事：先创建协程对象，再创建任务。
        task_b = tg.create_task(fake_io("B", 1))
    # 离开 TaskGroup 时，会等待这组任务全部完成或抛出异常。
    elapsed = time.perf_counter() - started
    print(f"concurrent elapsed: {elapsed:.2f}s")
    print(f"results: {task_a.result()}, {task_b.result()}")


async def main() -> None:
    print("=== sequential awaits ===")
    # run_sequential() 会先创建协程对象，然后被 await 执行。
    await run_sequential()
    print()
    print("=== concurrent task scheduling ===")
    # run_concurrent() 也是一样：先创建协程对象，再被 await 执行。
    await run_concurrent()


if __name__ == "__main__":
    # main() 会先创建顶层协程对象。
    # asyncio.run(...) 负责创建事件循环，并把 main() 放进事件循环中执行。
    # 事件循环运行期间，main() 里面再继续创建并调度其他协程和任务。
    asyncio.run(main())
