"""Async serial transport for Rego controller communication."""

import asyncio

import serial_asyncio_fast as serial_asyncio

from .connection import Connection
from .regoerror import RegoError


class SerialConnection(Connection):
    """Serial-based Connection implementation."""

    def __init__(self, url) -> None:
        """Initialize the serial connection."""
        self.__url = url
        self.__reader = None
        self.__writter = None

    @property
    def is_connected(self) -> bool:
        """Return True if the serial connection is open."""
        return self.__reader is not None

    async def connect(self) -> None:
        """Open the serial connection."""
        self.__reader, self.__writter = await serial_asyncio.open_serial_connection(
            url=self.__url, baudrate=19200
        )

    async def close(self) -> None:
        """Close the serial connection."""
        if self.__writter is not None:
            self.__writter.close()
            await self.__writter.wait_closed()
        self.__writter = None
        self.__reader = None

    async def read(self, length: int) -> bytes:
        """Read exactly `length` bytes from the controller."""
        if self.__reader is None:
            raise RegoError("Reader is not opened")
        return await self.__reader.readexactly(length)

    async def write(self, buffer: bytes) -> None:
        """Write bytes to the controller."""
        if self.__writter is None:
            raise RegoError("Writter is not opened")
        self.__writter.write(buffer)
        await self.__writter.drain()

    async def clear_reader_buffer(self, timeout: float) -> bytes | None:
        """Drain any pending bytes from the reader."""
        if self.__reader is None:
            raise RegoError("Reader is not opened")
        try:
            return await asyncio.wait_for(self.__reader.read(128), timeout=timeout)
        except TimeoutError:
            return None
