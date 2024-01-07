from unittest.mock import Mock
import asyncio
import pytest
from timespan import Timespan

class TestTimespan:

    def test_init(self):
        ts = Timespan(Mock(return_value = 1), 2, 3)
        assert ts.start==3
        assert ts.stop==6

    @pytest.mark.parametrize("t,is_in", [
        (39.99, False),
        (40.00, True),
        (50.00, True),
        (59.99, True),
        (60.00, False),
    ])
    def test_contains(self, t, is_in):
        ts = Timespan(Mock(return_value = 30), 10, 20)
        assert (t in ts) == is_in

    @pytest.mark.parametrize("now,delay,duration,span", [
        ( 5,  3, 14, ( 8, 22)),  # Update both
        ( 6,  5, 14, (10, 25)),  # Update stop
        ( 7,  2,  1, ( 9, 20)),  # Update start
        ( 8,  3,  4, (10, 20)),  # no update
        (12,  1, 13, (10, 26)),  # update inside
    ])
    def test_update(self, now, delay, duration, span):
        # start @ 10, end @ 20
        clock=Mock(return_value = 0., __qualname__="unittest.Mock")
        ts = Timespan(clock, 10, 10)
        # Update @1 to start @ 12, end @ 15, minimizing
        clock.return_value = now
        ts.update(delay, duration)
        assert (ts.start, ts.stop) == span

    def test_repr(self):
        clock = Mock(return_value = 0., __qualname__="unittest.Mock")
        ts = Timespan(clock, 10, 10)
        assert type(ts.__repr__()) == str
