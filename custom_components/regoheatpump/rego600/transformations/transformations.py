"""Shared transformation instances."""

from .bcd_transformation import BcdTransformation
from .identity_transformation import IdentityTransformation
from .numeric_transformation import NumericTransformation


class Transformations:
    """Namespace for shared transformations."""

    IDENTITY = IdentityTransformation()
    BCD = BcdTransformation()
    NUMERIC_ONE_TENTH = NumericTransformation(multiplier=0.1)
    NUMERIC_UNSCALED = NumericTransformation(multiplier=1)
