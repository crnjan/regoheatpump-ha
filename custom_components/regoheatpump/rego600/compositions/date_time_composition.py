"""Composition of a date and time from its fields."""

from datetime import datetime

from ..readable_register import Value
from ..regoerror import RegoProtocolError
from .composition import Composition


class DateTimeComposition(Composition[datetime]):
    """Build a date and time (no time zone) from its fields.

    Expects second, minute, hour, date, month and two-digit year, in that order.
    """

    FIELDS = 6

    def combine(self, values: list[Value]) -> datetime:
        """Return the date and time, or raise for an impossible one."""
        if len(values) != self.FIELDS:
            raise RegoProtocolError(f"Expected {self.FIELDS} values, got {values}")
        fields = [value for value in values if isinstance(value, int)]
        if len(fields) != self.FIELDS:
            raise RegoProtocolError(f"Expected whole numbers, got {values}")
        second, minute, hour, date, month, year = fields
        try:
            return datetime(2000 + year, month, date, hour, minute, second)
        except ValueError as err:
            raise RegoProtocolError(f"Invalid date and time {values}") from err
