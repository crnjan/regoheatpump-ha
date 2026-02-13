"""Decoder for last error payload."""

import datetime

from ..last_error import LastError
from ..value_converter import array_to_byte, string_from_bytes
from .abstract_decoder import AbstractDecoder


class ErrorDecoder(AbstractDecoder):
    """Decode the last error response."""

    @property
    def length(self) -> int:
        """Return expected response length."""
        return 42

    def _convert(self, buffer: bytes) -> LastError | None:
        if buffer[1] == 0xFF:
            return None
        timestamp_str = string_from_bytes(buffer, 3, 15)
        year = int(timestamp_str[:2]) + 1000
        if year < 1950:
            year += 1000
        timestamp = datetime.datetime(
            year,
            int(timestamp_str[2:4]),
            int(timestamp_str[4:6]),
            int(timestamp_str[7:9]),
            int(timestamp_str[10:12]),
            int(timestamp_str[13:15]),
        )
        return LastError(array_to_byte(buffer, 1), timestamp)
