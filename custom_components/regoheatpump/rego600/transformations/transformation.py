"""Test."""

from abc import ABC, abstractmethod

from ..last_error import LastError


class Transformation(ABC):
    """Test."""

    @abstractmethod
    def to_value(self, value: int | LastError | None) -> float | LastError | None:
        """Test."""

    @abstractmethod
    def from_value(self, value: float) -> int:
        """Test."""
