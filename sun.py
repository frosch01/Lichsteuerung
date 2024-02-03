""" A daylight "sensor" based on local time and geo coordinates"""
import asyncio
from enum import IntEnum
from dataclasses import dataclass
from datetime import datetime, timedelta
try:
    from zoneinfo import ZoneInfo
except ImportError:
    from backports.zoneinfo import ZoneInfo
from astral import Observer, sun


class SunEventType(IntEnum):
    """Distinguish sun events"""
    SUN_RISE = 0
    SUN_SET = 1


@dataclass
class SunEvent:
    """Event sent on sunset and sunrise"""
    type: SunEventType
    event_time: datetime
    now: datetime


class SunSensor:
    """Timed daylight "sensor" based on geo coordinates"""
    def __init__(self, polling_interval=timedelta(days=1)):
        self.polling_interval = polling_interval
        self.tzinfo = ZoneInfo("Europe/Berlin")
        self.home = Observer(48.742211, 9.2068, 430)
        self.loop = asyncio.get_running_loop()
        self.wait_event = asyncio.Event()
        self.cur_event = None
        self.loop.call_soon(self.__sun_timeout)
        self.queues = []

    def __sun_timeout(self):
        now = datetime.now(self.tzinfo)
        today_sunrise = sun.sunrise(self.home, now, self.tzinfo)
        today_sunset = sun.sunset(self.home, now, self.tzinfo)
        tomorrow = now + timedelta(days=1)
        tomorrow_sunrise = sun.sunrise(self.home, tomorrow, self.tzinfo)
        tomorrow_sunset = sun.sunset(self.home, tomorrow, self.tzinfo)
        yesterday = now - timedelta(days=1)
        yesterday_sunset = sun.sunset(self.home, yesterday, self.tzinfo)

        # Avoid not beeing close before event time and not creating the event.
        # Eventloop time is no world clock, there may be drift.
        hysterisis = timedelta(minutes=1)

        if now < today_sunrise - hysterisis:
            print("It is night")
            self.cur_event = SunEvent(SunEventType.SUN_SET, yesterday_sunset, now)
            tt_rise = today_sunrise - now
            tt_set = today_sunset - now
        elif now < today_sunset - hysterisis:
            print("It is day")
            self.cur_event = SunEvent(SunEventType.SUN_RISE, today_sunrise, now)
            tt_set = today_sunset - now
            tt_rise = tomorrow_sunrise - now
        else:
            print("It is night")
            self.cur_event = SunEvent(SunEventType.SUN_SET, today_sunset, now)
            tt_rise = tomorrow_sunrise - now
            tt_set = tomorrow_sunset - now

        # Create a new event to wait for next event
        self.wait_event.set()
        self.wait_event = asyncio.Event()

        # Push event to queues
        for queue in self.queues:
            try:
                queue.put_nowait(self.cur_event)
            except asyncio.QueueFull:
                print(f"{self.__class__}: Queue overrunn")

        # Sleep till next event, plan with some clock drift
        sleep_duration = min(tt_rise, tt_set, self.polling_interval).total_seconds()
        self.loop.call_later(sleep_duration, self.__sun_timeout)

    async def wait_next(self):
        """Wait for the next sunrise/sunset event, what ever happens first

        If the class was initialized with a polling interval, the last event
        is repeated with the given interval.
        """
        await self.wait_event.wait()
        # self.wait_event is consumed now !!!
        return self.cur_event

    def register_queue(self, queue):
        """Register a queue to receive sunrise/sunset events"""
        self.queues.append(queue)
