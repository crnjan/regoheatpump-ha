"""Base entity for Rego heat pump registers."""

from datetime import timedelta
import logging

from homeassistant.const import EntityCategory
from homeassistant.helpers.entity import Entity

from . import RegoConfigEntry
from .rego600 import (
    HeatPump,
    Identifier,
    Identifiers,
    LastError,
    Register,
    RegoError,
)

POLL_INTERVAL = timedelta(minutes=1)

_LOGGER = logging.getLogger(__name__)

# Entities not listed are primary entities. Last error is deliberately primary
# so it shows up next to the alarm state on generated dashboards.
_ENTITY_CATEGORIES: dict[Identifier, EntityCategory] = {
    # Installer configuration
    Identifiers.SETTINGS_HEAT_CURVE_COUPLING_DIFF: EntityCategory.CONFIG,
    Identifiers.SETTINGS_HEAT_CURVE_2: EntityCategory.CONFIG,
    Identifiers.SETTINGS_HEAT_CURVE_2_FINE_ADJ: EntityCategory.CONFIG,
    Identifiers.SETTINGS_ADJ_CURVE_AT_20: EntityCategory.CONFIG,
    Identifiers.SETTINGS_ADJ_CURVE_AT_15: EntityCategory.CONFIG,
    Identifiers.SETTINGS_ADJ_CURVE_AT_10: EntityCategory.CONFIG,
    Identifiers.SETTINGS_ADJ_CURVE_AT_5: EntityCategory.CONFIG,
    Identifiers.SETTINGS_ADJ_CURVE_AT_0: EntityCategory.CONFIG,
    Identifiers.SETTINGS_ADJ_CURVE_AT_MINUS_5: EntityCategory.CONFIG,
    Identifiers.SETTINGS_ADJ_CURVE_AT_MINUS_10: EntityCategory.CONFIG,
    Identifiers.SETTINGS_ADJ_CURVE_AT_MINUS_15: EntityCategory.CONFIG,
    Identifiers.SETTINGS_ADJ_CURVE_AT_MINUS_20: EntityCategory.CONFIG,
    Identifiers.SETTINGS_ADJ_CURVE_AT_MINUS_25: EntityCategory.CONFIG,
    Identifiers.SETTINGS_ADJ_CURVE_AT_MINUS_30: EntityCategory.CONFIG,
    Identifiers.SETTINGS_ADJ_CURVE_AT_MINUS_35: EntityCategory.CONFIG,
    Identifiers.SETTINGS_CURVE_INFL_BY_IN_TEMP: EntityCategory.CONFIG,
    Identifiers.SETTINGS_SUMMER_DISCONNECTION: EntityCategory.CONFIG,
    Identifiers.SETTINGS_HOTWATER_TARGET_HYSTERESIS: EntityCategory.CONFIG,
    # Front panel lamps (mirror the device states)
    Identifiers.FRONT_PANEL_POWER_LAMP: EntityCategory.DIAGNOSTIC,
    Identifiers.FRONT_PANEL_PUMP_LAMP: EntityCategory.DIAGNOSTIC,
    Identifiers.FRONT_PANEL_ADDITIONAL_HEAT_LAMP: EntityCategory.DIAGNOSTIC,
    Identifiers.FRONT_PANEL_WATER_HEATER_LAMP: EntityCategory.DIAGNOSTIC,
    Identifiers.FRONT_PANEL_ALARM_LAMP: EntityCategory.DIAGNOSTIC,
    # Targets and thresholds calculated by the controller
    Identifiers.CONTROL_DATA_RADIATOR_FORWARD_TARGET: EntityCategory.DIAGNOSTIC,
    Identifiers.CONTROL_DATA_RADIATOR_RETURN_TARGET: EntityCategory.DIAGNOSTIC,
    Identifiers.CONTROL_DATA_RADIATOR_RETURN_ON: EntityCategory.DIAGNOSTIC,
    Identifiers.CONTROL_DATA_RADIATOR_RETURN_OFF: EntityCategory.DIAGNOSTIC,
    Identifiers.CONTROL_DATA_HOTWATER_ON: EntityCategory.DIAGNOSTIC,
    Identifiers.CONTROL_DATA_HOTWATER_OFF: EntityCategory.DIAGNOSTIC,
    # Operating time counters
    Identifiers.OPERATING_TIMES_HP_IN_OPERATION_RAD: EntityCategory.DIAGNOSTIC,
    Identifiers.OPERATING_TIMES_HP_IN_OPERATION_DHW: EntityCategory.DIAGNOSTIC,
    Identifiers.OPERATING_TIMES_ADD_HEAT_IN_OPERATION_RAD: EntityCategory.DIAGNOSTIC,
    Identifiers.OPERATING_TIMES_ADD_HEAT_IN_OPERATION_DHW: EntityCategory.DIAGNOSTIC,
}

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
    Identifiers.SENSOR_VALUES_COMPRESSOR,
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
    """Base entity representing a single heat pump register."""

    _heat_pump: HeatPump
    _register: Register

    _attr_has_entity_name = True

    def __init__(self, entry: RegoConfigEntry, register: Register) -> None:
        """Initialize entity metadata and register binding."""
        super().__init__()

        self._heat_pump = entry.runtime_data.heat_pump
        self._register = register

        self._attr_unique_id = f"{entry.entry_id}-{register.identifier}"
        self._attr_device_info = entry.runtime_data.device_info
        self._attr_translation_key = str(register.identifier)
        self._attr_entity_category = _ENTITY_CATEGORIES.get(register.identifier)
        self._attr_entity_registry_enabled_default = (
            register.identifier in _ENABLED_ENTITIES
        )

    async def async_added_to_hass(self) -> None:
        """Trigger initial state update when entity is added."""
        self.async_schedule_update_ha_state(True)

    async def async_update(self) -> None:
        """Fetch latest register value from heat pump."""
        try:
            self._process_value(await self._heat_pump.read(self._register))
            self._attr_available = True
        except (OSError, RegoError):
            self._attr_available = False

    def _process_value(self, value: float | LastError | None) -> None:
        raise NotImplementedError
