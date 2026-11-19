"""Tests for the integer transformation."""

import datetime

import pytest

from custom_components.regoheatpump.rego600.last_error import LastError
from custom_components.regoheatpump.rego600.regoerror import RegoError
from custom_components.regoheatpump.rego600.transformations import Transformations


@pytest.mark.parametrize(("raw", "expected"), [(0, 0), (5, 5), (10, 10), (-3, -3)])
def test_to_value_is_unscaled(raw, expected):
    value = Transformations.INTEGER.to_value(raw)
    assert value == expected
    assert isinstance(value, int)


def test_to_value_none_should_return_none():
    assert Transformations.INTEGER.to_value(None) is None


def test_to_value_should_fail_with_non_num():
    with pytest.raises(RegoError):
        Transformations.INTEGER.to_value(
            LastError(code=1, timestamp=datetime.datetime(2026, 1, 1))
        )


@pytest.mark.parametrize(("value", "expected"), [(5, 5), (5.0, 5), (4.6, 5), (0, 0)])
def test_from_value_rounds_to_whole_number(value, expected):
    raw = Transformations.INTEGER.from_value(value)
    assert raw == expected
    assert isinstance(raw, int)
