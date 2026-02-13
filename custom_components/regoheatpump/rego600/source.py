"""Protocol source definition used when building commands."""

from dataclasses import dataclass


@dataclass(frozen=True)
class Source:
    """Read/write source bytes for a register group."""

    read: int
    write: int | None = None
