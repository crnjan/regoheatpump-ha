"""Docstring for homeassistant.components.regoheatpump.rego600.transformations.transformations."""

from .identity_transformation import IdentityTransformation
from .numeric_transformation import NumericTransformation


class Transformations:
    """Docstring for Transformations."""

    IDENTITY = IdentityTransformation()
    NUMERIC_ONE_TENTH = NumericTransformation(multiplier=0.1)
