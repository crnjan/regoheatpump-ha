"""Tests for the serialx transport adapter."""

import asyncio
from unittest import mock

import pytest
import serialx

from custom_components.regoheatpump.rego600.regoerror import RegoError
from custom_components.regoheatpump.rego600.serial_connection import SerialConnection


@pytest.fixture
def serial() -> mock.MagicMock:
    """Return a mock that matches the real serialx.AsyncSerial API.

    Autospec makes the tests fail if a method is missing in serialx or is
    sync vs. async differently than the code expects.
    """
    port = mock.create_autospec(serialx.AsyncSerial, instance=True)
    port.is_open = True
    return port


@pytest.fixture
def serial_factory(serial: mock.MagicMock):
    """Mock construction of the serialx connection."""
    with mock.patch.object(
        serialx, "async_serial_for_url", autospec=True, return_value=serial
    ) as factory:
        yield factory


async def test_connect_and_close(serial, serial_factory) -> None:
    """Connect opens the port with Rego settings; close closes it."""
    connection = SerialConnection("socket://heat-pump:9500")

    assert not connection.is_connected
    await connection.connect()

    serial_factory.assert_called_once_with("socket://heat-pump:9500", baudrate=19200)
    serial.open.assert_awaited_once()
    assert connection.is_connected

    await connection.close()

    serial.close.assert_awaited_once()
    assert not connection.is_connected


async def test_connect_failure(serial, serial_factory) -> None:
    """Connection failures become RegoError and the transport is aborted."""
    serial.open.side_effect = serialx.SerialException("unavailable")
    connection = SerialConnection("/dev/ttyUSB0")

    with pytest.raises(RegoError, match="Failed to connect"):
        await connection.connect()

    serial.abort.assert_called_once()
    assert not connection.is_connected


async def test_connect_timeout(serial, serial_factory) -> None:
    """A timeout while opening (e.g. ESPHome) becomes RegoError."""
    serial.open.side_effect = TimeoutError
    connection = SerialConnection("esphome://hp.local/?port_name=rego")

    with pytest.raises(RegoError, match="Failed to connect"):
        await connection.connect()


async def test_cancelled_connect_aborts_transport(serial, serial_factory) -> None:
    """A connect cancelled while opening (e.g. by a timeout) aborts the transport."""

    async def stalled_open() -> None:
        await asyncio.sleep(10)

    serial.open.side_effect = stalled_open
    connection = SerialConnection("esphome://hp.local/?port_name=rego")

    with pytest.raises(TimeoutError):
        await asyncio.wait_for(connection.connect(), timeout=0.01)

    serial.abort.assert_called_once()
    assert not connection.is_connected


async def test_dropped_link_reports_disconnected(serial, serial_factory) -> None:
    """A port that closed underneath us is reported as not connected."""
    connection = SerialConnection("/dev/ttyUSB0")
    await connection.connect()

    serial.is_open = False

    assert not connection.is_connected


async def test_reconnect_closes_stale_transport(serial_factory) -> None:
    """Reconnecting after a dropped link closes the old transport first."""
    stale = mock.create_autospec(serialx.AsyncSerial, instance=True)
    fresh = mock.create_autospec(serialx.AsyncSerial, instance=True)
    fresh.is_open = True
    serial_factory.side_effect = [stale, fresh]

    connection = SerialConnection("/dev/ttyUSB0")
    await connection.connect()
    stale.is_open = False

    await connection.connect()

    stale.close.assert_awaited_once()
    fresh.open.assert_awaited_once()
    assert connection.is_connected


async def test_read_write_and_clear(serial, serial_factory) -> None:
    """I/O is delegated to the serial object."""
    serial.readexactly.return_value = b"response"
    serial.read.return_value = b"pending"
    connection = SerialConnection("/dev/ttyUSB0")
    await connection.connect()

    assert await connection.read(8) == b"response"
    await connection.write(b"request")
    assert await connection.clear_reader_buffer(0.1) == b"pending"

    serial.readexactly.assert_awaited_once_with(8)
    serial.write.assert_awaited_once_with(b"request")
    serial.read.assert_awaited_once_with(128)


@pytest.mark.parametrize(
    ("method", "args", "serial_method", "error"),
    [
        ("read", (5,), "readexactly", EOFError()),
        ("read", (5,), "readexactly", serialx.SerialException("gone")),
        ("write", (b"x",), "write", OSError("gone")),
        ("clear_reader_buffer", (0.1,), "read", serialx.SerialException("gone")),
    ],
)
async def test_io_errors_become_rego_error(
    serial, serial_factory, method, args, serial_method, error
) -> None:
    """Transport errors are translated to RegoError."""
    getattr(serial, serial_method).side_effect = error
    connection = SerialConnection("/dev/ttyUSB0")
    await connection.connect()

    with pytest.raises(RegoError):
        await getattr(connection, method)(*args)


@pytest.mark.parametrize("method", ["read", "write", "clear_reader_buffer"])
async def test_io_without_connection_fails(method) -> None:
    """I/O before connect raises RegoError."""
    connection = SerialConnection("/dev/ttyUSB0")
    arg = b"x" if method == "write" else 1

    with pytest.raises(RegoError):
        await getattr(connection, method)(arg)


async def test_clear_reader_buffer_timeout(serial, serial_factory) -> None:
    """An empty buffer (timeout) is normal and returns None."""
    serial.read.side_effect = TimeoutError
    connection = SerialConnection("/dev/ttyUSB0")
    await connection.connect()

    assert await connection.clear_reader_buffer(0.1) is None


async def test_close_failure_aborts(serial, serial_factory) -> None:
    """The transport is aborted if a graceful close fails."""
    serial.close.side_effect = serialx.SerialException("disconnected")
    connection = SerialConnection("/dev/ttyUSB0")
    await connection.connect()

    await connection.close()

    serial.abort.assert_called_once()
    assert not connection.is_connected


async def test_debug_log_hides_encryption_key(serial, serial_factory, caplog) -> None:
    """The connect debug log does not contain the ESPHome API key."""
    caplog.set_level("DEBUG")
    connection = SerialConnection("esphome://hp.local/?port_name=rego&key=SECRET")

    await connection.connect()

    assert "SECRET" not in caplog.text
    assert "key=***" in caplog.text
