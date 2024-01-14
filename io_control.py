"""Map GPIO to installation and provide async interfaces to GPIO"""
import asyncio
from gpio_map import GpioMap


class S0EventDispatcher:
    """Async interface to GPIO and adding of input/output functionality

    Arguments:
        gpio (GpioMap): GPIO abstraction to use for accessing shield
    """
    def __init__(self, gpio=None):
        self.gpio = gpio if gpio is not None else GpioMap("S0EventDispatcher")
        self.queues = [[] for s in range(len(gpio.S0_PINS))]

    async def handle_detector_events(self, wait_timeout=1):
        """Add this method to your asyncio loop to receive edge events

        For a proper exception handling, a future from this coroutine shall
        be awaited. It is recommneded to add the future to an asyncio.gather.
        Wrapping in an asyncio task shall only be done if the task is awaited
        in order to receive exceptions and to have a proper termination
        handling.
        """
        loop = asyncio.get_running_loop()
        while True:
            # await handles exceptions and signals
            for event in await loop.run_in_executor(
                None,
                self.gpio.read_input_events,
                wait_timeout
            ):
                for queue in self.queues[event.s0_index]:
                    await queue.put(event)

    def register_queue(self, s0_index, queue):
        """Register a queue to push incoming S0 events"""
        self.queues[s0_index].append(queue)
