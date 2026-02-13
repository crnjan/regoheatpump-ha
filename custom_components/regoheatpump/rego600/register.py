"""Register definition and command payload builder."""

from dataclasses import dataclass
from typing import NamedTuple

from .checksum import checksum
from .decoders import Decoder, Decoders
from .identifier import Identifier
from .source import Source
from .transformations import Transformation, Transformations
from .type import Type
from .value_converter import int16_to_seven_bit_format


@dataclass(frozen=True)
class Register:
    """Definition of a single heat pump register."""

    identifier: Identifier
    source: Source
    address: int
    decoder: Decoder
    transformation: Transformation
    type: Type
    is_writtable: bool = False

    class Command(NamedTuple):
        """Command payload with decode/transform metadata."""

        payload: bytes
        decoder: Decoder
        transformation: Transformation

    def read(self) -> Command:
        """Build a read command for this register."""
        return Register.Command(
            self.__payload(self.source.read, 0), self.decoder, self.transformation
        )

    def write(self, data: int) -> Command:
        """Build a write command for this register."""
        if self.source.write is None:
            raise TypeError
        return Register.Command(
            self.__payload(self.source.write, data),
            Decoders.EMPTY,
            Transformations.IDENTITY,
        )

    def __payload(self, source: int, data: int) -> bytes:
        payload_bytes = int16_to_seven_bit_format(
            self.address
        ) + int16_to_seven_bit_format(data)
        return (
            b"\x81"
            + source.to_bytes()
            + payload_bytes
            + checksum(payload_bytes).to_bytes()
        )
