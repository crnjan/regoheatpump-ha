"""Dispatch repository that routes register lookups to the correct controller repository."""

from .register_factory import RegisterFactory
from .rego636 import Rego636RegisterRepository
from .rego637 import Rego637RegisterRepository
from ..identifiers import Identifiers
from ..rego_type import RegoType
from ..register import Register


class RegisterRepository:
    """Selects the appropriate controller-specific register repository based on RegoType."""

    @staticmethod
    def version() -> Register:
        """Version register."""
        return RegisterFactory.version(identifier=Identifiers.VERSION)

    @staticmethod
    def registers(rego_type: RegoType) -> list[Register]:
        """Return all registers for the given controller type."""
        repositories = {
            RegoType.REGO636: Rego636RegisterRepository,
            RegoType.REGO637: Rego637RegisterRepository,
        }
        return repositories[rego_type].registers()
