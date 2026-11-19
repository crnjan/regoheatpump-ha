"""A value together with when reading it started."""

from datetime import datetime
from typing import NamedTuple


class Reading[T](NamedTuple):
    """A value and when reading it started."""

    value: T
    # When the first command was sent (UTC), after the connection lock was taken
    started_at: datetime
