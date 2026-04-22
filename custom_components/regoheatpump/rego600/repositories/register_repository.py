from .register_factory import RegisterFactory
from .rego636 import Rego636RegisterRepository
from .rego637 import Rego637RegisterRepository
from ..const import REGO_TYPE_636, REGO_TYPE_637
from ..identifiers import Identifiers
from ..register import Register


class RegisterRepository:
    @staticmethod
    def _repository(rego_type: str):
        repositories = {
            REGO_TYPE_637: Rego637RegisterRepository,
            REGO_TYPE_636: Rego636RegisterRepository,
        }
        return repositories[rego_type]

    @staticmethod
    def version() -> Register:
        """Version register."""
        return RegisterFactory.version(identifier=Identifiers.VERSION)

    @staticmethod
    def registers(rego_type: str):
        return RegisterRepository._repository(rego_type).registers()
