"""Tests for diagnostics."""

from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from homeassistant.config_entries import ConfigEntryState
from homeassistant.const import CONF_URL
from homeassistant.helpers import entity_registry as er
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.regoheatpump.const import CONF_REGO_TYPE, DOMAIN
from custom_components.regoheatpump.diagnostics import (
    async_get_config_entry_diagnostics,
)
from custom_components.regoheatpump.rego600 import RegoError, RegoType

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
    assert "title" not in result["entry"]
    assert result["entry"]["data"][CONF_URL] == (
        "esphome://hp.local/?port_name=rego&key=***"
    )
    assert result["heat_pump"] == {
        "available": True,
        "offline": False,
        "register_count": 3,
    }
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


@pytest.mark.parametrize(
    "title",
    [
        # Older URL kept in a title after reconfigure
        "Heat pump (was esphome://old.local/?port_name=rego&key=OLDSECRET)",
        # ")" inside credentials or query values (review regression cases)
        "HP (rfc2217://operator:demo)OLDSECRET@hp.local:4000)",
        "HP (esphome://hp.local/?password=pa)ssword&key=OLDSECRET)",
    ],
)
async def test_diagnostics_never_include_title(hass, title: str) -> None:
    """Free-form titles are left out, so secrets in them can never leak."""
    entry = MockConfigEntry(
        domain=DOMAIN,
        title=title,
        data={CONF_URL: _URL, CONF_REGO_TYPE: RegoType.REGO637.value},
    )
    entry.add_to_hass(hass)
    entry.runtime_data = SimpleNamespace(
        heat_pump=MagicMock(is_offline=False, registers=[])
    )

    result = await async_get_config_entry_diagnostics(hass, entry)

    assert "title" not in result["entry"]
    assert "SECRET" not in str(result)


@pytest.mark.parametrize(
    "url",
    [
        "rfc2217://operator:demo)SECRET@hp.local:4000",
        "esphome://hp.local/?password=pa)SECRET&key=SECRET",
    ],
)
async def test_diagnostics_redact_secrets_containing_parenthesis(hass, url) -> None:
    """The configured URL is masked even if secrets contain ")"."""
    entry = MockConfigEntry(
        domain=DOMAIN,
        title="Heat pump",
        data={CONF_URL: url, CONF_REGO_TYPE: RegoType.REGO637.value},
    )
    entry.add_to_hass(hass)

    result = await async_get_config_entry_diagnostics(hass, entry)

    assert "SECRET" not in str(result)


async def test_diagnostics_without_runtime_data(hass) -> None:
    """Diagnostics work for an entry whose setup failed (no runtime data)."""
    entry = MockConfigEntry(
        domain=DOMAIN,
        title="Rego Heat Pump (Rego 637, socket://hp:9500)",
        data={CONF_URL: "socket://hp:9500", CONF_REGO_TYPE: RegoType.REGO637.value},
        state=ConfigEntryState.SETUP_RETRY,
        reason="Heat pump not reachable",
    )
    entry.add_to_hass(hass)
    registry = er.async_get(hass)
    registry.async_get_or_create(
        "sensor",
        DOMAIN,
        f"{entry.entry_id}-sensor_values-outdoor",
        config_entry=entry,
        suggested_object_id="heat_pump_outdoor",
    )

    result = await async_get_config_entry_diagnostics(hass, entry)

    assert result["heat_pump"] == {"available": False}
    assert result["entry"]["state"] == ConfigEntryState.SETUP_RETRY
    assert result["entry"]["reason"] == "Heat pump not reachable"
    assert result["entry"]["data"][CONF_URL] == "socket://hp:9500"
    assert [e["entity_id"] for e in result["entities"]] == ["sensor.heat_pump_outdoor"]


async def test_diagnostics_after_real_setup_failure(hass) -> None:
    """End to end: setup fails because the pump is unreachable, diagnostics work."""
    entry = MockConfigEntry(
        domain=DOMAIN,
        title="Rego Heat Pump (Rego 637, socket://hp:9500)",
        data={CONF_URL: "socket://hp:9500", CONF_REGO_TYPE: RegoType.REGO637.value},
    )
    entry.add_to_hass(hass)

    hp = MagicMock()
    hp.verify = AsyncMock(side_effect=RegoError("unreachable"))
    hp.dispose = AsyncMock()
    with patch("custom_components.regoheatpump.HeatPump.connect", return_value=hp):
        assert not await hass.config_entries.async_setup(entry.entry_id)
        await hass.async_block_till_done()

    assert entry.state is ConfigEntryState.SETUP_RETRY

    result = await async_get_config_entry_diagnostics(hass, entry)

    assert result["heat_pump"] == {"available": False}
    assert result["entry"]["state"] == ConfigEntryState.SETUP_RETRY
    assert result["entry"]["reason"] == "Heat pump not reachable"
