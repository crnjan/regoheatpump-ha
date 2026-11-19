"""Tests for the real-time clock offset sensor."""

from datetime import datetime, timedelta
from types import SimpleNamespace
from unittest.mock import AsyncMock, Mock
from zoneinfo import ZoneInfo

from homeassistant.components.sensor import SensorDeviceClass, SensorStateClass
from homeassistant.const import UnitOfTime
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.util import dt as dt_util
import pytest

from custom_components.regoheatpump import sensor
from custom_components.regoheatpump.rego600 import Reading, RegoError, RegoType
from custom_components.regoheatpump.rego600.repositories.register_repository import (
    RegisterRepository,
)

_ZONE = ZoneInfo("Europe/Ljubljana")
# When reading the clock starts
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


def _reading(controller: datetime, started_at: datetime) -> Reading:
    """A clock reading as the library returns it: local time, no time zone."""
    return Reading(controller.replace(tzinfo=None), started_at)


async def _sensors(rego_type: RegoType, read_clock: AsyncMock | None = None) -> dict:
    entry = Mock()
    entry.entry_id = "test-entry"
    entry.runtime_data = SimpleNamespace(
        heat_pump=SimpleNamespace(
            registers=RegisterRepository.registers(rego_type),
            read_timed=read_clock or AsyncMock(),
        ),
        device_info=DeviceInfo(identifiers={("regoheatpump", "test-entry")}),
    )
    add = Mock()
    await sensor.async_setup_entry(Mock(), entry, add)
    return {str(e._register.identifier): e for e in add.call_args.args[0]}


async def _clock(read_clock: AsyncMock):
    return (await _sensors(RegoType.REGO637, read_clock))["info-clock"]


async def test_only_rego_637_has_a_clock() -> None:
    assert "info-clock" in await _sensors(RegoType.REGO637)
    assert "info-clock" not in await _sensors(RegoType.REGO636)


async def test_clock_is_a_disabled_duration_sensor_in_minutes() -> None:
    entity = await _clock(AsyncMock())

    assert entity.device_class == SensorDeviceClass.DURATION
    assert entity.native_unit_of_measurement == UnitOfTime.MINUTES
    assert entity.state_class == SensorStateClass.MEASUREMENT
    assert entity.entity_registry_enabled_default is False


async def test_state_is_the_offset_in_minutes() -> None:
    read_clock = AsyncMock(return_value=_reading(_NOW + _AHEAD, _NOW))
    entity = await _clock(read_clock)

    await entity.async_update()

    assert entity.available
    assert entity.native_value == 213
    assert not entity.extra_state_attributes


async def test_offset_is_negative_when_the_controller_is_behind() -> None:
    read_clock = AsyncMock(
        return_value=_reading(_NOW - timedelta(minutes=7, seconds=40), _NOW)
    )
    entity = await _clock(read_clock)

    await entity.async_update()

    assert entity.native_value == -8


async def test_a_consistent_read_is_used_without_reading_again() -> None:
    later = _NOW + timedelta(minutes=1)
    read_clock = AsyncMock(
        side_effect=[
            _reading(_NOW + _AHEAD, _NOW),
            # One second more offset: within the tolerance
            _reading(later + _AHEAD + timedelta(seconds=1), later),
        ]
    )
    entity = await _clock(read_clock)

    await entity.async_update()
    await entity.async_update()

    assert read_clock.await_count == 2
    assert entity._offset == _AHEAD + timedelta(seconds=1)


async def test_a_torn_read_is_read_again() -> None:
    later = _NOW + timedelta(minutes=1)
    read_clock = AsyncMock(
        side_effect=[
            _reading(_NOW + _AHEAD, _NOW),
            # The minute rolled over between reading the seconds and the minutes
            _reading(later + _AHEAD + timedelta(seconds=59), later),
            _reading(later + _AHEAD, later),
        ]
    )
    entity = await _clock(read_clock)

    await entity.async_update()
    await entity.async_update()

    assert read_clock.await_count == 3
    assert entity.native_value == 213
    assert entity._offset == _AHEAD


async def test_a_clock_set_on_the_panel_is_accepted() -> None:
    later = _NOW + timedelta(minutes=1)
    read_clock = AsyncMock(
        side_effect=[
            _reading(_NOW + _AHEAD, _NOW),
            # Set to the right time on the panel: both reads agree
            _reading(later, later),
            _reading(later, later),
        ]
    )
    entity = await _clock(read_clock)

    await entity.async_update()
    await entity.async_update()

    assert read_clock.await_count == 3
    assert entity.native_value == 0


@pytest.mark.parametrize("error", [RegoError("offline"), OSError("closed")])
async def test_read_failure_makes_the_clock_unavailable(error) -> None:
    entity = await _clock(AsyncMock(side_effect=error))

    await entity.async_update()

    assert not entity.available


async def test_a_value_that_is_not_a_date_and_time_makes_the_clock_unavailable() -> (
    None
):
    entity = await _clock(AsyncMock(return_value=Reading(12.3, _NOW)))

    await entity.async_update()

    assert not entity.available


async def test_offset_is_measured_from_when_the_reading_started() -> None:
    # The reading started 5 s after the update began (e.g. queued behind other
    # requests); only the start of the reading counts
    started_at = _NOW + timedelta(seconds=5)
    entity = await _clock(
        AsyncMock(return_value=_reading(started_at + _AHEAD, started_at))
    )

    await entity.async_update()

    assert entity._offset == _AHEAD


async def _states(*offsets: timedelta) -> list:
    """The states shown after reads with these offsets, one minute apart."""
    readings = [
        _reading(_NOW + timedelta(minutes=i) + offset, _NOW + timedelta(minutes=i))
        for i, offset in enumerate(offsets)
    ]
    entity = await _clock(AsyncMock(side_effect=readings))
    states = []
    for _ in offsets:
        await entity.async_update()
        states.append(entity.native_value)
    return states


async def test_an_offset_jittering_around_half_a_minute_keeps_its_state() -> None:
    half = timedelta(minutes=212, seconds=30)
    second = timedelta(seconds=1)

    states = await _states(half - second, half + second, half - second, half)

    assert states == [212, 212, 212, 212]


async def test_an_offset_drifting_past_the_hysteresis_changes_the_state() -> None:
    states = await _states(
        timedelta(minutes=212, seconds=29),
        timedelta(minutes=212, seconds=31),
        timedelta(minutes=212, seconds=33),
        timedelta(minutes=212, seconds=35),
    )

    assert states == [212, 212, 213, 213]
