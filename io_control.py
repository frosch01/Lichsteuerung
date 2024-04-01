"""Provide async interfaces to GpioMap

GpioMaps is mapping I/O pins to local indexes. This module provides a async
based interface to control relais and handle incomping edge events.
"""
from enum import IntEnum
import asyncio
from gpio_map import GpioMap, RelaisState, S0Event
from timespan import Timespan
from sun import SunEvent, SunEventType


class RelaisMode(IntEnum):
    """Assign names to relais modes"""
    OFF = 0
    ON = 1
    AUTO = 2


class S0EventDispatcher:
    """Async interface to GPIO and adding of input/output functionality

    Arguments:
        gpio (GpioMap): GPIO abstraction to use for accessing shield
    """
    def __init__(self, gpio=None, wait_timeout=1):
        self.gpio = gpio if gpio is not None else GpioMap("S0EventDispatcher")
        self.queues = [[] for s in range(len(gpio.S0_PINS))]
        self.cancel = False
        self.task = asyncio.create_task(
            self.__handle_detector_events(wait_timeout),
            name=self.__class__,
        )

    async def __handle_detector_events(self, wait_timeout=1):
        """Add this method to your asyncio loop to receive edge events

        For a proper exception handling, a future from this coroutine shall
        be awaited. It is recommneded to add the future to an asyncio.gather.
        Wrapping in an asyncio task shall only be done if the task is awaited
        in order to receive exceptions and to have a proper termination
        handling.
        """
        loop = asyncio.get_running_loop()
        while not self.cancel:
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


class TimedRelais:
    """Control a relais based on a on/off time schedule

    This class makes use of asycio low level APIs to create the relais timing.
    In order to synchronize with high level API, wait can be called.

    Arguments:
        name (str): Name for the devicd controlled by relais
        gpio (GpioMap): Gpio to be used for controlling the relais
        relais (int): Index of the relais inside gpio
    """

    RELAIS = range(len(GpioMap.RELAIS_PINS))

    def __init__(self, name, gpio, relais):
        self.name = name
        self.gpio = gpio
        self.timer = None
        self.finished_event = asyncio.Event()
        self.timespan = Timespan(asyncio.get_running_loop().time)
        self.relais = relais
        self._mode = RelaisMode.AUTO

    def __repr__(self):
        return f"({self.__class__.__module__}.{self.__class__.__qualname__} "\
               f"name = {self.name}, "\
               f"relais = {self.relais}, "\
               f"timespan = {self.timespan})"

    @property
    def mode(self):
        """Return the current mode of the relais"""
        return self._mode

    @mode.setter
    def mode(self, mode):
        """Set the mode of the Relais"""
        if self._mode != mode:
            self._mode = mode
            if self._mode == RelaisMode.ON:
                self.gpio.set_relais(self.relais, RelaisState.ON)
            elif self._mode == RelaisMode.OFF:
                self.gpio.set_relais(self.relais, RelaisState.OFF)
            elif self._mode == RelaisMode.AUTO:
                self.gpio.set_relais(self.relais, RelaisState.OFF)

    @property
    def state(self):
        """Return the current state of the relais"""
        return self.gpio.get_relais(self.relais)

    def timed_off_action(self):
        """Turn the relais off, end of time-on-action"""
        if self._mode == RelaisMode.AUTO:
            self.gpio.set_relais(self.relais, RelaisState.OFF)
        self.finished_event.set()

    def timed_on_action(self):
        """Turn the relais off, plan off action. Intermediate time-on-action"""
        if self._mode == RelaisMode.AUTO:
            self.gpio.set_relais(self.relais, RelaisState.ON)
            loop = asyncio.get_running_loop()
            self.timer = loop.call_at(
                self.timespan.stop, self.timed_off_action)

    def update(self, delay, duration):
        """Update the pending action, create a new one if no one is running"""
        self.timespan.update(delay, duration)
        if self.timer is not None:
            self.timer.cancel()
        self.finished_event.clear()
        loop = asyncio.get_running_loop()
        self.timer = loop.call_at(self.timespan.start, self.timed_on_action)

    async def wait(self):
        """Synchronize with the running action to be finised"""
        await self.finished_event.wait()

    @classmethod
    async def relais_test(cls, gpio):
        """Drive all known relais once after the next for 0.5s

        Instantiate this class for each known relais and call update() for
        each instance.
        """
        relais = [cls(f"Test_{r}", gpio, r) for r in cls.RELAIS]
        _ = list(map(lambda t: t[1].update(t[0], 0.5), enumerate(relais)))
        await asyncio.gather(*[r.wait() for r in relais])


class S0Detector():
    """Control a set of relais on receiving S0Event

    Receive Events from S0 inputs. As a event occurs, trigger TimedRelais from
    a list given when ínstantiating. The detector uses a queue, read in an
    async task for receiving events.

    An S0Detector can be masked, means it is no longer reacting to incoming
    S0Events. The masking is set/unset automatically based on incomiung
    SUN_SET/SUN_RISE events.
    """
    def __init__(self, name, relais_trigger):
        self.name = name
        self.event_queue = asyncio.Queue()
        self.trigger = relais_trigger
        self.task = asyncio.create_task(self.__handle_s0_events(), name=name)
        self.cancel = False
        self.mask = False

    async def __handle_s0_events(self):
        while not self.cancel:
            event = await self.event_queue.get()
            match event:
                case S0Event():
                    if not self.mask:
                        for relais, delay, duration in self.trigger:
                            relais.update(delay, duration)
                case SunEvent():
                    match event.type:
                        case SunEventType.SUN_RISE:
                            self.mask = True
                            for relais, _, _ in self.trigger:
                                relais.mode = RelaisMode.AUTO
                        case SunEventType.SUN_SET:
                            self.mask = False

    @property
    def mask(self):
        """Return the mask state"""
        return self.__masked

    @mask.setter
    def mask(self, other):
        """Set the mask state"""
        self.__masked = other

    @property
    def queue(self):
        """The queue for pushing events to an instance

        The events expected to be pushed shall have types S0Event or SunEvent
        """
        return self.event_queue
