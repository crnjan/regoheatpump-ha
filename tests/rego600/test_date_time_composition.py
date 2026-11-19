"""Tests for composing a date and time from its fields."""

from datetime import datetime

import pytest

from custom_components.regoheatpump.rego600.compositions import Compositions
from custom_components.regoheatpump.rego600.regoerror import RegoProtocolError

# second, minute, hour, date, month, year
_FIELDS = [2, 31, 13, 17, 11, 26]


def test_combine():
    assert Compositions.DATE_TIME.combine(_FIELDS) == datetime(2026, 11, 17, 13, 31, 2)


@pytest.mark.parametrize(
    "fields",
    [
        [2, 31, 13, 31, 11, 26],  # 31 November
        [2, 31, 24, 17, 11, 26],  # hour 24
        [60, 31, 13, 17, 11, 26],  # second 60
        [2, 31, 13, 0, 11, 26],  # day 0
    ],
)
def test_impossible_date_is_a_protocol_error(fields):
    with pytest.raises(RegoProtocolError):
        Compositions.DATE_TIME.combine(fields)


def test_wrong_number_of_fields():
    with pytest.raises(RegoProtocolError):
        Compositions.DATE_TIME.combine(_FIELDS[:5])


@pytest.mark.parametrize("odd", [None, 1.5])
def test_fields_must_be_whole_numbers(odd):
    with pytest.raises(RegoProtocolError):
        Compositions.DATE_TIME.combine([*_FIELDS[:5], odd])
