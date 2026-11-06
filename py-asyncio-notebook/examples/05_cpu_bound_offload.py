import asyncio
import time


def cpu_bound_work(limit: int) -> int:
    total = 0
    for number in range(limit):
        total += number * number
    return total


async def bad_cpu_demo() -> None:
    print("=== bad cpu demo ===")
    started = time.perf_counter()
    cpu_bound_work(40_000_000)
    elapsed = time.perf_counter() - started
    print(f"cpu work blocked the event loop for {elapsed:.2f}s")


async def good_cpu_demo() -> None:
    print("=== offload with asyncio.to_thread ===")
    started = time.perf_counter()
    result = await asyncio.to_thread(cpu_bound_work, 40_000_000)
    elapsed = time.perf_counter() - started
    print(f"thread offload finished in {elapsed:.2f}s, result={result}")


async def heartbeat() -> None:
    for index in range(6):
        print(f"heartbeat {index}")
        await asyncio.sleep(0.2)


async def compare() -> None:
    print("running blocking cpu work with heartbeat")
    started = time.perf_counter()
    async with asyncio.TaskGroup() as tg:
        tg.create_task(bad_cpu_demo())
        tg.create_task(heartbeat())
    print(f"combined elapsed: {time.perf_counter() - started:.2f}s")
    print()
    print("running offloaded cpu work with heartbeat")
    started = time.perf_counter()
    async with asyncio.TaskGroup() as tg:
        tg.create_task(good_cpu_demo())
        tg.create_task(heartbeat())
    print(f"combined elapsed: {time.perf_counter() - started:.2f}s")


if __name__ == "__main__":
    # 总结：
    # 1. 这个文件要说明：CPU 密集任务不是 asyncio 擅长直接处理的场景
    # 2. 如果在事件循环里直接执行大量 CPU 计算，别的协程会被卡住，心跳任务无法及时推进
    # 3. asyncio.to_thread(...) 可以把这类同步计算转移到线程中执行，
    #    从而避免长时间阻塞事件循环
    # 4. 这并不意味着 CPU 计算被 asyncio “加速”了，
    #    而是意味着事件循环不会因为这段计算而失去响应能力
    #
    # 这个示例整体想体现：
    # “asyncio 适合 I/O 等待型并发；遇到 CPU 密集工作时，重点是隔离阻塞，而不是指望 async/await 直接提速。”
    asyncio.run(compare())
