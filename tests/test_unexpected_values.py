"""Plain entities reject values that are not numbers."""

from datetime import datetime
from types import SimpleNamespace
from unittest.mock import AsyncMock, Mock

from homeassistant.helpers.device_registry import DeviceInfo
import pytest

from custom_components.regoheatpump import binary_sensor, number, sensor
from custom_components.regoheatpump.rego600 import LastError, RegoType
from custom_components.regoheatpump.rego600.repositories.register_repository import (
    RegisterRepository,
)

_UNEXPECTED = [
    LastError(code=1, timestamp=datetime(2026, 1, 1)),
    datetime(2026, 11, 17, 13, 31, 2),
]


async def _entity(platform, identifier: str, value):
    entry = Mock()
    entry.entry_id = "test-entry"
    entry.runtime_data = SimpleNamespace(
        heat_pump=SimpleNamespace(
            registers=RegisterRepository.registers(RegoType.REGO637),
            read=AsyncMock(return_value=value),
        ),
        device_info=DeviceInfo(identifiers={("regoheatpump", "test-entry")}),
    )
    add = Mock()
    await platform.async_setup_entry(Mock(), entry, add)
    return next(
        e for e in add.call_args.args[0] if str(e._register.identifier) == identifier
    )


@pytest.mark.parametrize(
    ("platform", "identifier"),
    [
        (sensor, "sensor_values-outdoor"),
        (binary_sensor, "device_values-compressor"),
        (number, "settings-hot_water_target"),
    ],
)
@pytest.mark.parametrize("value", _UNEXPECTED)
async def test_unexpected_value_makes_the_entity_unavailable(
    platform, identifier, value
) -> None:
    entity = await _entity(platform, identifier, value)

    await entity.async_update()

    assert entity.available is False


@pytest.mark.parametrize(
    ("platform", "identifier", "value"),
    [
        (sensor, "sensor_values-outdoor", 21.5),
        (sensor, "sensor_values-outdoor", None),
        (binary_sensor, "device_values-compressor", 1),
        (number, "settings-hot_water_target", 48.0),
    ],
)
async def test_numbers_and_none_are_accepted(platform, identifier, value) -> None:
    entity = await _entity(platform, identifier, value)

    await entity.async_update()

    assert entity.available is True
