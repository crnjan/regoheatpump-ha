"""Provides TODO."""

import asyncio
from asyncio import timeout as asyncio_timeout
import logging
from typing import Self

from .connection import Connection
from .decoders import Decoder
from .last_error import LastError
from .register import Register
from .register_repository import RegisterRepository
from .regoerror import RegoError
from .serial_connection import SerialConnection
from .transformations import Transformation

_LOGGER = logging.getLogger(__name__)
_RETRIES: int = 3


class HeatPump:
    """Test."""

    def __init__(self, connection: Connection) -> None:
        """Test."""
        self.__connection = connection
        self.__lock = asyncio.Lock()

    @classmethod
    def connect(cls, url: str) -> Self:
        """Test."""
        connection = SerialConnection(url)
        return cls(connection)

    @property
    def registers(self) -> list[Register]:
        """Return the register database."""
        return RegisterRepository.registers()

    async def dispose(self):
        """Test."""
        await self.__connection.close()

    async def verify(self, retry: int = _RETRIES) -> None:
        """Test."""
        _LOGGER.debug("Reading Rego device version")
        register = RegisterRepository.version()
        async with self.__lock:
            version = await self.__send(*register.read(), retry)
            if version != 600:
                await self.__connection.close()
                raise RegoError(f"Invalid rego version received {version}")
        _LOGGER.debug("Connected to Rego version %s", version)

    async def read(
        self, register: Register, retry: int = _RETRIES
    ) -> float | LastError | None:
        """Test."""
        async with self.__lock:
            return await self.__send(*register.read(), retry)

    async def write(
        self, register: Register, value: float, retry: int = _RETRIES
    ) -> None:
        """Test."""
        transformed = register.transformation.from_value(value)
        async with self.__lock:
            await self.__send(*register.write(transformed), retry)

    async def __send(
        self,
        payload: bytes,
        decoder: Decoder,
        transformation: Transformation,
        retry: int,
    ) -> float | LastError | None:
        try:
            if not self.__connection.is_connected:
                _LOGGER.debug("Not connected, connecting")
                await self.__connection.connect()
                _LOGGER.debug("Connected")

            # Give heat pump some time between commands. Feeding commands too quickly
            # might cause heat pump not to respond.
            await asyncio.sleep(0.02)

            async with asyncio_timeout(2):
                _LOGGER.debug("Sending '%s'", payload.hex())
                await self.__connection.write(payload)
                _LOGGER.debug("Send, waiting for response")
                response = await self.__connection.read(decoder.length)
                _LOGGER.debug("Received %s", response.hex())
            return transformation.to_value(decoder.decode(response))

        except (OSError, RegoError) as e:
            _LOGGER.debug("Sending '%s' failed due %s", payload.hex(), repr({e}))
            await self.__connection.close()
            if retry > 0:
                _LOGGER.debug("Retrying, retry=%d", retry)
                await asyncio.sleep(0.2)
                return await self.__send(payload, decoder, transformation, retry - 1)
            raise
