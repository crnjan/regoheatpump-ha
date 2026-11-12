"""Tests for entity categories."""

from types import SimpleNamespace
from unittest.mock import Mock

from homeassistant.const import EntityCategory
from homeassistant.helpers.device_registry import DeviceInfo
import pytest

from custom_components.regoheatpump import binary_sensor, number, sensor
from custom_components.regoheatpump.rego600 import Group, RegoType
from custom_components.regoheatpump.rego600.repositories.register_repository import (
    RegisterRepository,
)

_EXPECTED = {
    Group.SETTINGS: EntityCategory.CONFIG,
    Group.FRONT_PANEL: EntityCategory.DIAGNOSTIC,
    Group.OPERATING_TIMES: EntityCategory.DIAGNOSTIC,
    Group.INFO: EntityCategory.DIAGNOSTIC,
    Group.SENSOR_VALUES: None,
    Group.CONTROL_DATA: None,
    Group.DEVICE_VALUES: None,
}


@pytest.mark.parametrize("rego_type", [RegoType.REGO636, RegoType.REGO637])
async def test_entity_categories_by_group(rego_type) -> None:
    """Every entity gets the category of its register group."""
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
    for entity in entities:
        group = entity._register.identifier.group
        assert entity.entity_category == _EXPECTED[group], entity.unique_id
