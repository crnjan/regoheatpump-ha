"""Client for reading and writing Rego 600 registers."""

import asyncio
from collections.abc import Callable
import logging
import time
from typing import Self

from .connection import Connection
from .decoders import Decoder
from .last_error import LastError
from .register import Register
from .rego_type import RegoType
from .regoerror import RegoError, RegoProtocolError
from .repositories import RegisterRepository
from .serial_connection import SerialConnection
from .transformations import Transformation

_LOGGER = logging.getLogger(__name__)
_RETRIES: int = 3

# After a request fails all its retries, further requests fail immediately for
# this long instead of each waiting for its own timeouts and retries.
OFFLINE_BACKOFF: float = 30.0


class HeatPump:
    """High-level API for Rego controller communication."""

    def __init__(
        self,
        connection: Connection,
        rego_type: RegoType,
        clock: Callable[[], float] = time.monotonic,
    ) -> None:
        """Initialize the client with a transport connection."""
        self.__connection = connection
        self.__lock = asyncio.Lock()
        self.__rego_type = rego_type
        self.__clock = clock
        self.__offline_until: float | None = None

    @classmethod
    def connect(cls, url: str, rego_type: RegoType) -> Self:
        """Create a client for the given serial URL."""
        connection = SerialConnection(url)
        return cls(connection, rego_type)

    @property
    def is_offline(self) -> bool:
        """Return True if the heat pump is considered unreachable."""
        return self.__offline_until is not None

    @property
    def registers(self) -> list[Register]:
        """Return the register database."""
        return RegisterRepository.registers(self.__rego_type)

    async def dispose(self):
        """Close the underlying connection."""
        await self.__connection.close()

    async def verify(self, retry: int = _RETRIES) -> None:
        """Verify the controller version."""
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
        """Read a register value."""
        return await self.__send(*register.read(), retry)

    async def write(
        self, register: Register, value: float, retry: int = _RETRIES
    ) -> None:
        """Write a register value."""
        await self.__send(*register.write(value), retry)

    async def __send(
        self,
        payload: bytes,
        decoder: Decoder,
        transformation: Transformation,
        retry: int,
    ) -> float | LastError | None:
        async with self.__lock:
            if (
                self.__offline_until is not None
                and self.__clock() < self.__offline_until
            ):
                raise RegoError("Heat pump is offline")

            try:
                value = await self.__synchronised_send(
                    payload, decoder, transformation, retry
                )
            except RegoProtocolError as err:
                # The controller answered, just not as expected: it is reachable,
                # so only this request fails.
                self.__mark_online()
                _LOGGER.warning(
                    "Unexpected response from heat pump to request '%s': %s",
                    payload.hex(),
                    err,
                )
                raise
            except (TimeoutError, RegoError) as err:
                if not self.is_offline:
                    _LOGGER.warning(
                        "Heat pump is not responding, retrying in %d seconds: %r",
                        OFFLINE_BACKOFF,
                        err,
                    )
                self.__offline_until = self.__clock() + OFFLINE_BACKOFF
                raise

            self.__mark_online()
            return value

    def __mark_online(self) -> None:
        if self.is_offline:
            _LOGGER.info("Heat pump is responding again")
            self.__offline_until = None

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
                await asyncio.wait_for(self.__connection.connect(), timeout=2)

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

            async with asyncio.timeout(2):
                _LOGGER.debug("Sending '%s'", payload.hex())
                await self.__connection.write(payload)
                response = await self.__connection.read(decoder.length)
                _LOGGER.debug("Received %s", response.hex())
            return transformation.to_value(decoder.decode(response))

        except (TimeoutError, RegoError) as e:
            _LOGGER.debug("Sending '%s' failed due %r", payload.hex(), e)
            await self.__connection.close()
            if retry > 0:
                _LOGGER.debug("Retrying, retry=%d", retry)
                await asyncio.sleep(0.2)
                return await self.__synchronised_send(
                    payload, decoder, transformation, retry - 1, is_reconnect=True
                )
            raise
