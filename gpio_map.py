"""
Map the relais, S0 inputs and PWM output of the I/O Shield
"""

from enum import IntEnum
from dataclasses import dataclass
import gpiod
from gpiod.line import Direction, Value, Edge
from gpiod import EdgeEvent
from rpi_hardware_pwm import HardwarePWM
import version_check

version_check.check_version(gpiod, "2.1.0")


class RelaisState(IntEnum):
    """Assign names to relais states"""
    ON = 0
    OFF = 1


@dataclass
class S0Event:
    """Extend gpiod::EdgeEvent with S0 index

    S0 index is provided to get upper layer code away from Raspberry PI pin
    naming schema. Enumeration is done based on a count starting as 0.
    """
    s0_index: int
    event: EdgeEvent


class GpioMap():
    """Map I/O shield design to RPI GPIOs, provide common class

    A single class for interfacing the I/O shield. Maps the GPIO-Pins to
    relais and PWM outputs and S0 inputs. Uses gpiod and rpi_hardware_pwm
    packages for acessing HW.

    Arguments:
        consumer (str): Name of application registered with gpiod
    """
    RELAIS_PINS = (18, 23, 24, 25, 12, 16, 20, 21)
    S0_PINS = (4, 17, 27, 22, 5, 6, 19, 26)
    PWM_CHANNELS = ((1, 2000),)  # Channel 1, 2000Hz
    CHIP_PATH = "/dev/gpiochip0"
    S0_INDEX_LOOKUP = dict(zip(S0_PINS, range(len(S0_PINS))))

    def __init__(self, consumer="GpioMap"):
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
                edge_detection=Edge.RISING) for l in self.S0_PINS},
        )

        self.pwms = list(map(lambda p: HardwarePWM(*p), self.PWM_CHANNELS))
        for pwm in self.pwms:
            pwm.start(100)

    def __enter__(self):
        return self

    def __exit__(self, exp_type, value, traceback):
        self.relais.set_values({r: Value(RelaisState.OFF)
                                for r in self.RELAIS_PINS})
        list(map(lambda p: p.stop(), self.pwms))
        return exp_type is None

    def set_relais(self, relais, state):
        """Set the state of one relais

        Arguments:
        relais (int): Index of the Relais, see self.RELAIS_PINS
        state (RelaisState): RelaisState.ON or RelaisState.OFF
        """
        self.relais.set_value(self.RELAIS_PINS[relais], Value(state))

    def set_pwm(self, pwm, value):
        """Set the duty cycle of a PWM

        Arguments:
        pwm (int): Index of PWM, see self.PWM_CHANNELS
        value (int): Duty cycle in percent, max is 100
        """
        value = int(min(100, max(0, value)))
        self.pwms[pwm].change_duty_cycle(value)

    def read_input_events(self, wait_timeout=0):
        """Read edge events from gpiod. Map event to S0 index

        This is a blocking call for reading edge events from S0 inputs.

        Arguments:
        wait_timeout (int): Time to wait for an event. None = infinite wait

        Returns:
        list[S0Event]: The list is empty on timeout
        """
        if self.s0s.wait_edge_events(wait_timeout):
            events = self.s0s.read_edge_events()
            return [S0Event(self.S0_INDEX_LOOKUP[e.line_offset], e) for e in events]
        return []
