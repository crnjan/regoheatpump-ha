"""Binary-coded decimal transformation."""

from ..last_error import LastError
from ..regoerror import RegoError, RegoProtocolError
from ..value_converter import bcd_to_int
from .transformation import Transformation


class BcdTransformation(Transformation):
    """Decode a two-digit BCD value: 0x26 -> 26."""

    def to_value(self, value: int | LastError | None) -> int:
        """Convert the raw BCD value to its decimal number."""
        if not isinstance(value, int):
            raise RegoError("Unsupported transformation")
        try:
            return bcd_to_int(value)
        except ValueError as err:
            raise RegoProtocolError(str(err)) from err

    def from_value(self, value: float) -> int:
        """Writes are not supported for BCD values."""
        raise RegoError("Not supported")
