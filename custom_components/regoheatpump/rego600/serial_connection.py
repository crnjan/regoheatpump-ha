"""Async serial transport for Rego controller communication."""

import asyncio
import logging

import serialx

from .connection import Connection
from .regoerror import RegoError

try:
    from aioesphomeapi.core import APIConnectionError
except ImportError:
    _COMM_ERRORS = (EOFError, OSError, serialx.SerialException)
else:
    _COMM_ERRORS = (EOFError, OSError, serialx.SerialException, APIConnectionError)

_LOGGER = logging.getLogger(__name__)


class SerialConnection(Connection):
    """Serial-based Connection implementation."""

    def __init__(self, url) -> None:
        """Initialize the serial connection."""
        self.__url = url
        self.__reader = None
        self.__writer = None

    @property
    def is_connected(self) -> bool:
        """Return True if the serial connection is open."""
        return self.__reader is not None

    async def connect(self) -> None:
        """Open the serial connection."""
        _LOGGER.debug("Connecting to '%s'", self.__url)
        try:
            self.__reader, self.__writer = await serialx.open_serial_connection(
                url=self.__url, baudrate=19200
            )
        except _COMM_ERRORS as err:
            raise RegoError("Failed to connect") from err

    async def close(self) -> None:
        """Close the serial connection."""
        writer = self.__writer
        self.__writer = None
        self.__reader = None

        if writer is None:
            return

        try:
            writer.close()
        except _COMM_ERRORS as e:
            _LOGGER.debug("Error while closing writer: %r", e)

        try:
            async with asyncio.timeout(1.0):
                await asyncio.shield(writer.wait_closed())
        except (*_COMM_ERRORS, RuntimeError) as e:
            _LOGGER.debug("Error while waiting for writer to close: %r", e)

    async def read(self, length: int) -> bytes:
        """Read exactly `length` bytes from the controller."""
        if self.__reader is None:
            raise RegoError("Reader is not opened")
        try:
            return await self.__reader.readexactly(length)
        except _COMM_ERRORS as err:
            raise RegoError("Read failed") from err

    async def write(self, buffer: bytes) -> None:
        """Write bytes to the controller."""
        if self.__writer is None:
            raise RegoError("Writer is not opened")
        try:
            self.__writer.write(buffer)
            await self.__writer.drain()
        except _COMM_ERRORS as err:
            raise RegoError("Write failed") from err

    async def clear_reader_buffer(self, timeout: float) -> bytes | None:
        """Drain any pending bytes from the reader."""
        if self.__reader is None:
            raise RegoError("Reader is not opened")
        try:
            return await asyncio.wait_for(self.__reader.read(128), timeout=timeout)
        except TimeoutError:
            return None
        except _COMM_ERRORS as err:
            raise RegoError("Failed to clear reader buffer") from err
