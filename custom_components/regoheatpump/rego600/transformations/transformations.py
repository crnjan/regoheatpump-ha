"""Shared transformation instances."""

from .bcd_transformation import BcdTransformation
from .identity_transformation import IdentityTransformation
from .integer_transformation import IntegerTransformation
from .numeric_transformation import NumericTransformation


class Transformations:
    """Namespace for shared transformations."""

    IDENTITY = IdentityTransformation()
    BCD = BcdTransformation()
    INTEGER = IntegerTransformation()
    NUMERIC_ONE_TENTH = NumericTransformation(multiplier=0.1)
