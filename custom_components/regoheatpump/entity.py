"""Test sensor."""

import logging

from homeassistant.components.sensor import Entity

from . import RegoConfigEntry
from .rego600 import HeatPump, Identifiers, LastError, Register, RegoError

_LOGGER = logging.getLogger(__name__)

_ENABLED_ENTITIES = [
    Identifiers.LAST_ERROR,
    Identifiers.SENSOR_VALUES_RADIATOR_RETURN,
    Identifiers.SENSOR_VALUES_OUTDOOR,
    Identifiers.SENSOR_VALUES_HOTWATER,
    Identifiers.SENSOR_VALUES_RADIATOR_FORWARD,
    Identifiers.SENSOR_VALUES_HEATFLUID_OUT,
    Identifiers.SENSOR_VALUES_HEATFLUID_IN,
    Identifiers.SENSOR_VALUES_COLDFLUID_IN,
    Identifiers.SENSOR_VALUES_COLDFLUID_OUT,
    Identifiers.SENSOR_VALUES_EXTERNAL_HOTWATER,
    Identifiers.CONTROL_DATA_RADIATOR_FORWARD_TARGET,
    Identifiers.CONTROL_DATA_RADIATOR_RETURN_ON,
    Identifiers.CONTROL_DATA_RADIATOR_RETURN_OFF,
    Identifiers.CONTROL_DATA_HOTWATER_ON,
    Identifiers.CONTROL_DATA_HOTWATER_OFF,
    Identifiers.DEVICE_VALUES_COLD_FLUID_PUMP,
    Identifiers.DEVICE_VALUES_COMPRESSOR,
    Identifiers.DEVICE_VALUES_ADDITIONAL_HEAT_3KW,
    Identifiers.DEVICE_VALUES_ADDITIONAL_HEAT_6KW,
    Identifiers.DEVICE_VALUES_RADIATOR_PUMP,
    Identifiers.DEVICE_VALUES_HEATFLUID_PUMP,
    Identifiers.DEVICE_VALUES_SWITCH_VALVE,
    Identifiers.DEVICE_VALUES_ALARM,
    Identifiers.SETTINGS_HEAT_CURVE,
    Identifiers.SETTINGS_HEAT_CURVE_FINE_ADJ,
    Identifiers.SETTINGS_SUMMER_DISCONNECTION,
    Identifiers.SETTINGS_HOTWATER_TARGET,
    Identifiers.SETTINGS_HOTWATER_TARGET_HYSTERESIS,
    Identifiers.OPERATING_TIMES_HP_IN_OPERATION_RAD,
    Identifiers.OPERATING_TIMES_HP_IN_OPERATION_DHW,
    Identifiers.OPERATING_TIMES_ADD_HEAT_IN_OPERATION_RAD,
    Identifiers.OPERATING_TIMES_ADD_HEAT_IN_OPERATION_DHW,
]


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
        self._attr_entity_registry_enabled_default = (
            register.identifier in _ENABLED_ENTITIES
        )

    async def async_update(self) -> None:
        """Update."""
        try:
            self._process_value(await self._heat_pump.read(self._register))
            self._attr_available = True
        except (OSError, RegoError) as e:
            self._attr_available = False
            _LOGGER.warning("Reading %s failed due %s", self._register.identifier, e)

    def _process_value(self, value: float | LastError | None) -> None:
        raise NotImplementedError
