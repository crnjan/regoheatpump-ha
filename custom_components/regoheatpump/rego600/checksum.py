"""Checksum helpers for Rego protocol frames."""

from functools import reduce


def checksum(buffer: bytes) -> int:
    """Return XOR checksum for the given payload bytes."""
    return reduce(lambda i, j: i ^ j, buffer)
