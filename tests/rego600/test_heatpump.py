import asyncio
import pytest

from unittest import mock
from unittest.mock import PropertyMock, call


from rego600 import HeatPump, RegoError
from rego600.connection import Connection
from rego600.identifiers import Identifiers
from rego600.register_factory import RegisterFactory

_REGISTER = RegisterFactory.system_temperature(Identifiers.SENSOR_VALUES_INDOOR, 0x020D)


@pytest.mark.asyncio
async def test_connect_fails():
    connection = mock.create_autospec(Connection)
    type(connection).is_connected = PropertyMock(return_value=False)
    connection.connect.side_effect = OSError
    hp = HeatPump(connection)
    with pytest.raises(OSError):
        await hp.read(_REGISTER, retry=0)
    connection.close.assert_called_once()


@pytest.mark.asyncio
@pytest.mark.parametrize("readReturnValue", [b"\xca\xfe\xba\xbe", b"\x01\x00\x00\x00\x00", b""])
async def test_verify_fails(readReturnValue):
    connection = mock.create_autospec(Connection)
    type(connection).is_connected = PropertyMock(return_value=False)
    connection.read.return_value = readReturnValue
    hp = HeatPump(connection)
    with pytest.raises(RegoError):
        await hp.verify(retry=0)
    connection.connect.assert_called_once()
    connection.close.assert_called_once()


@pytest.mark.asyncio
async def test_verify():
    connection = mock.create_autospec(Connection)
    type(connection).is_connected = PropertyMock(return_value=False)
    connection.read.return_value = b"\x01\x00\x04\x58\x5c"
    hp = HeatPump(connection)
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
    connection.read.side_effect = looongRead
    hp = HeatPump(connection)
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
    connection.read.side_effect = read
    hp = HeatPump(connection)
    assert await hp.read(_REGISTER, retry=1) == 0.9
    assert len(connection.connect.mock_calls) == 2
    connection.close.assert_called_once()


@pytest.mark.asyncio
async def test_read():
    connection = mock.create_autospec(Connection)
    type(connection).is_connected = PropertyMock(side_effect=lambda: len(connection.connect.mock_calls) > 0)
    connection.read.side_effect = [
        b"\x01\x00\x00\x08\x08",
        b"\x01\x00\x00\x0a\x0a",
    ]
    hp = HeatPump(connection)
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
    connection.read.return_value = b"\x01"
    hp = HeatPump(connection)
    await hp.write(_REGISTER, 1.2)
    connection.connect.assert_not_called()
    connection.write.assert_called_once_with(b"\x81\x03\x00\x04\x0d\x00\x00\x0c\x05")
    connection.close.assert_not_called()
    await hp.dispose()
    connection.close.assert_called_once()
