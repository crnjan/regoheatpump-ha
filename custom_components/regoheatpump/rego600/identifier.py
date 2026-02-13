"""Identifier model for a Rego register."""

from dataclasses import dataclass

from .group import Group


@dataclass(frozen=True)
class Identifier:
    """Register identifier (group + id)."""

    id: str
    group: Group

    def __str__(self):
        """Return the stable string form used in entity ids."""
        return f"{self.group.value}-{self.id}"
