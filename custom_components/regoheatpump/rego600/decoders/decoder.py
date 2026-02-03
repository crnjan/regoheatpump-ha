"""Test."""

from abc import ABC, abstractmethod

from ..last_error import LastError


class Decoder(ABC):
    """Test."""

    @property
    @abstractmethod
    def length(self) -> int:
        """Test."""

    @abstractmethod
    def decode(self, buffer: bytes) -> int | LastError | None:
        """Test."""
