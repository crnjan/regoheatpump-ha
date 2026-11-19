import asyncio
from datetime import UTC, datetime, timedelta
from unittest import mock
from unittest.mock import PropertyMock, call

import pytest

from custom_components.regoheatpump.rego600 import (
    HeatPump,
    RegoError,
    RegoProtocolError,
    RegoType,
)
from custom_components.regoheatpump.rego600.connection import Connection
from custom_components.regoheatpump.rego600.heatpump import OFFLINE_BACKOFF
from custom_components.regoheatpump.rego600.identifiers import Identifiers
from custom_components.regoheatpump.rego600.repositories.register_factory import (
    RegisterFactory,
)

_REGISTER = RegisterFactory.system_temperature(Identifiers.SENSOR_VALUES_INDOOR, 0x020D)
_WRITABLE_REGISTER = RegisterFactory.system_unitless(
    Identifiers.SETTINGS_HEAT_CURVE, 0x0000, is_writable=True
)


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
@pytest.mark.parametrize(
    "readReturnValue", [b"\xca\xfe\xba\xbe", b"\x01\x00\x00\x00\x00", b""]
)
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
    type(connection).is_connected = PropertyMock(
        side_effect=lambda: len(connection.connect.mock_calls) > 0
    )
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
    await hp.write(_WRITABLE_REGISTER, 1.2)
    connection.connect.assert_not_called()
    connection.write.assert_called_once_with(b"\x81\x03\x00\x00\x00\x00\x00\x0c\x0c")
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
        await hp.write(_WRITABLE_REGISTER, 2.1)
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


@pytest.mark.asyncio
async def test_unparsable_payload_does_not_mark_offline():
    """A frame that passes CRC but cannot be decoded fails only that request."""
    connection = mock.create_autospec(Connection)
    type(connection).is_connected = PropertyMock(return_value=False)
    connection.clear_reader_buffer.return_value = None
    # Valid header + checksum, but timestamp "000000 00:00:00" (month 0)
    body = [0x00, 0x0B] + [n for c in b"000000 00:00:00" for n in (c >> 4, c & 0x0F)]
    body += [0] * (40 - len(body))
    crc = 0
    for value in body:
        crc ^= value
    connection.read.return_value = bytes([0x01, *body, crc])
    hp = HeatPump(connection, RegoType.REGO637, clock=_FakeClock())

    last_error = RegisterFactory.last_error(Identifiers.LAST_ERROR)
    with pytest.raises(RegoProtocolError, match="Invalid payload"):
        await hp.read(last_error, retry=0)
    assert not hp.is_offline


@pytest.mark.asyncio
async def test_unexpected_response_is_logged(caplog):
    """An unexpected response is logged with the request and the error."""
    connection = mock.create_autospec(Connection)
    type(connection).is_connected = PropertyMock(return_value=False)
    connection.clear_reader_buffer.return_value = None
    connection.read.return_value = b"\x01\x00\x00\x09\x00"  # bad CRC
    hp = HeatPump(connection, RegoType.REGO637, clock=_FakeClock())

    with pytest.raises(RegoProtocolError):
        await hp.read(_REGISTER, retry=0)

    warnings = [r for r in caplog.records if r.levelname == "WARNING"]
    assert len(warnings) == 1
    message = warnings[0].getMessage()
    assert "Unexpected response from heat pump to request" in message
    assert _REGISTER.read_commands()[0].payload.hex() in message
    assert "crc" in message


@pytest.mark.parametrize(
    ("rego_type", "only_on_637"),
    [(RegoType.REGO636, False), (RegoType.REGO637, True)],
)
def test_registers_match_controller_type(rego_type, only_on_637):
    hp = HeatPump(mock.create_autospec(Connection), rego_type)

    assert (
        Identifiers.SENSOR_VALUES_EXTERNAL_HOTWATER
        in {register.identifier for register in hp.registers}
    ) is only_on_637


def _frame(value: int) -> bytes:
    """A 5 byte answer carrying a 16-bit value."""
    body = bytes([(value >> 14) & 0x7F, (value >> 7) & 0x7F, value & 0x7F])
    return b"\x01" + body + bytes([body[0] ^ body[1] ^ body[2]])


def _front_panel_read(address: int) -> bytes:
    return bytes([0x81, 0x00, 0x00, 0x00, address, 0x00, 0x00, 0x00, address])


# second, minute, hour, date, month, year of "261117 13:31:02", as BCD
_CLOCK = {0x01: 0x02, 0x02: 0x31, 0x03: 0x13, 0x04: 0x17, 0x05: 0x11, 0x07: 0x26}


@pytest.mark.asyncio
async def test_read_composite_register_reads_its_parts_and_combines_them():
    connection = mock.create_autospec(Connection)
    type(connection).is_connected = PropertyMock(return_value=True)
    connection.clear_reader_buffer.return_value = None
    connection.read.side_effect = [_frame(value) for value in _CLOCK.values()]
    hp = HeatPump(connection, RegoType.REGO637)
    register = RegisterFactory.real_time_clock(Identifiers.REAL_TIME_CLOCK)

    assert await hp.read(register) == datetime(2026, 11, 17, 13, 31, 2)
    # Seconds first, weekday (register 6) not read
    assert connection.write.call_args_list == [
        call(_front_panel_read(address)) for address in (1, 2, 3, 4, 5, 7)
    ]


@pytest.mark.asyncio
async def test_composite_read_is_not_interleaved_with_other_requests():
    connection = mock.create_autospec(Connection)
    type(connection).is_connected = PropertyMock(return_value=True)
    connection.clear_reader_buffer.return_value = None
    written: list[bytes] = []

    async def write(payload: bytes) -> None:
        written.append(payload)

    async def read(length: int) -> bytes:
        await asyncio.sleep(0)  # let other tasks run between requests
        payload = written[-1]
        if payload[1] == 0x00:
            return _frame(_CLOCK[payload[4]])
        return b"\x01\x00\x00\x08\x08"

    connection.write.side_effect = write
    connection.read.side_effect = read
    hp = HeatPump(connection, RegoType.REGO637)
    clock = RegisterFactory.real_time_clock(Identifiers.REAL_TIME_CLOCK)

    await asyncio.gather(hp.read(clock), hp.read(_REGISTER), hp.read(_REGISTER))

    clock_reads = [i for i, payload in enumerate(written) if payload[1] == 0x00]
    assert len(clock_reads) == 6
    assert clock_reads == list(range(clock_reads[0], clock_reads[0] + 6))


@pytest.mark.asyncio
async def test_invalid_part_value_fails_the_whole_read():
    connection = mock.create_autospec(Connection)
    type(connection).is_connected = PropertyMock(return_value=True)
    connection.clear_reader_buffer.return_value = None
    # Minutes 0x5A is not BCD
    connection.read.side_effect = [_frame(0x02), _frame(0x5A)] * 10
    hp = HeatPump(connection, RegoType.REGO637)
    register = RegisterFactory.real_time_clock(Identifiers.REAL_TIME_CLOCK)

    with pytest.raises(RegoProtocolError):
        await hp.read(register, retry=0)


@pytest.mark.asyncio
async def test_read_timed_starts_the_clock_once_the_lock_is_held():
    connection = mock.create_autospec(Connection)
    type(connection).is_connected = PropertyMock(return_value=True)
    connection.clear_reader_buffer.return_value = None
    written: list[bytes] = []

    async def write(payload: bytes) -> None:
        written.append(payload)

    async def read(length: int) -> bytes:
        payload = written[-1]
        if payload[1] == 0x00:
            return _frame(_CLOCK[payload[4]])
        await asyncio.sleep(0.3)  # a slow request holding the lock
        return b"\x01\x00\x00\x08\x08"

    connection.write.side_effect = write
    connection.read.side_effect = read
    hp = HeatPump(connection, RegoType.REGO637)
    clock = RegisterFactory.real_time_clock(Identifiers.REAL_TIME_CLOCK)

    before = datetime.now(UTC)
    slow = asyncio.ensure_future(hp.read(_REGISTER))
    await asyncio.sleep(0)  # the slow request takes the lock first
    reading = await hp.read_timed(clock)
    await slow

    assert reading.value == datetime(2026, 11, 17, 13, 31, 2)
    assert reading.started_at.tzinfo is UTC
    # Waiting for the slow request is not part of the reading
    assert reading.started_at - before >= timedelta(seconds=0.25)


@pytest.mark.asyncio
async def test_read_returns_the_value_of_read_timed():
    connection = mock.create_autospec(Connection)
    type(connection).is_connected = PropertyMock(return_value=True)
    connection.clear_reader_buffer.return_value = None
    connection.read.return_value = b"\x01\x00\x00\x08\x08"
    hp = HeatPump(connection, RegoType.REGO637)

    assert await hp.read(_REGISTER) == 0.8
