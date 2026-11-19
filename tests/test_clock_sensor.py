"""Tests for the controller clock sensor."""

from datetime import datetime, timedelta
from types import SimpleNamespace
from unittest.mock import AsyncMock, Mock, patch
from zoneinfo import ZoneInfo

from homeassistant.components.sensor import SensorDeviceClass
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.util import dt as dt_util
import pytest

from custom_components.regoheatpump import sensor
from custom_components.regoheatpump.rego600 import RegoError, RegoType
from custom_components.regoheatpump.rego600.repositories.register_repository import (
    RegisterRepository,
)

_ZONE = ZoneInfo("Europe/Ljubljana")
# Home Assistant's time when the clock is read
_NOW = datetime(2026, 11, 17, 9, 58, 8, tzinfo=_ZONE)
# The controller is 3 h 33 min ahead
_AHEAD = timedelta(hours=3, minutes=33)


@pytest.fixture(autouse=True)
def time_zone():
    """Run the tests in a time zone other than UTC."""
    previous = dt_util.get_default_time_zone()
    dt_util.set_default_time_zone(_ZONE)
    yield
    dt_util.set_default_time_zone(previous)


def _local(moment: datetime) -> datetime:
    """The controller's clock as the library returns it: local, no time zone."""
    return moment.replace(tzinfo=None)


async def _sensors(rego_type: RegoType, read_clock: AsyncMock | None = None) -> dict:
    entry = Mock()
    entry.entry_id = "test-entry"
    entry.runtime_data = SimpleNamespace(
        heat_pump=SimpleNamespace(
            registers=RegisterRepository.registers(rego_type),
            read=read_clock or AsyncMock(),
        ),
        device_info=DeviceInfo(identifiers={("regoheatpump", "test-entry")}),
    )
    add = Mock()
    await sensor.async_setup_entry(Mock(), entry, add)
    return {str(e._register.identifier): e for e in add.call_args.args[0]}


async def _clock(read_clock: AsyncMock):
    return (await _sensors(RegoType.REGO637, read_clock))["info-clock"]


async def _update(entity, now: datetime) -> None:
    with patch.object(dt_util, "now", return_value=now):
        await entity.async_update()


async def test_only_rego_637_has_a_clock() -> None:
    assert "info-clock" in await _sensors(RegoType.REGO637)
    assert "info-clock" not in await _sensors(RegoType.REGO636)


async def test_clock_is_a_disabled_timestamp_sensor() -> None:
    entity = await _clock(AsyncMock())

    assert entity.device_class == SensorDeviceClass.TIMESTAMP
    assert entity.entity_registry_enabled_default is False


async def test_state_is_the_controller_time_in_the_home_assistant_time_zone() -> None:
    read_clock = AsyncMock(return_value=_local(_NOW + _AHEAD))
    entity = await _clock(read_clock)

    await _update(entity, _NOW)

    assert entity.available
    assert entity.native_value == _NOW + _AHEAD
    assert entity.native_value.tzinfo == _ZONE
    assert entity.extra_state_attributes == {"offset_minutes": 213}


async def test_offset_is_negative_when_the_controller_is_behind() -> None:
    read_clock = AsyncMock(return_value=_local(_NOW - timedelta(minutes=7, seconds=40)))
    entity = await _clock(read_clock)

    await _update(entity, _NOW)

    assert entity.extra_state_attributes == {"offset_minutes": -8}


async def test_a_consistent_read_is_used_without_reading_again() -> None:
    later = _NOW + timedelta(minutes=1)
    read_clock = AsyncMock(
        side_effect=[
            _local(_NOW + _AHEAD),
            # One second more offset: within the tolerance
            _local(later + _AHEAD + timedelta(seconds=1)),
        ]
    )
    entity = await _clock(read_clock)

    await _update(entity, _NOW)
    await _update(entity, later)

    assert read_clock.await_count == 2
    assert entity.native_value == later + _AHEAD + timedelta(seconds=1)


async def test_a_torn_read_is_read_again() -> None:
    later = _NOW + timedelta(minutes=1)
    read_clock = AsyncMock(
        side_effect=[
            _local(_NOW + _AHEAD),
            # The minute rolled over between reading the seconds and the minutes
            _local(later + _AHEAD + timedelta(seconds=59)),
            _local(later + _AHEAD),
        ]
    )
    entity = await _clock(read_clock)

    await _update(entity, _NOW)
    await _update(entity, later)

    assert read_clock.await_count == 3
    assert entity.native_value == later + _AHEAD
    assert entity.extra_state_attributes == {"offset_minutes": 213}


async def test_a_clock_set_on_the_panel_is_accepted() -> None:
    later = _NOW + timedelta(minutes=1)
    read_clock = AsyncMock(
        side_effect=[
            _local(_NOW + _AHEAD),
            # Set to the right time on the panel: both reads agree
            _local(later),
            _local(later),
        ]
    )
    entity = await _clock(read_clock)

    await _update(entity, _NOW)
    await _update(entity, later)

    assert read_clock.await_count == 3
    assert entity.native_value == later
    assert entity.extra_state_attributes == {"offset_minutes": 0}


@pytest.mark.parametrize("error", [RegoError("offline"), OSError("closed")])
async def test_read_failure_makes_the_clock_unavailable(error) -> None:
    entity = await _clock(AsyncMock(side_effect=error))

    await _update(entity, _NOW)

    assert not entity.available


async def test_a_value_that_is_not_a_date_and_time_makes_the_clock_unavailable() -> (
    None
):
    entity = await _clock(AsyncMock(return_value=12.3))

    await _update(entity, _NOW)

    assert not entity.available
