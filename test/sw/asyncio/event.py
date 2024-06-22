import asyncio

async def waiter(event, num):
    while True:
        print(f'{num}: waiting for it')
        await event.wait()
        event.clear()
        print(f'{num}: got it!')
        await asyncio.sleep(0.1)

async def main():
    # Create an Event object.
    event = asyncio.Event()

    # Spawn 2 Tasks to wait until 'event' is set.
    waiter_task0 = asyncio.create_task(waiter(event, 0))
    waiter_task1 = asyncio.create_task(waiter(event, 1))

    # Sleep for 1 second and set the event.
    while True:
        await asyncio.sleep(1)
        print("Sending event: ")
        event.set()

    # Wait until the waiter task is finished.
    await waiter_task0
    await waiter_task1

asyncio.run(main())
