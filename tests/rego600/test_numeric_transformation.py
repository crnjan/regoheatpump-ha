import datetime
import pytest

from rego600.last_error import LastError
from rego600.regoerror import RegoError
from rego600.transformations.numeric_transformation import NumericTransformation

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
        transformation.to_value(LastError(code=1, timestamp=datetime.datetime(2010, 1, 1)))
