"""Integer transformation (unscaled whole numbers)."""

from ..last_error import LastError
from ..regoerror import RegoError
from .transformation import Transformation


class IntegerTransformation(Transformation):
    """Pass raw whole numbers through unscaled, in both directions."""

    def to_value(self, value: int | LastError | None) -> int | None:
        """Return the raw value as is."""
        if value is None or isinstance(value, int):
            return value
        raise RegoError("Unsupported transformation")

    def from_value(self, value: float) -> int:
        """Round the native value to a whole number."""
        return round(value)
