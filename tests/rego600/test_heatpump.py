import asyncio
import pytest

from unittest import mock
from unittest.mock import PropertyMock, call


from custom_components.regoheatpump.rego600 import HeatPump, RegoError, RegoProtocolError, RegoType
from custom_components.regoheatpump.rego600.heatpump import OFFLINE_BACKOFF
from custom_components.regoheatpump.rego600.connection import Connection
from custom_components.regoheatpump.rego600.identifiers import Identifiers
from custom_components.regoheatpump.rego600.repositories.register_factory import RegisterFactory

_REGISTER = RegisterFactory.system_temperature(Identifiers.SENSOR_VALUES_INDOOR, 0x020D)


@pytest.mark.asyncio
async def test_connect_fails():
    connection = mock.create_autospec(Connection)
    type(connection).is_connected = PropertyMock(return_value=False)
    connection.connect.side_effect = RegoError
    hp = HeatPump(connection, RegoType.REGO637)
    with pytest.raises(RegoError):
        await hp.read(_REGISTER, retry=0)
    connection.close.assert_called_once()


@pytest.mark.asyncio
@pytest.mark.parametrize("readReturnValue", [b"\xca\xfe\xba\xbe", b"\x01\x00\x00\x00\x00", b""])
async def test_verify_fails(readReturnValue):
    connection = mock.create_autospec(Connection)
    type(connection).is_connected = PropertyMock(return_value=False)
    connection.clear_reader_buffer.return_value = None
    connection.read.return_value = readReturnValue
    hp = HeatPump(connection, RegoType.REGO637)
    with pytest.raises(RegoError):
        await hp.verify(retry=0)
    connection.connect.assert_called_once()
    connection.close.assert_called_once()


@pytest.mark.asyncio
async def test_verify():
    connection = mock.create_autospec(Connection)
    type(connection).is_connected = PropertyMock(return_value=False)
    connection.clear_reader_buffer.return_value = None
    connection.read.return_value = b"\x01\x00\x04\x58\x5c"
    hp = HeatPump(connection, RegoType.REGO637)
    await hp.verify()
    connection.write.assert_called_once_with(b"\x81\x7f\x00\x00\x00\x00\x00\x00\x00")
    connection.connect.assert_called_once()
    connection.close.assert_not_called()
    await hp.dispose()
    connection.close.assert_called_once()


@pytest.mark.asyncio
async def test_waiting_for_response_should_timeout():
    async def looongRead(length: int):
        await asyncio.sleep(5)

    connection = mock.create_autospec(Connection)
    type(connection).is_connected = PropertyMock(return_value=False)
    connection.clear_reader_buffer.return_value = None
    connection.read.side_effect = looongRead
    hp = HeatPump(connection, RegoType.REGO637)
    with pytest.raises(TimeoutError):
        await hp.read(_REGISTER, retry=0)
    connection.connect.assert_called_once()
    connection.close.assert_called_once()


@pytest.mark.asyncio
async def test_waiting_for_response_should_timeout_and_retry():
    connection = mock.create_autospec(Connection)

    async def read(length: int):
        if len(connection.read.mock_calls) > 1:
            return b"\x01\x00\x00\x09\x09"
        await asyncio.sleep(5)

    type(connection).is_connected = PropertyMock(return_value=False)
    connection.clear_reader_buffer.return_value = None
    connection.read.side_effect = read
    hp = HeatPump(connection, RegoType.REGO637)
    assert await hp.read(_REGISTER, retry=1) == 0.9
    assert len(connection.connect.mock_calls) == 2
    connection.close.assert_called_once()


@pytest.mark.asyncio
async def test_read():
    connection = mock.create_autospec(Connection)
    type(connection).is_connected = PropertyMock(side_effect=lambda: len(connection.connect.mock_calls) > 0)
    connection.clear_reader_buffer.return_value = None
    connection.read.side_effect = [
        b"\x01\x00\x00\x08\x08",
        b"\x01\x00\x00\x0a\x0a",
    ]
    hp = HeatPump(connection, RegoType.REGO637)
    assert await hp.read(_REGISTER) == 0.8
    assert await hp.read(_REGISTER) == 1
    connection.connect.assert_called_once()
    connection.write.assert_has_calls(
        [
            call(b"\x81\x02\x00\x04\x0d\x00\x00\x00\x09"),
            call(b"\x81\x02\x00\x04\x0d\x00\x00\x00\x09"),
        ],
    )
    connection.close.assert_not_called()
    await hp.dispose()
    connection.close.assert_called_once()


@pytest.mark.asyncio
async def test_write():
    connection = mock.create_autospec(Connection)
    type(connection).is_connected = PropertyMock(return_value=True)
    connection.clear_reader_buffer.return_value = None
    connection.read.return_value = b"\x01"
    hp = HeatPump(connection, RegoType.REGO637)
    await hp.write(_REGISTER, 1.2)
    connection.connect.assert_not_called()
    connection.write.assert_called_once_with(b"\x81\x03\x00\x04\x0d\x00\x00\x0c\x05")
    connection.close.assert_not_called()
    await hp.dispose()
    connection.close.assert_called_once()


class _FakeClock:
    """Manually advanced monotonic clock."""

    def __init__(self) -> None:
        self.now = 1000.0

    def __call__(self) -> float:
        return self.now


def _offline_connection():
    connection = mock.create_autospec(Connection)
    type(connection).is_connected = PropertyMock(return_value=False)
    connection.connect.side_effect = RegoError("unreachable")
    return connection


@pytest.mark.asyncio
async def test_failure_marks_offline_and_fails_fast(caplog):
    """After retries are exhausted, further requests fail without I/O."""
    clock = _FakeClock()
    connection = _offline_connection()
    hp = HeatPump(connection, RegoType.REGO637, clock=clock)

    with pytest.raises(RegoError, match="unreachable"):
        await hp.read(_REGISTER, retry=0)
    assert hp.is_offline
    assert "Heat pump is not responding" in caplog.text

    connection.connect.reset_mock()
    with pytest.raises(RegoError, match="offline"):
        await hp.read(_REGISTER)
    with pytest.raises(RegoError, match="offline"):
        await hp.write(_REGISTER, 21.0)
    connection.connect.assert_not_called()


@pytest.mark.asyncio
async def test_probe_after_backoff_recovers(caplog):
    """After the backoff a request is tried again and clears the offline state."""
    clock = _FakeClock()
    connection = _offline_connection()
    hp = HeatPump(connection, RegoType.REGO637, clock=clock)

    with pytest.raises(RegoError):
        await hp.read(_REGISTER, retry=0)

    connection.connect.side_effect = None
    connection.clear_reader_buffer.return_value = None
    connection.read.return_value = b"\x01\x00\x00\x09\x09"
    clock.now += OFFLINE_BACKOFF

    assert await hp.read(_REGISTER, retry=0) == 0.9
    assert not hp.is_offline
    assert "Heat pump is responding again" in caplog.text


@pytest.mark.asyncio
async def test_failed_probe_extends_backoff_and_logs_once(caplog):
    """A failed probe stays offline for another backoff without logging again."""
    clock = _FakeClock()
    connection = _offline_connection()
    hp = HeatPump(connection, RegoType.REGO637, clock=clock)

    with pytest.raises(RegoError):
        await hp.read(_REGISTER, retry=0)

    clock.now += OFFLINE_BACKOFF
    with pytest.raises(RegoError, match="unreachable"):
        await hp.read(_REGISTER, retry=0)

    clock.now += OFFLINE_BACKOFF - 1
    with pytest.raises(RegoError, match="offline"):
        await hp.read(_REGISTER, retry=0)

    assert caplog.text.count("Heat pump is not responding") == 1


@pytest.mark.asyncio
async def test_unexpected_response_does_not_mark_offline(caplog):
    """A responding controller with a bad response fails only that request."""
    clock = _FakeClock()
    connection = mock.create_autospec(Connection)
    type(connection).is_connected = PropertyMock(return_value=False)
    connection.clear_reader_buffer.return_value = None
    connection.read.return_value = b"\x01\x00\x00\x09\x00"  # bad CRC
    hp = HeatPump(connection, RegoType.REGO637, clock=clock)

    with pytest.raises(RegoProtocolError, match="crc"):
        await hp.read(_REGISTER, retry=1)

    assert connection.read.call_count == 2  # still retried
    assert not hp.is_offline
    assert "not responding" not in caplog.text

    connection.read.return_value = b"\x01\x00\x00\x09\x09"
    assert await hp.read(_REGISTER, retry=0) == 0.9


@pytest.mark.asyncio
async def test_unexpected_response_after_backoff_marks_online(caplog):
    """Any response after the backoff shows the controller is reachable again."""
    clock = _FakeClock()
    connection = _offline_connection()
    hp = HeatPump(connection, RegoType.REGO637, clock=clock)

    with pytest.raises(RegoError):
        await hp.read(_REGISTER, retry=0)
    assert hp.is_offline

    connection.connect.side_effect = None
    connection.clear_reader_buffer.return_value = None
    connection.read.return_value = b"\x02\x00\x00\x09\x09"  # bad header
    clock.now += OFFLINE_BACKOFF

    with pytest.raises(RegoProtocolError, match="header"):
        await hp.read(_REGISTER, retry=0)
    assert not hp.is_offline
    assert "Heat pump is responding again" in caplog.text
