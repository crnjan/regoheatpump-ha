"""Test sensor."""

from dataclasses import dataclass
import logging

from homeassistant.components.number import (
    NumberDeviceClass,
    NumberEntity,
    NumberEntityDescription,
)
from homeassistant.const import UnitOfTemperature
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

from . import RegoConfigEntry
from .entity import POLL_INTERVAL, RegoEntity
from .rego600 import Identifiers, LastError, Register, Type

_LOGGER = logging.getLogger(__name__)

SCAN_INTERVAL = POLL_INTERVAL
PARALLEL_UPDATES = 1


@dataclass(frozen=True)
class ValueDescription:
    """Describes Example sensor entity."""

    min: int
    max: int


_RANGES = {
    Identifiers.SETTINGS_HOTWATER_TARGET: ValueDescription(min=35, max=54),
    Identifiers.SETTINGS_HOTWATER_TARGET_HYSTERESIS: ValueDescription(min=2, max=15),
    Identifiers.SETTINGS_HEAT_CURVE: ValueDescription(min=0, max=10),
    Identifiers.SETTINGS_HEAT_CURVE_2: ValueDescription(min=0, max=10),
    Identifiers.SETTINGS_SUMMER_DISCONNECTION: ValueDescription(min=10, max=30),
}


_DESCRIPTIONS = {
    Type.TEMPERATURE: NumberEntityDescription(
        key=Type.TEMPERATURE.name,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        device_class=NumberDeviceClass.TEMPERATURE,
    ),
    Type.UNITLESS: NumberEntityDescription(
        key=Type.UNITLESS.name,
    ),
}


async def async_setup_entry(
    hass: HomeAssistant,
    entry: RegoConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Test."""
    async_add_entities(
        RegoNumberEntity(entry, register)
        for register in entry.runtime_data.heat_pump.registers
        if register.is_writtable and register.type in _DESCRIPTIONS
    )


class RegoNumberEntity(NumberEntity, RegoEntity):
    """An entity using CoordinatorEntity."""

    def __init__(self, entry: RegoConfigEntry, register: Register) -> None:
        """Test."""
        super().__init__(entry, register)
        self.entity_description = _DESCRIPTIONS[register.type]
        self._attr_native_step = 0.1
        description = _RANGES.get(
            register.identifier, ValueDescription(min=-10, max=10)
        )
        self._attr_native_min_value = description.min
        self._attr_native_max_value = description.max

    async def async_set_native_value(self, value: float) -> None:
        """Update the current value."""
        await self._heat_pump.write(self._register, value)

    def _process_value(self, value: float | LastError | None) -> None:
        self._attr_native_value = value if not isinstance(value, LastError) else None
