"""Test."""

from abc import ABC, abstractmethod


class Connection(ABC):
    """Test."""

    @property
    @abstractmethod
    def is_connected(self) -> bool:
        """Test."""

    @abstractmethod
    async def connect(self) -> None:
        """Test."""

    @abstractmethod
    async def close(self) -> None:
        """Test."""

    @abstractmethod
    async def read(self, length: int) -> bytes:
        """Test."""

    @abstractmethod
    async def write(self, buffer: bytes) -> None:
        """Test."""
