"""Sensor platform for Rego heat pump registers."""

from collections.abc import Callable
from dataclasses import dataclass
import logging
from typing import Any

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorEntityDescription,
    SensorStateClass,
    StateType,
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


@dataclass(frozen=True)
class RegoSensorEntityDescription(SensorEntityDescription):
    """Entity description for Rego sensor register."""

    value_fn: Callable[[float | LastError | None], StateType] = lambda v: (
        v if not isinstance(v, LastError) else None
    )
    extra_attributes_fn: Callable[[float | LastError | None], dict[str, Any] | None] = (
        lambda _: None
    )


_DESCRIPTIONS = {
    Type.TEMPERATURE: RegoSensorEntityDescription(
        key=Type.TEMPERATURE.name,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    Type.HOURS: RegoSensorEntityDescription(
        key=Type.HOURS.name,
        native_unit_of_measurement=UnitOfTime.HOURS,
        device_class=SensorDeviceClass.DURATION,
        state_class=SensorStateClass.TOTAL,
    ),
    Type.ERROR: RegoSensorEntityDescription(
        key=Type.ERROR.name,
        value_fn=lambda v: v.code if isinstance(v, LastError) else None,
        extra_attributes_fn=lambda v: (
            {"timestamp": v.timestamp} if isinstance(v, LastError) else {}
        ),
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
        if not register.is_writtable and register.type in _DESCRIPTIONS
    )


class RegoSensorEntity(SensorEntity, RegoEntity):
    """An entity using RegoEntity."""

    entity_description: RegoSensorEntityDescription

    def __init__(
        self,
        entry: RegoConfigEntry,
        register: Register,
        entity_description: RegoSensorEntityDescription,
    ) -> None:
        """Initialize sensor entity for a specific register."""
        super().__init__(entry, register)
        self.entity_description = entity_description

    def _process_value(self, value: float | LastError | None) -> None:
        self._attr_native_value = self.entity_description.value_fn(value)
        if extra_state := self.entity_description.extra_attributes_fn(value):
            self._attr_extra_state_attributes = extra_state
