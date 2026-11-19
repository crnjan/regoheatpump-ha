"""Tests for the BCD transformation."""

import datetime

import pytest

from custom_components.regoheatpump.rego600.last_error import LastError
from custom_components.regoheatpump.rego600.regoerror import (
    RegoError,
    RegoProtocolError,
)
from custom_components.regoheatpump.rego600.transformations import Transformations


@pytest.mark.parametrize(("raw", "expected"), [(0x00, 0), (0x26, 26), (0x59, 59)])
def test_to_value(raw, expected):
    assert Transformations.BCD.to_value(raw) == expected


@pytest.mark.parametrize("raw", [0x5A, 0xA0, 0x0126])
def test_non_bcd_value_is_a_protocol_error(raw):
    with pytest.raises(RegoProtocolError):
        Transformations.BCD.to_value(raw)


@pytest.mark.parametrize(
    "raw", [None, LastError(code=1, timestamp=datetime.datetime(2026, 1, 1))]
)
def test_non_integer_is_rejected(raw):
    with pytest.raises(RegoError):
        Transformations.BCD.to_value(raw)


def test_writes_are_not_supported():
    with pytest.raises(RegoError):
        Transformations.BCD.from_value(26)
