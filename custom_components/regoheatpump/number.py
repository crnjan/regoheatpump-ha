"""Test sensor."""

from dataclasses import dataclass
import logging

from homeassistant.components.number import NumberDeviceClass, NumberEntity
from homeassistant.const import UnitOfTemperature
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

from . import RegoConfigEntry
from .entity import RegoEntity
from .rego600 import Identifiers, LastError, Register, Type

_LOGGER = logging.getLogger(__name__)


@dataclass(frozen=True)
class ValueDescription:
    """Describes Example sensor entity."""

    min: int
    max: int


_DESCRIPTIONS = {
    Identifiers.SETTINGS_HOTWATER_TARGET: ValueDescription(min=35, max=54),
    Identifiers.SETTINGS_HOTWATER_TARGET_HYSTERESIS: ValueDescription(min=2, max=15),
    Identifiers.SETTINGS_HEAT_CURVE: ValueDescription(min=0, max=10),
    Identifiers.SETTINGS_HEAT_CURVE_2: ValueDescription(min=0, max=10),
    Identifiers.SETTINGS_SUMMER_DISCONNECTION: ValueDescription(min=10, max=30),
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
        if register.is_writtable and register.type == Type.TEMPERATURE
    )


class RegoNumberEntity(NumberEntity, RegoEntity):
    """An entity using CoordinatorEntity."""

    def __init__(self, entry: RegoConfigEntry, register: Register) -> None:
        """Test."""
        super().__init__(entry, register)
        self._attr_native_unit_of_measurement = UnitOfTemperature.CELSIUS
        self._attr_device_class = NumberDeviceClass.TEMPERATURE
        self._attr_native_step = 0.1
        description = _DESCRIPTIONS.get(
            register.identifier, ValueDescription(min=-10, max=10)
        )
        self._attr_native_min_value = description.min
        self._attr_native_max_value = description.max

    async def async_set_native_value(self, value: float) -> None:
        """Update the current value."""
        await self._heat_pump.write(self._register, value)

    def _process_value(self, value: float | LastError | None) -> None:
        self._attr_native_value = value if not isinstance(value, LastError) else None
