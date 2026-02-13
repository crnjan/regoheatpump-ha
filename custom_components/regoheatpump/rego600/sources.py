"""Protocol command sources for Rego register groups."""

from .source import Source


class Sources:
    """Shared Source instances used to build commands."""

    FRONT_PANEL = Source(read=0x00)
    SYSTEM = Source(read=0x02, write=0x03)
    LAST_ERROR = Source(read=0x40)
    VERSION = Source(read=0x7F)
