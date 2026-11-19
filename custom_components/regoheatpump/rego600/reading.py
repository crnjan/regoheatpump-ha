"""A value together with when reading it started."""

from datetime import datetime
from typing import NamedTuple

from .register import Value


class Reading(NamedTuple):
    """A value and when reading it started."""

    value: Value
    # When the first command was sent (UTC), after the connection lock was taken
    started_at: datetime
