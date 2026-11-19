import datetime

import pytest

from custom_components.regoheatpump.rego600.last_error import LastError
from custom_components.regoheatpump.rego600.regoerror import RegoError
from custom_components.regoheatpump.rego600.transformations import Transformations
from custom_components.regoheatpump.rego600.transformations.numeric_transformation import (
    NumericTransformation,
)


def test_to_value_should_mul_10():
    transformation = NumericTransformation(multiplier=10)
    assert transformation.to_value(1) == 10


def test_to_value_should_mul_0_1():
    transformation = NumericTransformation(multiplier=0.1)
    assert transformation.to_value(12) == 1.2


def test_to_value_none_should_return_none():
    transformation = NumericTransformation(multiplier=1)
    assert transformation.to_value(None) is None


def test_to_value_should_fail_with_non_num():
    transformation = NumericTransformation(multiplier=0.1)
    with pytest.raises(RegoError):
        transformation.to_value(
            LastError(code=1, timestamp=datetime.datetime(2010, 1, 1))
        )


@pytest.mark.parametrize(
    ("raw", "expected"),
    [(27, 2.7), (-27, -2.7), (405, 40.5), (0, 0.0), (3, 0.3), (-32768, -3276.8)],
)
def test_to_value_tenths_are_exact(raw, expected):
    transformation = NumericTransformation(multiplier=0.1)
    assert transformation.to_value(raw) == expected


def test_to_value_missing_sensor_should_return_none():
    transformation = NumericTransformation(multiplier=0.1)
    assert transformation.to_value(-483) is None


@pytest.mark.parametrize(("raw", "expected"), [(0, 0), (5, 5), (10, 10), (-3, -3)])
def test_unscaled_to_value_keeps_the_raw_number(raw, expected):
    assert Transformations.NUMERIC_UNSCALED.to_value(raw) == expected


@pytest.mark.parametrize(("value", "expected"), [(5, 5), (5.0, 5), (4.6, 5), (0, 0)])
def test_unscaled_from_value_rounds_to_a_whole_number(value, expected):
    raw = Transformations.NUMERIC_UNSCALED.from_value(value)
    assert raw == expected
    assert isinstance(raw, int)
