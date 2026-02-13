"""Register groups used for namespacing identifiers."""

from enum import Enum


class Group(Enum):
    """Logical register group."""

    SENSOR_VALUES = "sensor_values"
    CONTROL_DATA = "control_data"
    DEVICE_VALUES = "device_values"
    SETTINGS = "settings"
    OPERATING_TIMES = "operating_times"
    INFO = "info"
    FRONT_PANEL = "front_panel"
