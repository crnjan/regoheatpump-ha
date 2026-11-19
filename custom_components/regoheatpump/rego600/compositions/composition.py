"""Composition interface: builds one value from several part values."""

from abc import ABC, abstractmethod

from ..readable_register import Value


class Composition[T](ABC):
    """Combine the values of a composite register's parts into one value."""

    @abstractmethod
    def combine(self, values: list[Value]) -> T:
        """Build the value from the part values, in part order.

        Each composition checks that it got the values it needs.
        """
