"""Supported register value types."""

from enum import Enum, auto


class Type(Enum):
    """Register value type."""

    TEMPERATURE = auto()
    SWITCH = auto()
    HOURS = auto()
    UNITLESS = auto()
    ERROR = auto()
    VERSION = auto()
