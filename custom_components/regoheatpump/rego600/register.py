"""Common interface of everything that can be read from the heat pump."""

from abc import ABC, abstractmethod
from datetime import datetime
from typing import NamedTuple

from .decoders import Decoder
from .identifier import Identifier
from .last_error import LastError
from .transformations import Transformation
from .type import Type

# Every value the integration can read
type Value = float | LastError | datetime | None


class Command(NamedTuple):
    """Command payload with decode/transform metadata."""

    payload: bytes
    decoder: Decoder
    transformation: Transformation


class Register(ABC):
    """A value read with one or more commands, possibly writable."""

    identifier: Identifier
    type: Type
    is_writable: bool

    @abstractmethod
    def read_commands(self) -> list[Command]:
        """Commands to send, in order, to read the value."""

    @abstractmethod
    def combine(self, values: list[Value]) -> Value:
        """Build the value from the results of the read commands, in order."""

    @abstractmethod
    def write(self, value: float) -> Command:
        """Command to write the value; only for registers that are writable."""
