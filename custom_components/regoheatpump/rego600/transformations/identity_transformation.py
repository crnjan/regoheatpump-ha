"""Test."""

from ..heatpump import RegoError
from ..last_error import LastError
from .transformation import Transformation


class IdentityTransformation(Transformation):
    """Test."""

    def to_value(self, value: int | LastError | None) -> float | LastError | None:
        """Test."""
        return value

    def from_value(self, value: float) -> int:
        """Test."""
        raise RegoError("Not supported")
