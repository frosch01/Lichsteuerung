"""A simple meter based on S0 interface"""
import time
import asyncio

class S0Meter:
    """An energy meter based on a S0 interface

    Energy is determined by counting S0 edge events.
    """
    PULSE_PER_KWH = 2000

    def __init__(self, name, total=0):
        self.name = name
        self.total = total
        self.last_event = time.monotonic_ns()
        self.last_delta = 1
        self.event_queue = asyncio.Queue()

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

    @property
    def queue(self):
        """The queue for pushing events to be counted"""
        return self.event_queue

    async def handle_s0_events(self):
        """Receive S0 events from a queue and digest

        This method handles events in a loop. It'll not return.
        """
        while True:
            event = await self.event_queue.get()
            self.pulse(event.event.timestamp_ns)
            print(self)

    def __str__(self):
        """Pretty print the meter"""
        return f"({self.name}: {self.power:4.0f}W, {self.energy}kwh"
