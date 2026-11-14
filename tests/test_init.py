"""Tests for integration setup."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from homeassistant.config_entries import ConfigEntryState
from homeassistant.const import CONF_URL
from homeassistant.helpers import device_registry as dr
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.regoheatpump.const import CONF_REGO_TYPE, DOMAIN
from custom_components.regoheatpump.rego600 import RegoType
from custom_components.regoheatpump.rego600.repositories.register_repository import (
    RegisterRepository,
)


@pytest.mark.parametrize(
    ("rego_type", "expected_model"),
    [(RegoType.REGO636, "Rego 636"), (RegoType.REGO637, "Rego 637")],
)
async def test_device_shows_controller_model(hass, rego_type, expected_model) -> None:
    """The device page shows which controller the entry was set up for."""
    entry = MockConfigEntry(
        domain=DOMAIN,
        data={CONF_URL: "/dev/ttyUSB0", CONF_REGO_TYPE: rego_type.value},
    )
    entry.add_to_hass(hass)

    hp = MagicMock()
    hp.verify = AsyncMock()
    hp.dispose = AsyncMock()
    hp.read = AsyncMock(return_value=None)
    # One register is enough for the device to be created
    hp.registers = [
        register
        for register in RegisterRepository.registers(rego_type)
        if str(register.identifier) == "sensor_values-outdoor"
    ]
    with patch("custom_components.regoheatpump.HeatPump.connect", return_value=hp):
        assert await hass.config_entries.async_setup(entry.entry_id)
        await hass.async_block_till_done()

    assert entry.state is ConfigEntryState.LOADED
    (device,) = dr.async_entries_for_config_entry(dr.async_get(hass), entry.entry_id)
    assert device.identifiers == {(DOMAIN, entry.entry_id)}
    assert device.name == "Heat Pump"
    assert device.model == expected_model
    assert device.manufacturer is None

    assert await hass.config_entries.async_unload(entry.entry_id)
