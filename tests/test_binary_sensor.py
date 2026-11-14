"""Tests for binary sensor entities."""

from types import SimpleNamespace
from unittest.mock import Mock

from homeassistant.components.binary_sensor import BinarySensorDeviceClass
from homeassistant.helpers.device_registry import DeviceInfo
import pytest

from custom_components.regoheatpump.binary_sensor import async_setup_entry
from custom_components.regoheatpump.rego600 import RegoType
from custom_components.regoheatpump.rego600.repositories.register_repository import (
    RegisterRepository,
)

# Written out by hand, on purpose not derived from the production mapping
_EXPECTED_DEVICE_CLASSES = {
    "device_values-alarm": BinarySensorDeviceClass.PROBLEM,
    "front_panel-alarm_lamp": BinarySensorDeviceClass.PROBLEM,
    "device_values-compressor": BinarySensorDeviceClass.RUNNING,
    "device_values-cold_fluid_pump": BinarySensorDeviceClass.RUNNING,
    "device_values-radiator_pump": BinarySensorDeviceClass.RUNNING,
    "device_values-heat_fluid_pump": BinarySensorDeviceClass.RUNNING,
    "device_values-additional_heat_3kw": BinarySensorDeviceClass.RUNNING,
    "device_values-additional_heat_6kw": BinarySensorDeviceClass.RUNNING,
    "device_values-switch_valve": None,
    "front_panel-power_lamp": None,
    "front_panel-heat_pump_lamp": None,
    "front_panel-additional_heat_lamp": None,
    "front_panel-hot_water_lamp": None,
}


async def _binary_sensors(rego_type: RegoType) -> dict:
    entry = Mock()
    entry.entry_id = "test-entry"
    entry.runtime_data = SimpleNamespace(
        heat_pump=SimpleNamespace(registers=RegisterRepository.registers(rego_type)),
        device_info=DeviceInfo(identifiers={("regoheatpump", "test-entry")}),
    )
    add = Mock()
    await async_setup_entry(Mock(), entry, add)
    return {str(e._register.identifier): e for e in add.call_args.args[0]}


@pytest.mark.parametrize("rego_type", [RegoType.REGO636, RegoType.REGO637])
async def test_device_classes(rego_type) -> None:
    """Alarms are problems, compressor, pumps and heaters are running."""
    entities = await _binary_sensors(rego_type)

    assert {
        identifier: entity.device_class for identifier, entity in entities.items()
    } == _EXPECTED_DEVICE_CLASSES


@pytest.mark.parametrize(("value", "expected"), [(0, False), (1, True)])
async def test_state_follows_register_value(value, expected) -> None:
    """A device class does not change how the register value maps to on/off."""
    entity = (await _binary_sensors(RegoType.REGO637))["device_values-alarm"]

    entity._process_value(value)

    assert entity.is_on is expected
