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
        version = await self.__send(*register.read(), retry)
        if version != 600:
            await self.__connection.close()
            raise RegoError(f"Invalid rego version received {version}")
        _LOGGER.debug("Connected to Rego version %s", version)

    async def read(
        self, register: Register, retry: int = _RETRIES
    ) -> float | LastError | None:
        """Test."""
        return await self.__send(*register.read(), retry)

    async def write(
        self, register: Register, value: float, retry: int = _RETRIES
    ) -> None:
        """Test."""
        transformed = register.transformation.from_value(value)
        await self.__send(*register.write(transformed), retry)

    async def __send(
        self,
        payload: bytes,
        decoder: Decoder,
        transformation: Transformation,
        retry: int,
    ) -> float | LastError | None:
        async with self.__lock:
            return await self.__synchronised_send(
                payload, decoder, transformation, retry
            )

    async def __synchronised_send(
        self,
        payload: bytes,
        decoder: Decoder,
        transformation: Transformation,
        retry: int,
        is_reconnect: bool = False,
    ) -> float | LastError | None:
        try:
            if not self.__connection.is_connected:
                _LOGGER.debug("Not connected, connecting")
                await self.__connection.connect()
                _LOGGER.debug("Connected")

            # Protocol is request driven so there should be no data available before sending
            # a command to the heat pump. After reconnect give more time to read any potential
            # leftovers from previous response.
            if buffer := await self.__connection.clear_reader_buffer(
                timeout=1 if is_reconnect else 0.08
            ):
                _LOGGER.debug(
                    "There are %d unexpected bytes available. Skipping '%s'",
                    len(buffer),
                    buffer.hex(),
                )

            async with asyncio_timeout(2):
                _LOGGER.debug("Sending '%s'", payload.hex())
                await self.__connection.write(payload)
                response = await self.__connection.read(decoder.length)
                _LOGGER.debug("Received %s", response.hex())
            return transformation.to_value(decoder.decode(response))

        except (OSError, RegoError) as e:
            _LOGGER.debug("Sending '%s' failed due %s", payload.hex(), repr({e}))
            await self.__connection.close()
            if retry > 0:
                _LOGGER.debug("Retrying, retry=%d", retry)
                await asyncio.sleep(0.2)
                return await self.__synchronised_send(
                    payload, decoder, transformation, retry - 1, is_reconnect=True
                )
            raise
