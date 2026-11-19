"""A value read from several registers and combined into one."""

from dataclasses import dataclass

from .compositions import Composition
from .identifier import Identifier
from .register import Command, Register, Value
from .regoerror import RegoProtocolError
from .type import Type


@dataclass(frozen=True)
class CompositeRegister(Register):
    """Read-only value built from its parts, read in the given order.

    A part can be any readable register, including another composite.
    """

    identifier: Identifier
    type: Type
    parts: tuple[Register, ...]
    composition: Composition
    is_writable: bool = False

    def read_commands(self) -> list[Command]:
        """The read commands of all parts, in order."""
        return [command for part in self.parts for command in part.read_commands()]

    def combine(self, values: list[Value]) -> Value:
        """Let each part combine its own values, then compose the results."""
        counts = [len(part.read_commands()) for part in self.parts]
        if len(values) != sum(counts):
            raise RegoProtocolError(f"Expected {sum(counts)} values, got {len(values)}")
        results = []
        index = 0
        for part, count in zip(self.parts, counts, strict=True):
            results.append(part.combine(values[index : index + count]))
            index += count
        return self.composition.combine(results)

    def write(self, value: float) -> Command:
        """Composite registers are read-only."""
        raise TypeError(f"{self.identifier} is not writable")
