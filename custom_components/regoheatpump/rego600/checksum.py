"""Test."""

from functools import reduce


def checksum(buffer: bytes) -> int:
    """Test."""
    return reduce(lambda i, j: i ^ j, buffer)
