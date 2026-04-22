"""Rego 600 protocol client and models."""

from .const import REGO_TYPE_636, REGO_TYPE_637
from .group import Group
from .heatpump import HeatPump
from .identifier import Identifier
from .identifiers import Identifiers
from .last_error import LastError
from .register import Register
from .regoerror import RegoError
from .type import Type

__all__ = [
    "REGO_TYPE_636",
    "REGO_TYPE_637",
    "Group",
    "HeatPump",
    "Identifier",
    "Identifiers",
    "LastError",
    "Register",
    "RegoError",
    "Type",
]
