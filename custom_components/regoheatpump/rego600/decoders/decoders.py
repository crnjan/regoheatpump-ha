"""Test."""

from .empty_decoder import EmptyDecoder
from .error_decoder import ErrorDecoder
from .int16_decoder import Int16Decoder


class Decoders:
    """Test."""

    EMPTY = EmptyDecoder()
    ERROR = ErrorDecoder()
    INT_16 = Int16Decoder()
