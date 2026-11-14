"""Number platform for writable Rego heat pump registers."""

from dataclasses import dataclass
import logging

from homeassistant.components.number import (
    NumberDeviceClass,
    NumberEntity,
    NumberEntityDescription,
)
from homeassistant.const import UnitOfTemperature
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

from . import RegoConfigEntry
from .entity import POLL_INTERVAL, RegoEntity
from .rego600 import Identifier, Identifiers, LastError, Register, RegoError

_LOGGER = logging.getLogger(__name__)

SCAN_INTERVAL = POLL_INTERVAL
PARALLEL_UPDATES = 1


@dataclass(frozen=True)
class ValueDescription:
    """Defines allowed value range for writable register."""

    min: int
    max: int


# Every writable register needs an entry
_RANGES: dict[Identifier, ValueDescription] = {
    Identifiers.SETTINGS_HEAT_CURVE: ValueDescription(min=0, max=10),
    Identifiers.SETTINGS_HEAT_CURVE_FINE_ADJ: ValueDescription(min=-10, max=10),
    Identifiers.SETTINGS_HEAT_CURVE_COUPLING_DIFF: ValueDescription(min=2, max=15),
    Identifiers.SETTINGS_HEAT_CURVE_2: ValueDescription(min=0, max=10),
    Identifiers.SETTINGS_HEAT_CURVE_2_FINE_ADJ: ValueDescription(min=-10, max=10),
    Identifiers.SETTINGS_ADJ_CURVE_AT_20: ValueDescription(min=-10, max=10),
    Identifiers.SETTINGS_ADJ_CURVE_AT_15: ValueDescription(min=-10, max=10),
    Identifiers.SETTINGS_ADJ_CURVE_AT_10: ValueDescription(min=-10, max=10),
    Identifiers.SETTINGS_ADJ_CURVE_AT_5: ValueDescription(min=-10, max=10),
    Identifiers.SETTINGS_ADJ_CURVE_AT_0: ValueDescription(min=-10, max=10),
    Identifiers.SETTINGS_ADJ_CURVE_AT_MINUS_5: ValueDescription(min=-10, max=10),
    Identifiers.SETTINGS_ADJ_CURVE_AT_MINUS_10: ValueDescription(min=-10, max=10),
    Identifiers.SETTINGS_ADJ_CURVE_AT_MINUS_15: ValueDescription(min=-10, max=10),
    Identifiers.SETTINGS_ADJ_CURVE_AT_MINUS_20: ValueDescription(min=-10, max=10),
    Identifiers.SETTINGS_ADJ_CURVE_AT_MINUS_25: ValueDescription(min=-10, max=10),
    Identifiers.SETTINGS_ADJ_CURVE_AT_MINUS_30: ValueDescription(min=-10, max=10),
    Identifiers.SETTINGS_ADJ_CURVE_AT_MINUS_35: ValueDescription(min=-10, max=10),
    Identifiers.SETTINGS_INDOOR_TEMP_SETTING: ValueDescription(min=10, max=30),
    Identifiers.SETTINGS_CURVE_INFL_BY_IN_TEMP: ValueDescription(min=-10, max=10),
    Identifiers.SETTINGS_SUMMER_DISCONNECTION: ValueDescription(min=10, max=30),
    Identifiers.SETTINGS_HOTWATER_TARGET: ValueDescription(min=35, max=54),
    Identifiers.SETTINGS_HOTWATER_TARGET_HYSTERESIS: ValueDescription(min=2, max=15),
}


_TEMPERATURE = NumberEntityDescription(
    key="TEMPERATURE",
    native_unit_of_measurement=UnitOfTemperature.CELSIUS,
    device_class=NumberDeviceClass.TEMPERATURE,
)

# A difference, not a temperature. Home Assistant must not convert these like
# a temperature (2.5 °C is 36.5 °F, but a 2.5 °C difference is 4.5 °F).
_TEMPERATURE_DELTA = NumberEntityDescription(
    key="TEMPERATURE_DELTA",
    native_unit_of_measurement=UnitOfTemperature.CELSIUS,
    device_class=NumberDeviceClass.TEMPERATURE_DELTA,
)

_UNITLESS = NumberEntityDescription(
    key="UNITLESS",
)

# Every writable register needs an entry
_DESCRIPTIONS: dict[Identifier, NumberEntityDescription] = {
    Identifiers.SETTINGS_HEAT_CURVE: _UNITLESS,
    Identifiers.SETTINGS_HEAT_CURVE_FINE_ADJ: _TEMPERATURE_DELTA,
    Identifiers.SETTINGS_HEAT_CURVE_COUPLING_DIFF: _TEMPERATURE_DELTA,
    Identifiers.SETTINGS_HEAT_CURVE_2: _UNITLESS,
    Identifiers.SETTINGS_HEAT_CURVE_2_FINE_ADJ: _TEMPERATURE_DELTA,
    Identifiers.SETTINGS_ADJ_CURVE_AT_20: _TEMPERATURE_DELTA,
    Identifiers.SETTINGS_ADJ_CURVE_AT_15: _TEMPERATURE_DELTA,
    Identifiers.SETTINGS_ADJ_CURVE_AT_10: _TEMPERATURE_DELTA,
    Identifiers.SETTINGS_ADJ_CURVE_AT_5: _TEMPERATURE_DELTA,
    Identifiers.SETTINGS_ADJ_CURVE_AT_0: _TEMPERATURE_DELTA,
    Identifiers.SETTINGS_ADJ_CURVE_AT_MINUS_5: _TEMPERATURE_DELTA,
    Identifiers.SETTINGS_ADJ_CURVE_AT_MINUS_10: _TEMPERATURE_DELTA,
    Identifiers.SETTINGS_ADJ_CURVE_AT_MINUS_15: _TEMPERATURE_DELTA,
    Identifiers.SETTINGS_ADJ_CURVE_AT_MINUS_20: _TEMPERATURE_DELTA,
    Identifiers.SETTINGS_ADJ_CURVE_AT_MINUS_25: _TEMPERATURE_DELTA,
    Identifiers.SETTINGS_ADJ_CURVE_AT_MINUS_30: _TEMPERATURE_DELTA,
    Identifiers.SETTINGS_ADJ_CURVE_AT_MINUS_35: _TEMPERATURE_DELTA,
    Identifiers.SETTINGS_INDOOR_TEMP_SETTING: _TEMPERATURE,
    Identifiers.SETTINGS_CURVE_INFL_BY_IN_TEMP: _UNITLESS,
    Identifiers.SETTINGS_SUMMER_DISCONNECTION: _TEMPERATURE,
    Identifiers.SETTINGS_HOTWATER_TARGET: _TEMPERATURE,
    Identifiers.SETTINGS_HOTWATER_TARGET_HYSTERESIS: _TEMPERATURE_DELTA,
}


async def async_setup_entry(
    hass: HomeAssistant,
    entry: RegoConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Set up number entities for writable registers."""
    async_add_entities(
        RegoNumberEntity(entry, register)
        for register in entry.runtime_data.heat_pump.registers
        if register.is_writable
    )


class RegoNumberEntity(NumberEntity, RegoEntity):
    """Entity representing a writable heat pump register."""

    def __init__(self, entry: RegoConfigEntry, register: Register) -> None:
        """Initialize writable register entity."""
        super().__init__(entry, register)
        self.entity_description = _DESCRIPTIONS[register.identifier]
        self._attr_native_step = 0.1
        description = _RANGES[register.identifier]
        self._attr_native_min_value = description.min
        self._attr_native_max_value = description.max

    async def async_set_native_value(self, value: float) -> None:
        """Write new value to heat pump register."""
        try:
            await self._heat_pump.write(self._register, value)
        except (OSError, RegoError) as err:
            raise HomeAssistantError(
                f"Failed to write {value} to {self._register.identifier}"
            ) from err
        self._attr_native_value = value
        self.async_write_ha_state()

    def _process_value(self, value: float | LastError | None) -> None:
        self._attr_native_value = value if not isinstance(value, LastError) else None
