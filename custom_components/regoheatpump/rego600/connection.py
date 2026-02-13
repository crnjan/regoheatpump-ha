"""Abstract transport interface for Rego communication."""

from abc import ABC, abstractmethod


class Connection(ABC):
    """Transport interface used by the heat pump client."""

    @property
    @abstractmethod
    def is_connected(self) -> bool:
        """Return True if the transport is connected."""

    @abstractmethod
    async def connect(self) -> None:
        """Open the transport connection."""

    @abstractmethod
    async def close(self) -> None:
        """Close the transport connection."""

    @abstractmethod
    async def read(self, length: int) -> bytes:
        """Read exactly `length` bytes."""

    @abstractmethod
    async def write(self, buffer: bytes) -> None:
        """Write bytes to the transport."""

    @abstractmethod
    async def clear_reader_buffer(self, timeout: float) -> bytes | None:
        """Drain any pending bytes from the reader."""
