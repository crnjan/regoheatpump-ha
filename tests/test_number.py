from __future__ import annotations

from types import SimpleNamespace
from unittest.mock import Mock

import pytest
from homeassistant.helpers.device_registry import DeviceInfo

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
