"""Tests for diagnostics."""

from types import SimpleNamespace
from unittest.mock import MagicMock

from homeassistant.const import CONF_URL
from homeassistant.helpers import entity_registry as er
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.regoheatpump.const import CONF_REGO_TYPE, DOMAIN
from custom_components.regoheatpump.diagnostics import (
    async_get_config_entry_diagnostics,
)
from custom_components.regoheatpump.rego600 import RegoType

_URL = "esphome://hp.local/?port_name=rego&key=SECRET"


async def test_diagnostics_redacts_and_lists_entities(hass) -> None:
    """Diagnostics hide the API key and include entity states."""
    entry = MockConfigEntry(
        domain=DOMAIN,
        # Title as written by versions before 0.0.9
        title=f"Rego Heat Pump (Rego 637, {_URL})",
        data={CONF_URL: _URL, CONF_REGO_TYPE: RegoType.REGO637.value},
    )
    entry.add_to_hass(hass)
    entry.runtime_data = SimpleNamespace(
        heat_pump=MagicMock(is_offline=False, registers=[object()] * 3)
    )

    registry = er.async_get(hass)
    outdoor = registry.async_get_or_create(
        "sensor",
        DOMAIN,
        f"{entry.entry_id}-sensor_values-outdoor",
        config_entry=entry,
        suggested_object_id="heat_pump_outdoor",
    )
    registry.async_get_or_create(
        "sensor",
        DOMAIN,
        f"{entry.entry_id}-sensor_values-indoor",
        config_entry=entry,
        suggested_object_id="heat_pump_indoor",
        disabled_by=er.RegistryEntryDisabler.INTEGRATION,
    )
    hass.states.async_set(outdoor.entity_id, "-3.4", {"unit_of_measurement": "°C"})

    result = await async_get_config_entry_diagnostics(hass, entry)

    assert "SECRET" not in str(result)
    assert result["entry"]["title"] == (
        "Rego Heat Pump (Rego 637, esphome://hp.local/?port_name=rego&key=***)"
    )
    assert result["entry"]["data"][CONF_URL] == (
        "esphome://hp.local/?port_name=rego&key=***"
    )
    assert result["heat_pump"] == {"offline": False, "register_count": 3}
    assert result["entities"] == [
        {
            "entity_id": "sensor.heat_pump_indoor",
            "register": "sensor_values-indoor",
            "disabled_by": er.RegistryEntryDisabler.INTEGRATION,
            "state": None,
            "attributes": None,
        },
        {
            "entity_id": "sensor.heat_pump_outdoor",
            "register": "sensor_values-outdoor",
            "disabled_by": None,
            "state": "-3.4",
            "attributes": {"unit_of_measurement": "°C"},
        },
    ]
