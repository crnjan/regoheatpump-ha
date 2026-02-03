"""Test sensor."""

import logging

from homeassistant.components.number import NumberDeviceClass, NumberEntity
from homeassistant.components.sensor import timedelta
from homeassistant.const import UnitOfTemperature
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

from . import RegoConfigEntry
from .entity import RegoEntity
from .rego600 import LastError, Register, Type

_LOGGER = logging.getLogger(__name__)

SCAN_INTERVAL = timedelta(seconds=60)
PARALLEL_UPDATES = 1


async def async_setup_entry(
    hass: HomeAssistant,
    entry: RegoConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Test."""
    async_add_entities(
        (
            RegoNumberEntity(entry, register)
            for register in entry.runtime_data.heat_pump.registers
            if register.is_writtable and register.type == Type.TEMPERATURE
        ),
        update_before_add=True,
    )


class RegoNumberEntity(NumberEntity, RegoEntity):
    """An entity using CoordinatorEntity."""

    def __init__(self, entry: RegoConfigEntry, register: Register) -> None:
        """Test."""
        super().__init__(entry, register)
        self._attr_native_unit_of_measurement = UnitOfTemperature.CELSIUS
        self._attr_device_class = NumberDeviceClass.TEMPERATURE

    async def async_set_native_value(self, value: float) -> None:
        """Update the current value."""
        await self._heat_pump.write(self._register, value)

    def _process_value(self, value: float | LastError | None) -> None:
        self._attr_native_value = value if not isinstance(value, LastError) else None
