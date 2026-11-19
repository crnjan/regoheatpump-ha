"""Composition interface: builds one value from several part values."""

from abc import ABC, abstractmethod

from ..register import Value


class Composition(ABC):
    """Combine the values of a composite register's parts into one value."""

    @abstractmethod
    def combine(self, values: list[Value]) -> Value:
        """Build the value from the part values, in part order.

        Each composition checks that it got the values it needs.
        """
