"""Decoder for empty/ACK responses."""

from .abstract_decoder import AbstractDecoder


class EmptyDecoder(AbstractDecoder):
    """Decode an ACK-only response."""

    @property
    def length(self) -> int:
        """Return expected response length."""
        return 1

    def _convert(self, buffer: bytes) -> int:
        return 0
