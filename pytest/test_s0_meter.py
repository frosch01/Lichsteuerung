import mock
import pytest
import s0_meter
from s0_meter import S0Meter

class TestS0Meter:
    def test_increment(self):
        with mock.patch.object(s0_meter.time, 'monotonic_ns') as mock_monotonic_ns:
            mock_monotonic_ns.return_value = 1000000000 # 1s
            meter = S0Meter()
            assert meter.total == 0
            assert meter.last_event == 1000000000
            meter.pulse(2000000000) # 2s
            assert meter.total == 1
            assert meter.last_event == 2000000000
            mock_monotonic_ns.return_value = 2500000000 # 2.5s, delta 0.5s
            assert meter.power == 3600
            assert meter.energy == 0.001
            mock_monotonic_ns.return_value = 4000000000 # 4.0s, delta 2s
            assert meter.power == 1800
