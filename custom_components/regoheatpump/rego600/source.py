"""Test."""

from dataclasses import dataclass


@dataclass(frozen=True)
class Source:
    """Test."""

    read: int
    write: int | None = None
