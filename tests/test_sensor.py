from __future__ import annotations

from datetime import datetime
from types import SimpleNamespace
from unittest.mock import AsyncMock, Mock

import pytest
from homeassistant.components.sensor import SensorDeviceClass, SensorStateClass
from homeassistant.const import UnitOfTemperature, UnitOfTime
from homeassistant.helpers.device_registry import DeviceInfo

from custom_components.regoheatpump.sensor import (
    RegoSensorEntity,
    _DESCRIPTIONS,
    async_setup_entry,
)
from custom_components.regoheatpump.rego600 import Group, Identifier, LastError, Type
from custom_components.regoheatpump.rego600.register_factory import RegisterFactory


@pytest.mark.parametrize(
    ("register", "expected_unit", "expected_device_class", "expected_state_class"),
    [
        (
            RegisterFactory.system_temperature(
                Identifier("temp", Group.SENSOR_VALUES), 0x020D
            ),
            UnitOfTemperature.CELSIUS,
            SensorDeviceClass.TEMPERATURE,
            SensorStateClass.MEASUREMENT,
        ),
        (
            RegisterFactory.system_hours(Identifier("hours", Group.OPERATING_TIMES), 0x0301),
            UnitOfTime.HOURS,
            SensorDeviceClass.DURATION,
            SensorStateClass.TOTAL,
        ),
        (
            RegisterFactory.last_error(Identifier("last_error", Group.DEVICE_VALUES)),
            None,
            None,
            None,
        ),
    ],
)
async def test_async_setup_entry_creates_supported_read_only_sensor_entities(
    register,
    expected_unit,
    expected_device_class,
    expected_state_class,
) -> None:
    writable_register = RegisterFactory.system_temperature(
        Identifier("setpoint", Group.SETTINGS), 0x0400, is_writable=True
    )
    unsupported_register = RegisterFactory.version(
        Identifier("version", Group.DEVICE_VALUES)
    )

    entry = Mock()
    entry.entry_id = "test-entry"
    entry.runtime_data = SimpleNamespace(
        heat_pump=SimpleNamespace(registers=[register, writable_register, unsupported_register]),
        device_info=DeviceInfo(identifiers={("regoheatpump", "test-entry")}, name="Heat Pump"),
    )

    async_add_entities = Mock()

    await async_setup_entry(Mock(), entry, async_add_entities)

    async_add_entities.assert_called_once()
    added_entities = list(async_add_entities.call_args.args[0])

    assert len(added_entities) == 1
    entity = added_entities[0]
    assert isinstance(entity, RegoSensorEntity)
    assert entity.entity_description == _DESCRIPTIONS[register.type]
    assert entity.entity_description.native_unit_of_measurement == expected_unit
    assert entity.entity_description.device_class == expected_device_class
    assert entity.entity_description.state_class == expected_state_class


async def test_process_value_sets_native_value_for_regular_sensor_value() -> None:
    register = RegisterFactory.system_temperature(
        Identifier("outdoor", Group.SENSOR_VALUES), 0x020D
    )
    entry = Mock()
    entry.entry_id = "test-entry"
    entry.runtime_data = SimpleNamespace(
        heat_pump=SimpleNamespace(),
        device_info=DeviceInfo(identifiers={("regoheatpump", "test-entry")}, name="Heat Pump"),
    )

    entity = RegoSensorEntity(entry, register, _DESCRIPTIONS[Type.TEMPERATURE])

    entity._process_value(12.3)

    assert entity.native_value == 12.3
    assert entity.extra_state_attributes is None


async def test_process_value_sets_error_code_and_timestamp_for_last_error() -> None:
    register = RegisterFactory.last_error(
        Identifier("last_error", Group.DEVICE_VALUES)
    )
    entry = Mock()
    entry.entry_id = "test-entry"
    entry.runtime_data = SimpleNamespace(
        heat_pump=SimpleNamespace(),
        device_info=DeviceInfo(identifiers={("regoheatpump", "test-entry")}, name="Heat Pump"),
    )

    entity = RegoSensorEntity(entry, register, _DESCRIPTIONS[Type.ERROR])
    timestamp = datetime(2026, 3, 9, 12, 0, 0)

    entity._process_value(LastError(code=42, timestamp=timestamp))

    assert entity.native_value == 42
    assert entity.extra_state_attributes == {"timestamp": timestamp}


async def test_async_update_reads_value_from_heat_pump_and_marks_entity_available() -> None:
    register = RegisterFactory.system_temperature(
        Identifier("outdoor", Group.SENSOR_VALUES), 0x020D
    )
    heat_pump = Mock()
    heat_pump.read = AsyncMock(return_value=7.5)
    entry = Mock()
    entry.entry_id = "test-entry"
    entry.runtime_data = SimpleNamespace(
        heat_pump=heat_pump,
        device_info=DeviceInfo(identifiers={("regoheatpump", "test-entry")}, name="Heat Pump"),
    )

    entity = RegoSensorEntity(entry, register, _DESCRIPTIONS[Type.TEMPERATURE])

    await entity.async_update()

    heat_pump.read.assert_awaited_once_with(register)
    assert entity.native_value == 7.5
    assert entity.available is True
