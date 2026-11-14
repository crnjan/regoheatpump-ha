"""Tests for entity categories."""

from types import SimpleNamespace
from unittest.mock import Mock

from homeassistant.const import EntityCategory
from homeassistant.helpers.device_registry import DeviceInfo
import pytest

from custom_components.regoheatpump import binary_sensor, number, sensor
from custom_components.regoheatpump.entity import _ENTITY_CATEGORIES
from custom_components.regoheatpump.rego600 import RegoType
from custom_components.regoheatpump.rego600.repositories.register_repository import (
    RegisterRepository,
)


async def _all_entities(rego_type: RegoType) -> list:
    entry = Mock()
    entry.entry_id = "test-entry"
    entry.runtime_data = SimpleNamespace(
        heat_pump=SimpleNamespace(registers=RegisterRepository.registers(rego_type)),
        device_info=DeviceInfo(identifiers={("regoheatpump", "test-entry")}),
    )
    entities = []
    for platform in (binary_sensor, number, sensor):
        add = Mock()
        await platform.async_setup_entry(Mock(), entry, add)
        entities.extend(add.call_args.args[0])
    assert len(entities) == len(RegisterRepository.registers(rego_type))
    return entities


# Written out by hand, on purpose not derived from _ENTITY_CATEGORIES, so a
# wrong or missing entry in the production mapping fails the tests.
_EXPECTED_CONFIG = {
    "settings-heat_curve_coupling_diff",
    "settings-heat_curve_2",
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
    "settings-curve_infl_by_in_temp",
    "settings-summer_disconnection",
    "settings-hot_water_target_hysteresis",
}

_EXPECTED_DIAGNOSTIC = {
    "front_panel-power_lamp",
    "front_panel-heat_pump_lamp",
    "front_panel-additional_heat_lamp",
    "front_panel-hot_water_lamp",
    "front_panel-alarm_lamp",
    "control_data-radiator_forward_target",
    "control_data-radiator_return_target",
    "control_data-radiator_return_on",
    "control_data-radiator_return_off",
    "control_data-hot_water_on",
    "control_data-hot_water_off",
    "operating_times-heat_pump_in_operation_rad",
    "operating_times-heat_pump_in_operation_dhw",
    "operating_times-add_heat_in_operation_rad",
    "operating_times-add_heat_in_operation_dhw",
}

_EXPECTED_PRIMARY_SAMPLE = {
    "info-last_error",
    "sensor_values-outdoor",
    "sensor_values-hot_water",
    "sensor_values-radiator_forward",
    "device_values-compressor",
    "device_values-alarm",
}


def _identifiers_with_category(entities: list, category: EntityCategory | None) -> set:
    return {
        str(e._register.identifier) for e in entities if e.entity_category == category
    }


@pytest.mark.parametrize("rego_type", [RegoType.REGO636, RegoType.REGO637])
async def test_entity_categories(rego_type) -> None:
    """Config and diagnostic entities are exactly the expected ones."""
    entities = await _all_entities(rego_type)

    config = _identifiers_with_category(entities, EntityCategory.CONFIG)
    diagnostic = _identifiers_with_category(entities, EntityCategory.DIAGNOSTIC)

    assert config == _EXPECTED_CONFIG
    assert diagnostic == _EXPECTED_DIAGNOSTIC


@pytest.mark.parametrize("rego_type", [RegoType.REGO636, RegoType.REGO637])
async def test_sensors_and_last_error_are_primary(rego_type) -> None:
    """Measured values, device states and the last error stay on the main list."""
    primary = _identifiers_with_category(await _all_entities(rego_type), None)

    assert primary >= _EXPECTED_PRIMARY_SAMPLE


def test_category_list_has_no_unknown_registers() -> None:
    """Every listed identifier exists on at least one controller (catches typos)."""
    known = {
        register.identifier
        for rego_type in RegoType
        for register in RegisterRepository.registers(rego_type)
    }
    assert set(_ENTITY_CATEGORIES) <= known


@pytest.mark.parametrize("rego_type", [RegoType.REGO636, RegoType.REGO637])
async def test_comfort_controls_are_primary(rego_type) -> None:
    """The settings users change day to day stay on the main entity list."""
    primary_numbers = {
        str(e._register.identifier)
        for e in await _all_entities(rego_type)
        if e._register.is_writable and e.entity_category is None
    }
    assert primary_numbers == {
        "settings-hot_water_target",
        "settings-heat_curve",
        "settings-heat_curve_fine_adj",
        "settings-indoor_temp_setting",
    }
