"""Map GPIO to installation and provide async interfaces to GPIO"""
import asyncio
from gpio_map import GpioMap, Value, RelaisState


class IoControl:
    """Async interface to GPIO and adding of input/output functionality

    Arguments:
        gpio (GpioMap): GPIO abstraction to use for accessing shield
    """
    S0_DETECTOR = set(range(0, 4))
    S0_METER = set(range(4, 8))
    RELAIS = set(range(8))

    def __init__(self, gpio=None):
        self.gpio = gpio if gpio is not None else GpioMap("IoControl")

    async def timed_on(self, relais, duration):
        """Turn the relais on to a given time"""
        self.gpio.set_relais(relais, Value(RelaisState.ON))
        await asyncio.sleep(duration)
        self.gpio.set_relais(relais, Value(RelaisState.OFF))

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
                s0_index = event.s0_index
                t_stamp = event.event.timestamp_ns

                if s0_index in self.S0_DETECTOR:
                    print(f"{t_stamp}: Received detector event #{s0_index}")
                elif s0_index in self.S0_METER:
                    print(f"{t_stamp}: Received meter event #{s0_index}")
                else:
                    print(f"{t_stamp}: Unmapped event #{s0_index}")

    async def relais_test(self):
        """Run a simple test for all relais

        Drive all relais at once and release them after time given by relais
        index.
        """
        await asyncio.gather(
            *list(map(lambda r: self.timed_on(r, r * 0.1 + 0.2), self.RELAIS))
        )
