"""Error types for Rego communication and decoding."""


class RegoError(Exception):
    """Raised on protocol/transport errors."""


class RegoProtocolError(RegoError):
    """Raised when the controller responds, but with an unexpected response."""
