"""Shared transformation instances."""

from .identity_transformation import IdentityTransformation
from .numeric_transformation import NumericTransformation


class Transformations:
    """Namespace for shared transformations."""

    IDENTITY = IdentityTransformation()
    NUMERIC_ONE_TENTH = NumericTransformation(multiplier=0.1)
