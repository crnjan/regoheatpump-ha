"""Test."""

from .source import Source


class Sources:
    """Test."""

    FRONT_PANEL = Source(read=0x00)
    SYSTEM = Source(read=0x02, write=0x03)
    LAST_ERROR = Source(read=0x40)
    VERSION = Source(read=0x7F)
