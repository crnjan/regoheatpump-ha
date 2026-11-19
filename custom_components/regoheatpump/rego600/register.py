"""Register definition and command payload builder."""

from dataclasses import dataclass

from .checksum import checksum
from .decoders import Decoder, Decoders
from .identifier import Identifier
from .readable_register import Command, ReadableRegister, Value
from .source import Source
from .transformations import Transformation, Transformations
from .type import Type
from .value_converter import int16_to_seven_bit_format


@dataclass(frozen=True)
class Register(ReadableRegister[Value]):
    """Definition of a single heat pump register."""

    identifier: Identifier
    source: Source
    address: int
    decoder: Decoder
    transformation: Transformation
    type: Type
    is_writable: bool = False

    def read(self) -> Command:
        """Build a read command for this register."""
        return Command(
            self.__payload(self.source.read, 0), self.decoder, self.transformation
        )

    def write(self, value: float) -> Command:
        """Build a write command for this register from a native value."""
        if self.source.write is None:
            raise TypeError
        return Command(
            self.__payload(self.source.write, self.transformation.from_value(value)),
            Decoders.EMPTY,
            Transformations.IDENTITY,
        )

    def read_commands(self) -> list[Command]:
        """A single read command."""
        return [self.read()]

    def combine(self, values: list[Value]) -> Value:
        """The value of the single read."""
        return values[0]

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
