"""bar."""

import logging

from homeassistant.components.binary_sensor import BinarySensorEntity
from homeassistant.components.sensor import timedelta
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

from . import RegoConfigEntry
from .entity import RegoEntity
from .rego600 import LastError, Type

_LOGGER = logging.getLogger(__name__)

SCAN_INTERVAL = timedelta(seconds=60)
PARALLEL_UPDATES = 1


async def async_setup_entry(
    hass: HomeAssistant,
    entry: RegoConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Foo."""
    async_add_entities(
        (
            RegoBinarySensorEntity(entry, register)
            for register in entry.runtime_data.heat_pump.registers
            if register.type == Type.SWITCH and not register.is_writtable
        ),
        update_before_add=True,
    )


class RegoBinarySensorEntity(BinarySensorEntity, RegoEntity):
    """An entity using CoordinatorEntity."""

    def _process_value(self, value: float | LastError | None) -> None:
        self.is_on = value != 0
