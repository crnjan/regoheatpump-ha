"""Sensor platform for Rego heat pump registers."""

from datetime import datetime, timedelta
import logging

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorEntityDescription,
    SensorStateClass,
)
from homeassistant.const import UnitOfTemperature, UnitOfTime
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback
from homeassistant.util import dt as dt_util

from . import RegoConfigEntry
from .entity import POLL_INTERVAL, RegoEntity
from .rego600 import (
    LastError,
    Register,
    RegoError,
    RegoProtocolError,
    Type,
    Value,
)

_LOGGER = logging.getLogger(__name__)

SCAN_INTERVAL = POLL_INTERVAL
PARALLEL_UPDATES = 1


_DESCRIPTIONS = {
    Type.TEMPERATURE: SensorEntityDescription(
        key=Type.TEMPERATURE.name,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    Type.HOURS: SensorEntityDescription(
        key=Type.HOURS.name,
        native_unit_of_measurement=UnitOfTime.HOURS,
        device_class=SensorDeviceClass.DURATION,
        state_class=SensorStateClass.TOTAL_INCREASING,
    ),
    Type.ERROR: SensorEntityDescription(
        key=Type.ERROR.name,
    ),
    Type.CLOCK: SensorEntityDescription(
        key=Type.CLOCK.name,
        native_unit_of_measurement=UnitOfTime.MINUTES,
        device_class=SensorDeviceClass.DURATION,
        state_class=SensorStateClass.MEASUREMENT,
        suggested_display_precision=0,
    ),
}

# Two reads of the clock agree when their offsets to Home Assistant's clock
# differ by at most this much. A read torn by a minute rolling over is off by
# almost a minute or more.
CLOCK_OFFSET_TOLERANCE = timedelta(seconds=2)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: RegoConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Set up Rego sensor entities from readable registers."""
    async_add_entities(
        _ENTITY_CLASSES.get(register.type, RegoSensorEntity)(
            entry, register, _DESCRIPTIONS[register.type]
        )
        for register in entry.runtime_data.heat_pump.registers
        if not register.is_writable and register.type in _DESCRIPTIONS
    )


class RegoSensorBase(SensorEntity, RegoEntity):
    """Sensor for a read-only heat pump register."""

    def __init__(
        self,
        entry: RegoConfigEntry,
        register: Register,
        entity_description: SensorEntityDescription,
    ) -> None:
        """Initialize sensor entity for a specific register."""
        super().__init__(entry, register)
        self.entity_description = entity_description


class RegoSensorEntity(RegoSensorBase):
    """Sensor showing a register value as it is."""

    def _process_value(self, value: Value) -> None:
        if value is not None and not isinstance(value, int | float):
            raise RegoProtocolError(f"Expected a number, got {value!r}")
        self._attr_native_value = value


class RegoLastErrorSensorEntity(RegoSensorBase):
    """The last error: its code as the state, when it happened as an attribute."""

    def _process_value(self, value: Value) -> None:
        if isinstance(value, LastError):
            self._attr_native_value = value.code
            self._attr_extra_state_attributes = {"timestamp": value.timestamp}
        elif value is None:
            # No error recorded
            self._attr_native_value = None
            self._attr_extra_state_attributes = {}
        else:
            raise RegoProtocolError(f"Expected the last error, got {value!r}")


class RegoClockSensorEntity(RegoSensorBase):
    """How far the controller's clock is from Home Assistant's, in minutes.

    The controller's date and time is an attribute.
    """

    # Changes on every read; the offset is what is worth keeping
    _unrecorded_attributes = frozenset({"real_time_clock"})

    _offset: timedelta | None = None

    async def async_update(self) -> None:
        """Read the clock, and read it again if it jumped against the last read."""
        try:
            controller, offset = await self._read_clock()
            if (
                self._offset is not None
                and abs(offset - self._offset) > CLOCK_OFFSET_TOLERANCE
            ):
                # Either a minute rolled over during the read, or the clock was
                # set. A second read tells: it cannot be torn again so soon.
                controller, offset = await self._read_clock()
        except (OSError, RegoError):
            self._attr_available = False
            return

        self._offset = offset
        self._attr_native_value = round(offset.total_seconds() / 60)
        self._attr_extra_state_attributes = {"real_time_clock": controller}
        self._attr_available = True

    async def _read_clock(self) -> tuple[datetime, timedelta]:
        reading = await self._heat_pump.read_timed(self._register)
        if not isinstance(reading.value, datetime):
            raise RegoProtocolError(f"Expected a date and time, got {reading.value!r}")
        controller = reading.value.replace(tzinfo=dt_util.get_default_time_zone())
        # The seconds are read first, so the start of the reading is when the
        # clock was read
        return controller, controller - reading.started_at


# Value types that need more than a plain sensor
_ENTITY_CLASSES: dict[Type, type[RegoSensorBase]] = {
    Type.ERROR: RegoLastErrorSensorEntity,
    Type.CLOCK: RegoClockSensorEntity,
}
