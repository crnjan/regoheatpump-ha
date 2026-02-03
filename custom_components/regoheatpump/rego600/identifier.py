"""Test."""

from dataclasses import dataclass

from .group import Group


@dataclass(frozen=True)
class Identifier:
    """Test."""

    id: str
    group: Group

    def __str__(self):
        """Test."""
        return f"{self.group.value}-{self.id}"
