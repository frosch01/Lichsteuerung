import pytest
import time
from gpio_map import GpioMap, Value, RelaisState

class TestGpioMap:
    """Test class GpioMap

    This test is HW based and requires to be executed on actual hardware.
    Closing relais contacts shall be connected to S0 inputs 1:1.
    """
    def test_gpio_single_on(self):
        with GpioMap("test_all_on") as gpio:
            for seq in range(len(gpio.RELAIS_PINS)):
                gpio.set_relais(seq, RelaisState.ON)
                # S0 inpout filtes take up 100ms to react
                time.sleep(0.2)
                events = gpio.read_input_events(0)
                assert len(events) == 1
                assert events[0].s0_index == seq
                gpio.set_relais(seq, RelaisState.OFF)
                events = gpio.read_input_events(0)
                assert len(events) == 0
        # sleep another 0.2s for input filter relaxing
        time.sleep(0.2)

    def test_gpio_all_on(self):
        with GpioMap("test_all_on") as gpio:
            for seq in range(len(gpio.RELAIS_PINS)):
                gpio.set_relais(seq, RelaisState.ON)
            # S0 inpout filtes take up 100ms to react
            time.sleep(0.2)
            events = gpio.read_input_events(0)
            assert set([e.s0_index for e in events]) == set(range(8))
            for seq in range(len(gpio.RELAIS_PINS)):
                gpio.set_relais(seq, RelaisState.OFF)
            events = gpio.read_input_events(0)
            assert len(events) == 0
        # sleep another 0.2s for input filter relaxing
        time.sleep(0.2)
