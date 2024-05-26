"""I/O instantiation reflecting the installation"""

import asyncio
from io_control import S0EventDispatcher, TimedRelais, S0Detector, RelaisMode, RelaisState, Dimmer
from s0_meter import S0Meter
from gpio_map import GpioMap
from sun import SunSensor
from app_state import AppState

class LightControl:
    """Defines the behavior of the light installation.

    Instantiates and stores all I/O classes as found in our house.
    Interconnects the instances as expected/wanted.

    Provides an interface to nicegui UI.
    """
    def __init__(self):
        self.lamps = {}
        self.detectors = {}
        self.meters = {}
        self.sun = None
        self.dim = None

    async def io_main(self):
        """I/O main routine to be used from nicegui

        Instantiate all classes for the installations found in the house.
        Connect the instances to interoperate as expected.

        This routine will never create a result. It runs in a loop and
        async sleeps forever. This ensures a graceful termination in
        interaction with nicegui
        """

        with GpioMap("light_control") as gpio:

            s0ed = S0EventDispatcher(gpio)

            lamp_yard_front = TimedRelais("Lampe Einfahrt vorne", gpio, 0)
            lamp_yard_rear = TimedRelais("Lampe Einfahrt hinten", gpio, 1)
            lamp_terrasse = TimedRelais("Lampe Terasse", gpio, 2)
            lamp_garage = TimedRelais("Lampe Garage", gpio, 3)

            app_state = AppState("/var/lib/light-control/state.json")
            meters = (
                (4, S0Meter("HVAC-A Arbeiten + Schlafen", app_state)),
                (5, S0Meter("HVAC-B Wohnen + Essen", app_state)),
                (6, S0Meter("HVAC-C Mareike + Ralph", app_state)),
                (7, S0Meter("Außenbeleuchtung", app_state))
            )

            for s0_index, meter in meters:
                s0ed.register_queue(s0_index, meter.queue)

            detectors = (
                (0, S0Detector("Melder Einfahrt", (
                        (lamp_terrasse, 4, 600),
                        (lamp_yard_rear, 2, 300),
                        (lamp_yard_front, 0, 900),
                        (lamp_garage, 6, 600),
                    )
                )),
                (1, S0Detector("Melder Terasse", (
                        (lamp_terrasse, 0, 600),
                        #(lamp_yard_rear, 5, 300),
                        #(lamp_yard_front, 3, 300),
                        #(lamp_garage, 5, 300),
                    )
                )),
                (2, S0Detector("Melder Garage", (
                        (lamp_terrasse, 3, 600),
                        #(lamp_yard_rear, 3, 10),
                        #(lamp_yard_front, 5, 600),
                        (lamp_garage, 0, 900),
                    )
                )),
            )

            sun = SunSensor()

            for s0_index, detector in detectors:
                s0ed.register_queue(s0_index, detector.queue)
                sun.register_queue(detector.queue)

            dim = Dimmer("Dimmer Terrasse", gpio)
            sun.register_queue(dim.queue)

            self.lamps = {
                "yard_front": lamp_yard_front,
                "yard_rear": lamp_yard_rear,
                "terrasse": lamp_terrasse,
                "garage": lamp_garage,
            }

            self.detectors = {
                "yard": detectors[0][1],
                "terrasse": detectors[1][1],
                "garage": detectors[2][1],
            }

            self.meters = {
                "hvac-a": meters[0][1],
                "hvac-b": meters[1][1],
                "hvac-c": meters[2][1],
                "light":  meters[3][1],
            }

            self.sun = sun
            self.dim = dim

            # Wait forever. This ensures a nice nice termination when
            # exectuting from nicegui
            while True:
                try:
                    # Save the state daily
                    await asyncio.sleep(84600)
                except asyncio.exceptions.CancelledError as err:
                    raise err
                finally:
                    # This is execued in any case before try block exits
                    # Exception is raised after finally!!!
                    print("Storing light-control state")
                    app_state.store_state()

    def set_relais_mode(self, name, ui_mode):
        """UI setter for relais mode"""
        match ui_mode:
            case 1:
                mode = RelaisMode.AUTO
            case 2:
                mode = RelaisMode.ON
            case 3:
                mode = RelaisMode.OFF
            case _:
                return
        try:
            self.lamps[name].mode = mode
        except KeyError:
            pass

    def get_relais_mode(self, name):
        """UI getter for relais mode"""
        try:
            match self.lamps[name].mode:
                case RelaisMode.AUTO:
                    return 1
                case RelaisMode.ON:
                    return 2
                case RelaisMode.OFF:
                    return 3
        except KeyError:
            pass

        return 1

    def get_relais_state(self, name):
        """UI getter for relais state"""
        try:
            match self.lamps[name].state:
                case RelaisState.ON:
                    return 'yellow'
                case RelaisState.OFF:
                    return 'gray'
                case _:
                    return 'red'
        except KeyError:
            return 'red'

    def set_detector(self, name, ui_mode):
        """UI setter for detector mode"""
        match ui_mode:
            case 1:
                mask = False
            case 2:
                mask = True
            case _:
                return

        try:
            self.detectors[name].mask = mask
        except KeyError:
            pass

    def get_detector(self, name):
        """UI getter for detector mode"""
        try:
            return 2 if self.detectors[name].mask else 1
        except KeyError:
            pass
        return 1

if __name__ == '__main__':
    light_control = LightControl()
    asyncio.run(light_control.io_main())
