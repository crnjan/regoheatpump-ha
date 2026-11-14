"""Tests for entity categories."""

from types import SimpleNamespace
from unittest.mock import Mock

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


@pytest.mark.parametrize("rego_type", [RegoType.REGO636, RegoType.REGO637])
async def test_entity_categories(rego_type) -> None:
    """Every entity gets its listed category, unlisted entities are primary."""
    for entity in await _all_entities(rego_type):
        expected = _ENTITY_CATEGORIES.get(entity._register.identifier)
        assert entity.entity_category == expected, entity.unique_id


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
