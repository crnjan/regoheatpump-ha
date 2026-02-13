"""Binary sensor platform for Rego heat pump switches."""

import logging

from homeassistant.components.binary_sensor import BinarySensorEntity
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

from . import RegoConfigEntry
from .entity import POLL_INTERVAL, RegoEntity
from .rego600 import LastError, Type

_LOGGER = logging.getLogger(__name__)

SCAN_INTERVAL = POLL_INTERVAL
PARALLEL_UPDATES = 1


async def async_setup_entry(
    hass: HomeAssistant,
    entry: RegoConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Set up binary sensors for readable switch registers."""
    async_add_entities(
        RegoBinarySensorEntity(entry, register)
        for register in entry.runtime_data.heat_pump.registers
        if register.type == Type.SWITCH and not register.is_writtable
    )


class RegoBinarySensorEntity(BinarySensorEntity, RegoEntity):
    """An entity using CoordinatorEntity."""

    def _process_value(self, value: float | LastError | None) -> None:
        self.is_on = value != 0
