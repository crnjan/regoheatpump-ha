"""Models for decoded last error information."""

import datetime
from typing import NamedTuple


class LastError(NamedTuple):
    """Decoded last error payload."""

    code: int
    timestamp: datetime.datetime
