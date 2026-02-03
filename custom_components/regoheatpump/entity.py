"""Test sensor."""

import logging

from rego600 import HeatPump, LastError, Register, RegoError

from homeassistant.components.sensor import Entity

from . import RegoConfigEntry

_LOGGER = logging.getLogger(__name__)


class RegoEntity(Entity):
    """An entity using CoordinatorEntity."""

    _heat_pump: HeatPump
    _register: Register

    _attr_has_entity_name = True

    def __init__(self, entry: RegoConfigEntry, register: Register) -> None:
        """Test."""
        super().__init__()

        self._heat_pump = entry.runtime_data.heat_pump
        self._register = register

        self._attr_unique_id = f"{entry.entry_id}-{register.identifier}"
        self._attr_device_info = entry.runtime_data.device_info
        self._attr_translation_key = str(register.identifier)
        # self._attr_name = str(register.identifier)

    async def async_update(self) -> None:
        """Update."""
        try:
            self.process_value(await self._heat_pump.read(self._register))
            self._attr_available = True
        except (OSError, RegoError) as e:
            self._attr_available = False
            _LOGGER.warning("Reading %s failed due %s", self._register.identifier, e)

    def process_value(self, value: float | LastError | None) -> None:
        """Foo."""
        raise NotImplementedError
