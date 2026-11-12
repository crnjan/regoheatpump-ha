"""Base decoder with framing and checksum validation."""

from abc import abstractmethod

from ..checksum import checksum
from ..last_error import LastError
from ..regoerror import RegoProtocolError
from .decoder import Decoder


class AbstractDecoder(Decoder):
    """Validate and decode a response frame."""

    def decode(self, buffer: bytes) -> int | LastError | None:
        """Validate header/checksum and convert payload."""
        if self.length < 1 or len(buffer) != self.length:
            raise RegoProtocolError(
                f"Unexpected size of '{buffer.hex()}'; expecting: {self.length}, got: {len(buffer)}"
            )

        if buffer[0] != 0x01:
            raise RegoProtocolError(f"Invalid header for '{buffer.hex()}'")

        if (
            self.length > 1
            and checksum(buffer[1 : self.length - 1]) != buffer[self.length - 1]
        ):
            raise RegoProtocolError(f"Invalid crc of '{buffer.hex()}'")

        try:
            return self._convert(buffer)
        except (ValueError, IndexError) as err:
            # A well-formed frame with a payload that cannot be interpreted,
            # e.g. an invalid date in the last error record
            raise RegoProtocolError(f"Invalid payload '{buffer.hex()}'") from err

    @abstractmethod
    def _convert(self, buffer: bytes) -> int | LastError | None:
        """Convert a validated buffer into a decoded value."""
