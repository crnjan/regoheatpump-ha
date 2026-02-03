from .identity_transformation import IdentityTransformation
from .numeric_transformation import NumericTransformation


class Transformations:
    IDENTITY = IdentityTransformation()
    NUMERIC_ONE_TENTH = NumericTransformation(multiplier=0.1)
