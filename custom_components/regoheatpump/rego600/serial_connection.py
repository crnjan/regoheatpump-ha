"""Async serial transport for Rego controller communication."""

from __future__ import annotations

import asyncio
import logging

import serialx

from .connection import Connection
from .redact import redact_url
from .regoerror import RegoError

_LOGGER = logging.getLogger(__name__)


class SerialConnection(Connection):
    """Serial-based Connection implementation."""

    def __init__(self, url: str) -> None:
        """Initialize the serial connection."""
        self.__url = url
        self.__serial: serialx.AsyncSerial | None = None

    @property
    def is_connected(self) -> bool:
        """Return True if the serial connection is open."""
        return self.__serial is not None and self.__serial.is_open

    async def connect(self) -> None:
        """Open the serial connection."""
        # A dropped link leaves a stale (no longer open) transport behind
        await self.close()

        _LOGGER.debug("Connecting to '%s'", redact_url(self.__url))
        serial = serialx.async_serial_for_url(self.__url, baudrate=19200)
        try:
            await serial.open()
        except (OSError, serialx.SerialException) as err:
            serial.abort()
            raise RegoError("Failed to connect") from err
        except asyncio.CancelledError:
            # E.g. the caller's connect timeout. The transport is not stored yet,
            # so close() could not clean it up later.
            serial.abort()
            raise
        self.__serial = serial

    async def close(self) -> None:
        """Close the serial connection."""
        serial = self.__serial
        self.__serial = None

        if serial is None:
            return

        try:
            async with asyncio.timeout(1.0):
                await asyncio.shield(serial.close())
        except (TimeoutError, OSError, serialx.SerialException, RuntimeError) as err:
            serial.abort()
            _LOGGER.debug("Error while closing connection: %r", err)

    async def read(self, length: int) -> bytes:
        """Read exactly `length` bytes from the controller."""
        if self.__serial is None:
            raise RegoError("Reader is not opened")
        try:
            return await self.__serial.readexactly(length)
        except (EOFError, OSError, serialx.SerialException) as err:
            raise RegoError("Read failed") from err

    async def write(self, buffer: bytes) -> None:
        """Write bytes to the controller."""
        if self.__serial is None:
            raise RegoError("Writer is not opened")
        try:
            await self.__serial.write(buffer)
        except (OSError, serialx.SerialException) as err:
            raise RegoError("Write failed") from err

    async def clear_reader_buffer(self, timeout: float) -> bytes | None:
        """Drain any pending bytes from the reader."""
        if self.__serial is None:
            raise RegoError("Reader is not opened")
        try:
            return await asyncio.wait_for(self.__serial.read(128), timeout=timeout)
        except TimeoutError:
            return None
        except (EOFError, OSError, serialx.SerialException) as err:
            raise RegoError("Failed to clear reader buffer") from err
