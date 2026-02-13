"""Decoder interface for Rego responses."""

from abc import ABC, abstractmethod

from ..last_error import LastError


class Decoder(ABC):
    """Decode a response frame into a value."""

    @property
    @abstractmethod
    def length(self) -> int:
        """Return the expected response length."""

    @abstractmethod
    def decode(self, buffer: bytes) -> int | LastError | None:
        """Decode the response buffer."""
