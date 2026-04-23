from .register_factory import RegisterFactory
from .rego636 import Rego636RegisterRepository
from .rego637 import Rego637RegisterRepository
from ..identifiers import Identifiers
from ..rego_type import RegoType
from ..register import Register


class RegisterRepository:
    @staticmethod
    def _repository(rego_type: RegoType) -> type[Rego636RegisterRepository] | type[Rego637RegisterRepository]:
        """Return the register repository class for the given controller type."""
        repositories: dict[RegoType, type[Rego636RegisterRepository] | type[Rego637RegisterRepository]] = {
            RegoType.REGO637: Rego637RegisterRepository,
            RegoType.REGO636: Rego636RegisterRepository,
        }
        return repositories[rego_type]

    @staticmethod
    def version() -> Register:
        """Version register."""
        return RegisterFactory.version(identifier=Identifiers.VERSION)

    @staticmethod
    def registers(rego_type: RegoType) -> list[Register]:
        """Return all registers for the given controller type."""
        return RegisterRepository._repository(rego_type).registers()
