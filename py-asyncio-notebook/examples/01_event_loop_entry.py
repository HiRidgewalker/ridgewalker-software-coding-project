import asyncio


async def say_after(delay: float, label: str) -> None:
    print(f"start {label}")
    await asyncio.sleep(delay)
    print(f"done  {label}")


async def main() -> None:
    print("calling async function returns a coroutine object:")
    coroutine = say_after(0.1, "demo")
    print(coroutine)
    await coroutine


if __name__ == "__main__":
    asyncio.run(main())
