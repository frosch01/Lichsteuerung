import asyncio
import mock
import pytest
import s0_meter
from s0_meter import S0Meter

class TestS0Meter:

    def app_state_mock(self, initial=None):
        app_state = mock.Mock
        app_state.get_state = mock.Mock(return_value=mock.Mock())
        if initial is None:
            app_state.get_state.return_value = None
        else:
            app_state.get_state.return_value.state = {"total": initial}
        app_state.register_client = mock.Mock()
        return app_state

    @pytest.mark.asyncio
    async def test_increment(self):
        with mock.patch.object(s0_meter.time, 'monotonic_ns') as mock_monotonic_ns:
            mock_monotonic_ns.return_value = 1000000000 # 1s
            meter = S0Meter("Test", self.app_state_mock())
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
            # Graceful shutdown...
            with pytest.raises(asyncio.exceptions.CancelledError):
                meter.task.cancel()
                await asyncio.wait_for(meter.task, timeout=1.0)

    @pytest.mark.asyncio
    async def test_backgroud_task_running(self):
        meter = S0Meter("Test", self.app_state_mock())
        with pytest.raises(asyncio.exceptions.TimeoutError):
            await asyncio.wait_for(meter.task, timeout=1.0)

    @pytest.mark.asyncio
    async def test_event_handler_exec(self):
        meter = S0Meter("Test", self.app_state_mock())
        with pytest.raises(asyncio.exceptions.TimeoutError):
            await meter.queue.put(mock.Mock(event=mock.Mock(timestamp_ns=1e9)))
            await asyncio.wait_for(meter.task, timeout=1.0)
        assert meter.total == 1

    @pytest.mark.asyncio
    async def test_register_state(self):
        app_state = self.app_state_mock(42)
        meter = S0Meter("Test", app_state)
        app_state.get_state.assert_called_with("Test")
        app_state.register_client.assert_called_with(meter)
        assert meter.total == 42
