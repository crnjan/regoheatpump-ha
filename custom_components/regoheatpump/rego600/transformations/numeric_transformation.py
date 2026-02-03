"""Test."""

from dataclasses import dataclass

from ..last_error import LastError
from ..regoerror import RegoError
from .transformation import Transformation


@dataclass(frozen=True)
class NumericTransformation(Transformation):
    """Test."""

    multiplier: float

    def to_value(self, value: int | LastError | None) -> float | LastError | None:
        """Test."""
        # -483 value marks "absence" of a sensor
        if value is None or value == -483:
            return None
        if isinstance(value, int):
            return round(value * self.multiplier * 1 / self.multiplier) / (
                1 / self.multiplier
            )
        raise RegoError("Unsupported transformation")

    def from_value(self, value: float) -> int:
        """Test."""
        return round(value / self.multiplier)
