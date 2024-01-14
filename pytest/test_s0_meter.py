import asyncio
import mock
import pytest
import s0_meter
from s0_meter import S0Meter

class TestS0Meter:
    def test_increment(self):
        with mock.patch.object(s0_meter.time, 'monotonic_ns') as mock_monotonic_ns:
            mock_monotonic_ns.return_value = 1000000000 # 1s
            meter = S0Meter("Test")
            assert meter.total == 0
            assert meter.last_event == 1000000000
            meter.pulse(2000000000) # 2s
            assert meter.total == 1
            assert meter.last_event == 2000000000
            mock_monotonic_ns.return_value = 2500000000 # 2.5s, delta 0.5s
            assert meter.power == 1800
            assert meter.energy == 0.0005
            mock_monotonic_ns.return_value = 4000000000 # 4.0s, delta 2s
            assert meter.power == 900
        meter = S0Meter("Test")
        with pytest.raises(asyncio.exceptions.TimeoutError):
            await asyncio.wait_for(meter.handle_s0_events(), timeout=1.0)

    @pytest.mark.asyncio
    async def test_event_handler_exec(self):
        meter = S0Meter("Test")
        with pytest.raises(asyncio.exceptions.TimeoutError):
            await meter.queue.put(mock.Mock(event=mock.Mock(timestamp_ns=1e9)))
            await asyncio.wait_for(meter.handle_s0_events(), timeout=1.0)
        assert meter.total == 1
