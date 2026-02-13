"""Identity transformation (pass-through)."""

from ..last_error import LastError
from ..regoerror import RegoError
from .transformation import Transformation


class IdentityTransformation(Transformation):
    """Pass-through transformation."""

    def to_value(self, value: int | LastError | None) -> float | LastError | None:
        """Return the decoded value unchanged."""
        return value

    def from_value(self, value: float) -> int:
        """Writes are not supported for identity transformation."""
        raise RegoError("Not supported")
