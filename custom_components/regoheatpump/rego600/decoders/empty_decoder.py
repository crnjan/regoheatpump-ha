"""Test."""

from .abstract_decoder import AbstractDecoder


class EmptyDecoder(AbstractDecoder):
    """Test."""

    @property
    def length(self) -> int:
        """Test."""
        return 1

    def _convert(self, buffer: bytes) -> int:
        return 0
