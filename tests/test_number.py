from __future__ import annotations

from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock, Mock, patch

import pytest
from homeassistant.components.number import NumberDeviceClass
from homeassistant.const import CONF_URL, UnitOfTemperature
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.util.unit_system import US_CUSTOMARY_SYSTEM
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.regoheatpump.const import CONF_REGO_TYPE, DOMAIN

from custom_components.regoheatpump.number import RegoNumberEntity, async_setup_entry
from custom_components.regoheatpump.rego600 import Identifiers, RegoType
from custom_components.regoheatpump.rego600.repositories.register_repository import RegisterRepository


async def _number_entities(rego_type: RegoType) -> dict[str, RegoNumberEntity]:
    entry = Mock()
    entry.entry_id = "test-entry"
    entry.runtime_data = SimpleNamespace(
        heat_pump=SimpleNamespace(registers=RegisterRepository.registers(rego_type)),
        device_info=DeviceInfo(identifiers={("regoheatpump", "test-entry")}, name="Heat Pump"),
    )

    async_add_entities = Mock()

    await async_setup_entry(Mock(), entry, async_add_entities)

    async_add_entities.assert_called_once()
    return {entity.unique_id: entity for entity in async_add_entities.call_args.args[0]}


@pytest.mark.parametrize("rego_type", [RegoType.REGO636, RegoType.REGO637])
@pytest.mark.parametrize(
    ("identifier", "expected_min", "expected_max"),
    [
        (Identifiers.SETTINGS_HEAT_CURVE, 0, 10),
        (Identifiers.SETTINGS_HEAT_CURVE_FINE_ADJ, -10, 10),
        (Identifiers.SETTINGS_HEAT_CURVE_COUPLING_DIFF, 2, 15),
        (Identifiers.SETTINGS_HEAT_CURVE_2, 0, 10),
        (Identifiers.SETTINGS_HEAT_CURVE_2_FINE_ADJ, -10, 10),
        (Identifiers.SETTINGS_INDOOR_TEMP_SETTING, 10, 30),
        (Identifiers.SETTINGS_SUMMER_DISCONNECTION, 10, 30),
        (Identifiers.SETTINGS_HOTWATER_TARGET, 35, 54),
        (Identifiers.SETTINGS_HOTWATER_TARGET_HYSTERESIS, 2, 15),
        # Registers without an explicit range fall back to -10..10.
        (Identifiers.SETTINGS_ADJ_CURVE_AT_0, -10, 10),
    ],
)
async def test_number_entity_value_range(
    rego_type,
    identifier,
    expected_min,
    expected_max,
) -> None:
    entities = await _number_entities(rego_type)

    entity = entities[f"test-entry-{identifier}"]
    assert entity.native_min_value == expected_min
    assert entity.native_max_value == expected_max
    assert entity.native_step == 0.1


async def test_write_failure_raises_home_assistant_error() -> None:
    """A failed register write surfaces as a HomeAssistantError."""
    from unittest.mock import AsyncMock

    from homeassistant.exceptions import HomeAssistantError

    from custom_components.regoheatpump.rego600 import RegoError

    entities = await _number_entities(RegoType.REGO637)
    entity = entities[f"test-entry-{Identifiers.SETTINGS_HOTWATER_TARGET}"]
    entity._heat_pump = Mock(write=AsyncMock(side_effect=RegoError("Write failed")))
    entity.async_write_ha_state = Mock()

    with pytest.raises(HomeAssistantError, match="Failed to write 50"):
        await entity.async_set_native_value(50)

    entity.async_write_ha_state.assert_not_called()


# Written out by hand, on purpose not derived from the production list
_EXPECTED_TEMPERATURES = {
    "settings-indoor_temp_setting",
    "settings-summer_disconnection",
    "settings-hot_water_target",
}

_EXPECTED_TEMPERATURE_DELTAS = {
    "settings-heat_curve_fine_adj",
    "settings-heat_curve_coupling_diff",
    "settings-heat_curve_2_fine_adj",
    "settings-adj_curve_at_20",
    "settings-adj_curve_at_15",
    "settings-adj_curve_at_10",
    "settings-adj_curve_at_5",
    "settings-adj_curve_at_0",
    "settings-adj_curve_at_minus_5",
    "settings-adj_curve_at_minus_10",
    "settings-adj_curve_at_minus_15",
    "settings-adj_curve_at_minus_20",
    "settings-adj_curve_at_minus_25",
    "settings-adj_curve_at_minus_30",
    "settings-adj_curve_at_minus_35",
    "settings-hot_water_target_hysteresis",
}

_EXPECTED_UNITLESS = {
    "settings-heat_curve",
    "settings-heat_curve_2",
    "settings-curve_infl_by_in_temp",
}


@pytest.mark.parametrize("rego_type", [RegoType.REGO636, RegoType.REGO637])
async def test_number_device_classes(rego_type) -> None:
    """Setpoints are temperatures, offsets and hystereses are differences."""
    entities = (await _number_entities(rego_type)).values()

    def identifiers(device_class) -> set[str]:
        return {
            str(e._register.identifier)
            for e in entities
            if e.device_class == device_class
        }

    assert identifiers(NumberDeviceClass.TEMPERATURE) == _EXPECTED_TEMPERATURES
    assert (
        identifiers(NumberDeviceClass.TEMPERATURE_DELTA) == _EXPECTED_TEMPERATURE_DELTAS
    )
    assert identifiers(None) == _EXPECTED_UNITLESS
    assert {
        e.native_unit_of_measurement for e in entities if e.device_class is not None
    } == {UnitOfTemperature.CELSIUS}


async def test_offsets_are_not_converted_like_temperatures(hass) -> None:
    """With Fahrenheit, a 2.5 °C offset must not show as 36.5 °F."""
    hass.config.units = US_CUSTOMARY_SYSTEM
    entry = MockConfigEntry(
        domain=DOMAIN,
        data={CONF_URL: "/dev/ttyUSB0", CONF_REGO_TYPE: RegoType.REGO637.value},
    )
    entry.add_to_hass(hass)

    hp = MagicMock()
    hp.verify = AsyncMock()
    hp.dispose = AsyncMock()
    hp.read = AsyncMock(return_value=2.5)
    hp.registers = [
        register
        for register in RegisterRepository.registers(RegoType.REGO637)
        if str(register.identifier)
        in ("settings-heat_curve_fine_adj", "settings-hot_water_target")
    ]
    with patch("custom_components.regoheatpump.HeatPump.connect", return_value=hp):
        assert await hass.config_entries.async_setup(entry.entry_id)
        await hass.async_block_till_done()

    offset = hass.states.get("number.heat_pump_heat_curve_fine_tune")
    assert offset.state == "2.5"
    assert offset.attributes["unit_of_measurement"] == UnitOfTemperature.CELSIUS
    assert (offset.attributes["min"], offset.attributes["max"]) == (-10, 10)

    # A real temperature is still converted
    setpoint = hass.states.get("number.heat_pump_dhw_target")
    assert setpoint.state == "36.5"
    assert setpoint.attributes["unit_of_measurement"] == UnitOfTemperature.FAHRENHEIT

    assert await hass.config_entries.async_unload(entry.entry_id)
