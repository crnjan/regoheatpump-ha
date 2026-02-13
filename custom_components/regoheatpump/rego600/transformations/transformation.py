"""Transformation interface for raw register values."""

from abc import ABC, abstractmethod

from ..last_error import LastError


class Transformation(ABC):
    """Convert raw decoded values to native values and back."""

    @abstractmethod
    def to_value(self, value: int | LastError | None) -> float | LastError | None:
        """Convert raw value to a native value."""

    @abstractmethod
    def from_value(self, value: float) -> int:
        """Convert native value to raw register format."""
