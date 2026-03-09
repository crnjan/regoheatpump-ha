"""Sensor platform for Rego heat pump registers."""

import logging

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorEntityDescription,
    SensorStateClass,
)
from homeassistant.const import UnitOfTemperature, UnitOfTime
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

from . import RegoConfigEntry
from .entity import POLL_INTERVAL, RegoEntity
from .rego600 import LastError, Register, Type

_LOGGER = logging.getLogger(__name__)

SCAN_INTERVAL = POLL_INTERVAL
PARALLEL_UPDATES = 1


_DESCRIPTIONS = {
    Type.TEMPERATURE: SensorEntityDescription(
        key=Type.TEMPERATURE.name,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    Type.HOURS: SensorEntityDescription(
        key=Type.HOURS.name,
        native_unit_of_measurement=UnitOfTime.HOURS,
        device_class=SensorDeviceClass.DURATION,
        state_class=SensorStateClass.TOTAL,
    ),
    Type.ERROR: SensorEntityDescription(
        key=Type.ERROR.name,
    ),
}


async def async_setup_entry(
    hass: HomeAssistant,
    entry: RegoConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Set up Rego sensor entities from readable registers."""
    async_add_entities(
        RegoSensorEntity(entry, register, _DESCRIPTIONS[register.type])
        for register in entry.runtime_data.heat_pump.registers
        if not register.is_writable and register.type in _DESCRIPTIONS
    )


class RegoSensorEntity(SensorEntity, RegoEntity):
    """An entity using RegoEntity."""

    entity_description: SensorEntityDescription

    def __init__(
        self,
        entry: RegoConfigEntry,
        register: Register,
        entity_description: SensorEntityDescription,
    ) -> None:
        """Initialize sensor entity for a specific register."""
        super().__init__(entry, register)
        self.entity_description = entity_description

    def _process_value(self, value: float | LastError | None) -> None:
        if isinstance(value, LastError):
            self._attr_native_value = value.code
            self._attr_extra_state_attributes = {"timestamp": value.timestamp}
        else:
            self._attr_native_value = value
