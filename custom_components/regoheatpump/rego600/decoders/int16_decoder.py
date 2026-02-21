"""Decoder for int16 register responses."""

from .uint16_decoder import UInt16Decoder


class Int16Decoder(UInt16Decoder):
    """Decode a signed int16 value."""

    def _convert(self, buffer: bytes) -> int:
        value = super()._convert(buffer)
        return value if (value & 0x8000) == 0 else value - 0x10000
