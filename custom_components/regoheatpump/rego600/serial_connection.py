"""Test."""

import serial_asyncio_fast as serial_asyncio

from .connection import Connection
from .regoerror import RegoError


class SerialConnection(Connection):
    """Test."""

    def __init__(self, url) -> None:
        """Test."""
        self.__url = url
        self.__reader = None
        self.__writter = None

    @property
    def is_connected(self) -> bool:
        """Test."""
        return self.__reader is not None

    async def connect(self) -> None:
        """Test."""
        self.__reader, self.__writter = await serial_asyncio.open_serial_connection(
            url=self.__url, baudrate=19200
        )

    async def close(self) -> None:
        """Test."""
        if self.__writter is not None:
            self.__writter.close()
            await self.__writter.wait_closed()
        self.__writter = None
        self.__reader = None

    async def read(self, length: int) -> bytes:
        """Test."""
        if self.__reader is None:
            raise RegoError("Reader is not opened")
        return await self.__reader.readexactly(length)

    async def write(self, buffer: bytes) -> None:
        """Test."""
        if self.__writter is None:
            raise RegoError("Writter is not opened")
        self.__writter.write(buffer)
        await self.__writter.drain()
