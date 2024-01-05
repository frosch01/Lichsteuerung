"""
Access the relais, S0 inputs and PWM output of the LightControl HW
"""

# try:
#    f = open('/sys/firmware/devicetree/base/model', 'r', encoding="ascii")
# except OSError:
#    print("No Raspberry PI detected. Running with stub GPIO")
#    from GPIO_stub import GPIO
# else:
#    print(f"Raspberry PI model {f.readline()} detected. Running on real GPIO pins")

from enum import IntEnum
import asyncio
import gpiod
from gpiod.line import Direction, Value, Edge
from rpi_hardware_pwm import HardwarePWM
import version_check

version_check.check_version(gpiod, "2.1.0")


class RelaisState(IntEnum):
    """Assign names to relais states"""
    ON = 0
    OFF = 1


class IoControl():
    """Map HW design to RPI GPIOs"""
    RELAIS_PINS = [18, 23, 24, 25, 12, 16, 20, 21]
    DETECTOR_PINS = [4, 17, 27, 22]
    METER_PINS = [5, 6, 19, 26]
    PWM_CHANNELS = [(1, 2000)]  # Channel 1, 2000Hz
    CHIP_PATH = "/dev/gpiochip0"

    def __init__(self, consumer):
        self.relais = gpiod.request_lines(
            self.CHIP_PATH,
            consumer=consumer,
            config={
                l: gpiod.LineSettings(
                    direction=Direction.OUTPUT,
                    output_value=Value(RelaisState.OFF))
                for l in self.RELAIS_PINS
            },
        )

        self.s0s = gpiod.request_lines(
            self.CHIP_PATH,
            consumer=consumer,
            config={l: gpiod.LineSettings(
                edge_detection=Edge.RISING) for l in self.DETECTOR_PINS + self.METER_PINS},
        )

        self.dims = list(map(lambda x: HardwarePWM(*x), self.PWM_CHANNELS))
        for pwm in self.dims:
            pwm.start(100)

    def __enter__(self):
        return self

    def __exit__(self, exp_type, value, traceback):
        self.relais.set_values({r: Value(RelaisState.OFF)
                                for r in self.RELAIS_PINS})
        list(map(lambda p: p.stop(), self.dims))
        return exp_type is None

    def set_relais(self, relais, state):
        """Set the state of a relais"""
        self.relais.set_value(self.RELAIS_PINS[relais], Value(state))

    async def timed_on(self, relais, duration):
        """Turn the relais on to a given time"""
        self.relais.set_value(self.RELAIS_PINS[relais], Value(RelaisState.ON))
        await asyncio.sleep(duration)
        self.relais.set_value(self.RELAIS_PINS[relais], Value(RelaisState.OFF))

    def set_pwm(self, pwm, value):
        """Set the duty cycle of a PWM"""
        value = int(min(100, max(0, value)))
        self.dims[pwm].change_duty_cycle(value)

    def __detector_event_thread(self, wait_timeout):
        """Thread method for reading edge events from gpiod"""
        if self.s0s.wait_edge_events(wait_timeout):
            return self.s0s.read_edge_events()
        return []

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
                self.__detector_event_thread,
                wait_timeout
            ):
                try:
                    print(f"{event.timestamp_ns}: Received detector event "
                          f"#{self.DETECTOR_PINS.index(event.line_offset)}")
                except ValueError:
                    pass

                try:
                    print(f"{event.timestamp_ns}: Received meter event "
                          f"#{self.METER_PINS.index(event.line_offset)}")
                except ValueError:
                    pass

    async def relais_test(self):
        """Test sequence for all relais. The on time is derived from the gpio offset"""
        await asyncio.gather(
            *list(
                map(lambda r: self.timed_on(r, r), range(len(self.RELAIS_PINS)))
            )
        )
