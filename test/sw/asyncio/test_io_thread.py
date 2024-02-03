"""A simple test on creating an I/O thread"""
import asyncio
import time

class MyClass:
    """This is class body to investigate how to thread with classes"""

    def __init__(self):
        self.name = self.__class__.__name__

    def blocking_io(self, raise_excp):
        """Simultate some blocking I/O"""
        # File operations (such as logging) can block the
        # event loop: run them in a thread pool.
        print(f"{self.name}: Thread is running now, sleeping...")
        time.sleep(1)
        if raise_excp:
            raise RuntimeError("Test Exception")
        print(f"{self.name}: Thread exited gracefully")
        return 0

    async def wait_for_io(self):
        """Warp the waiting into an future"""
        loop = asyncio.get_running_loop()
        for _ in range(0, 10):
            result = await loop.run_in_executor(None, self.blocking_io, False)
            print(f"{self.name}: I/O Thread finished with result {type(result)} {result}")

        # Force an Exception
        await loop.run_in_executor(None, self.blocking_io, True)

        print(f"{self.name}: I/O task loop exited")

async def some_loop():
    """Just some async activity"""
    while True:
        print("Main: executing...")
        await asyncio.sleep(0.5)

async def main():
    """Async main"""
    await asyncio.gather(
        MyClass().wait_for_io(),
        some_loop(),
    )

if __name__ == '__main__':
    asyncio.run(main())
