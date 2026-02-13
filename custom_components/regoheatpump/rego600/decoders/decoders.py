"""Shared decoder instances."""

from .empty_decoder import EmptyDecoder
from .error_decoder import ErrorDecoder
from .int16_decoder import Int16Decoder


class Decoders:
    """Namespace for shared decoders."""

    EMPTY = EmptyDecoder()
    ERROR = ErrorDecoder()
    INT_16 = Int16Decoder()
