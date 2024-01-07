"""Provide Timespan"""


class Timespan:
    """Timespan defined by 2 points in time

    The timespan lives in absolute time while the API uses relative time
    (duration). The timespan is defined by a pair if absolute time, a start
    and a stop time. These 2 times can be changed while the span is extended
    when not elapsed already it is while reset when elapsed

    Arguments:
        delay (float): The relative time when timespan starts
        duration (float): The duration of the timespan
        now (method): Method for getting current time
    """
    def __init__(self, now_func, delay=0, duration=0):
        self.now_func = now_func
        self.last = now_func()
        self.start = self.last + delay
        self.stop = self.start + duration

    def __contains__(self, item):
        """Return true if item is within the timespan"""
        return self.start <= item < self.stop

    def __repr__(self):
        return f"{self.__class__.__module__}.{self.__class__.__qualname__} "\
               f"clock={self.now_func.__qualname__}, "\
               f"last = {self.last}, start = {self.start}, stop = {self.stop}"

    def update(self, delay, duration):
        """Update/Maximize the timespan

        Arguments:
            delay (float): Defines new start = now + delay
            duration (float): Defines new stop = now + delay + duration
        """
        self.last = self.now_func()
        start = self.last + delay
        stop = start + duration

        # When time is beyond span, re-initilize, else maximize span
        if self.last < self.stop:
            self.start = min(self.start, start)
            self.stop = max(self.stop, stop)
        else:
            self.start, self.stop = (start, stop)
