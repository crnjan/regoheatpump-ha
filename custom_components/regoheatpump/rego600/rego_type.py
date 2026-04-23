"""Enumeration of supported Rego controller types."""

from enum import StrEnum


class RegoType(StrEnum):
    """Supported Rego heat pump controller variants."""

    REGO636 = "rego636"
    REGO637 = "rego637"
