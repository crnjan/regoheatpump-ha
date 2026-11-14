"""Binary sensor platform for Rego heat pump switches."""

import logging

from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntity,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

from . import RegoConfigEntry
from .entity import POLL_INTERVAL, RegoEntity
from .rego600 import Identifier, Identifiers, LastError, Register, Type

_LOGGER = logging.getLogger(__name__)

SCAN_INTERVAL = POLL_INTERVAL
PARALLEL_UPDATES = 1

# Entities not listed have no device class and show plain on/off
_DEVICE_CLASSES: dict[Identifier, BinarySensorDeviceClass] = {
    Identifiers.DEVICE_VALUES_ALARM: BinarySensorDeviceClass.PROBLEM,
    Identifiers.FRONT_PANEL_ALARM_LAMP: BinarySensorDeviceClass.PROBLEM,
    Identifiers.DEVICE_VALUES_COMPRESSOR: BinarySensorDeviceClass.RUNNING,
    Identifiers.DEVICE_VALUES_COLD_FLUID_PUMP: BinarySensorDeviceClass.RUNNING,
    Identifiers.DEVICE_VALUES_RADIATOR_PUMP: BinarySensorDeviceClass.RUNNING,
    Identifiers.DEVICE_VALUES_HEATFLUID_PUMP: BinarySensorDeviceClass.RUNNING,
    Identifiers.DEVICE_VALUES_ADDITIONAL_HEAT_3KW: BinarySensorDeviceClass.RUNNING,
    Identifiers.DEVICE_VALUES_ADDITIONAL_HEAT_6KW: BinarySensorDeviceClass.RUNNING,
}


async def async_setup_entry(
    hass: HomeAssistant,
    entry: RegoConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Set up binary sensors for readable switch registers."""
    async_add_entities(
        RegoBinarySensorEntity(entry, register)
        for register in entry.runtime_data.heat_pump.registers
        if register.type == Type.SWITCH and not register.is_writable
    )


class RegoBinarySensorEntity(BinarySensorEntity, RegoEntity):
    """Binary sensor for an on/off heat pump register."""

    def __init__(self, entry: RegoConfigEntry, register: Register) -> None:
        """Initialize binary sensor entity for a specific register."""
        super().__init__(entry, register)
        self._attr_device_class = _DEVICE_CLASSES.get(register.identifier)

    def _process_value(self, value: float | LastError | None) -> None:
        self._attr_is_on = value != 0
