"""Tests for the byte-level conversion helpers."""

import pytest

from custom_components.regoheatpump.rego600.value_converter import bcd_to_int


@pytest.mark.parametrize(
    ("value", "expected"), [(0x00, 0), (0x09, 9), (0x10, 10), (0x26, 26), (0x99, 99)]
)
def test_bcd_to_int(value, expected):
    assert bcd_to_int(value) == expected


@pytest.mark.parametrize("value", [0x0A, 0x5A, 0xA0, 0xFF, 0x0126])
def test_bcd_to_int_rejects_non_bcd(value):
    with pytest.raises(ValueError, match="Invalid BCD value"):
        bcd_to_int(value)
