"""Test."""

from ..value_converter import seven_bit_format_to_int16
from .abstract_decoder import AbstractDecoder


class Int16Decoder(AbstractDecoder):
    """Test."""

    @property
    def length(self) -> int:
        """Test."""
        return 5

    def _convert(self, buffer: bytes) -> int:
        return seven_bit_format_to_int16(buffer, 1)
