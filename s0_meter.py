"""A simple meter based on S0 interface"""
import time
import asyncio
from app_state import State, Stateful

class S0Meter(Stateful):
    """An energy meter based on a S0 interface

    Energy is determined by counting S0 edge events.

    Arguments:
        name (str): Gives the meter a name
        total (int): Initial count
    """
    # As given by specification of Eltaco
    PULSE_PER_KWH = 2000

    def __init__(self, name, app_state):
        self.name = name
        self.total = 0
        self.last_event = time.monotonic_ns()
        self.last_delta = 1
        self.event_queue = asyncio.Queue()
        self.task = asyncio.create_task(self.__handle_s0_events(), name=name)
        self._register_state(app_state)

    def _register_state(self, app_state):
        state = app_state.get_state(self.name)
        if state is not None:
            self.total = state.state["total"]
            assert isinstance(self.total, int)
        app_state.register_client(self)

    @property
    def state(self):
        """Return the app_state State of the instance"""
        return State(self.name, {"total": self.total})

    def pulse(self, timestamp):
        """Register last detected pulse with at time"""
        self.total += 1

        # Update event times
        self.last_delta = timestamp - self.last_event
        self.last_event = timestamp

    @property
    def power(self):
        """Get the current power"""
        delta_t = time.monotonic_ns() - self.last_event  # nanos
        delta_t = max((self.last_delta, delta_t)) * 1e-9  # secs
        delta_e = 3.6e6 / self.PULSE_PER_KWH  # Watt seconds
        return delta_e / delta_t

    @property
    def energy(self):
        """Get the consumed energy"""
        return self.total / self.PULSE_PER_KWH

    @energy.setter
    def energy(self, value):
        """Set the consumed energy (calibration)"""
        self.total = int(value * self.PULSE_PER_KWH)

    def set_energy(self, value):
        """Set the consumed energy (calibration)"""
        self.energy = value

    @property
    def queue(self):
        """The queue for pushing events to be counted

        The objects expected to be pushed shall have type S0Event
        """
        return self.event_queue

    async def __handle_s0_events(self):
        """Receive S0 events from a queue and digest

        This method handles events in a loop. It'll not return.
        """
        while True:
            event = await self.event_queue.get()
            self.pulse(event.event.timestamp_ns)
            print(self)

    def __str__(self):
        """Pretty print the meter"""
        return f"({self.name}: {self.power:4.0f}W, {self.energy}kwh)"

    def __repr__(self):
        return self.__str__()
