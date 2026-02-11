"""Test."""

from .group import Group
from .identifier import Identifier


class Identifiers:
    """Test."""

    # HP version
    VERSION = Identifier(id="version", group=Group.INFO)
    # Last error information
    LAST_ERROR = Identifier(id="last_error", group=Group.INFO)
    # Front Panel
    FRONT_PANEL_POWER_LAMP = Identifier(id="power_lamp", group=Group.FRONT_PANEL)
    FRONT_PANEL_PUMP_LAMP = Identifier(id="heat_pump_lamp", group=Group.FRONT_PANEL)
    FRONT_PANEL_ADDITIONAL_HEAT_LAMP = Identifier(
        id="additional_heat_lamp", group=Group.FRONT_PANEL
    )
    FRONT_PANEL_WATER_HEATER_LAMP = Identifier(
        id="hot_water_lamp", group=Group.FRONT_PANEL
    )
    FRONT_PANEL_ALARM_LAMP = Identifier(id="alarm_lamp", group=Group.FRONT_PANEL)
    # System registers, sensor values
    SENSOR_VALUES_RADIATOR_RETURN = Identifier(
        id="radiator_return", group=Group.SENSOR_VALUES
    )
    SENSOR_VALUES_OUTDOOR = Identifier(id="outdoor", group=Group.SENSOR_VALUES)
    SENSOR_VALUES_HOTWATER = Identifier(id="hot_water", group=Group.SENSOR_VALUES)
    SENSOR_VALUES_RADIATOR_FORWARD = Identifier(
        id="radiator_forward", group=Group.SENSOR_VALUES
    )
    SENSOR_VALUES_INDOOR = Identifier(id="indoor", group=Group.SENSOR_VALUES)
    SENSOR_VALUES_COMPRESSOR = Identifier(id="compressor", group=Group.SENSOR_VALUES)
    SENSOR_VALUES_HEATFLUID_OUT = Identifier(
        id="heat_fluid_out", group=Group.SENSOR_VALUES
    )
    SENSOR_VALUES_HEATFLUID_IN = Identifier(
        id="heat_fluid_in", group=Group.SENSOR_VALUES
    )
    SENSOR_VALUES_COLDFLUID_IN = Identifier(
        id="cold_fluid_in", group=Group.SENSOR_VALUES
    )
    SENSOR_VALUES_COLDFLUID_OUT = Identifier(
        id="cold_fluid_out", group=Group.SENSOR_VALUES
    )
    SENSOR_VALUES_EXTERNAL_HOTWATER = Identifier(
        id="external_hot_water", group=Group.SENSOR_VALUES
    )
    # System registers, control data
    CONTROL_DATA_RADIATOR_RETURN_TARGET = Identifier(
        id="radiator_return_target", group=Group.CONTROL_DATA
    )
    CONTROL_DATA_RADIATOR_RETURN_ON = Identifier(
        id="radiator_return_on", group=Group.CONTROL_DATA
    )
    CONTROL_DATA_RADIATOR_RETURN_OFF = Identifier(
        id="radiator_return_off", group=Group.CONTROL_DATA
    )
    CONTROL_DATA_HOTWATER_ON = Identifier(id="hot_water_on", group=Group.CONTROL_DATA)
    CONTROL_DATA_HOTWATER_OFF = Identifier(id="hot_water_off", group=Group.CONTROL_DATA)
    CONTROL_DATA_RADIATOR_FORWARD_TARGET = Identifier(
        id="radiator_forward_target", group=Group.CONTROL_DATA
    )
    CONTROL_DATA_ADDHEAT_POWER_PERCENT = Identifier(
        id="add_heat_power_percent", group=Group.CONTROL_DATA
    )
    # System registers, device values
    DEVICE_VALUES_COLD_FLUID_PUMP = Identifier(
        id="cold_fluid_pump", group=Group.DEVICE_VALUES
    )
    DEVICE_VALUES_COMPRESSOR = Identifier(id="compressor", group=Group.DEVICE_VALUES)
    DEVICE_VALUES_ADDITIONAL_HEAT_3KW = Identifier(
        id="additional_heat_3kw", group=Group.DEVICE_VALUES
    )
    DEVICE_VALUES_ADDITIONAL_HEAT_6KW = Identifier(
        id="additional_heat_6kw", group=Group.DEVICE_VALUES
    )
    DEVICE_VALUES_RADIATOR_PUMP = Identifier(
        id="radiator_pump", group=Group.DEVICE_VALUES
    )
    DEVICE_VALUES_HEATFLUID_PUMP = Identifier(
        id="heat_fluid_pump", group=Group.DEVICE_VALUES
    )
    DEVICE_VALUES_SWITCH_VALVE = Identifier(
        id="switch_valve", group=Group.DEVICE_VALUES
    )
    DEVICE_VALUES_ALARM = Identifier(id="alarm", group=Group.DEVICE_VALUES)
    # System registers, settings
    SETTINGS_HEAT_CURVE = Identifier(id="heat_curve", group=Group.SETTINGS)
    SETTINGS_HEAT_CURVE_FINE_ADJ = Identifier(
        id="heat_curve_fine_adj", group=Group.SETTINGS
    )
    SETTINGS_HEAT_CURVE_COUPLING_DIFF = Identifier(
        id="heat_curve_coupling_diff", group=Group.SETTINGS
    )
    SETTINGS_HEAT_CURVE_2 = Identifier(id="heat_curve_2", group=Group.SETTINGS)
    SETTINGS_HEAT_CURVE_2_FINE_ADJ = Identifier(
        id="heat_curve_2_fine_adj", group=Group.SETTINGS
    )
    SETTINGS_ADJ_CURVE_AT_20 = Identifier(id="adj_curve_at_20", group=Group.SETTINGS)
    SETTINGS_ADJ_CURVE_AT_15 = Identifier(id="adj_curve_at_15", group=Group.SETTINGS)
    SETTINGS_ADJ_CURVE_AT_10 = Identifier(id="adj_curve_at_10", group=Group.SETTINGS)
    SETTINGS_ADJ_CURVE_AT_5 = Identifier(id="adj_curve_at_5", group=Group.SETTINGS)
    SETTINGS_ADJ_CURVE_AT_0 = Identifier(id="adj_curve_at_0", group=Group.SETTINGS)
    SETTINGS_ADJ_CURVE_AT_MINUS_5 = Identifier(
        id="adj_curve_at_minus_5", group=Group.SETTINGS
    )
    SETTINGS_ADJ_CURVE_AT_MINUS_10 = Identifier(
        id="adj_curve_at_minus_10", group=Group.SETTINGS
    )
    SETTINGS_ADJ_CURVE_AT_MINUS_15 = Identifier(
        id="adj_curve_at_minus_15", group=Group.SETTINGS
    )
    SETTINGS_ADJ_CURVE_AT_MINUS_20 = Identifier(
        id="adj_curve_at_minus_20", group=Group.SETTINGS
    )
    SETTINGS_ADJ_CURVE_AT_MINUS_25 = Identifier(
        id="adj_curve_at_minus_25", group=Group.SETTINGS
    )
    SETTINGS_ADJ_CURVE_AT_MINUS_30 = Identifier(
        id="adj_curve_at_minus_30", group=Group.SETTINGS
    )
    SETTINGS_ADJ_CURVE_AT_MINUS_35 = Identifier(
        id="adj_curve_at_minus_35", group=Group.SETTINGS
    )
    SETTINGS_INDOOR_TEMP_SETTING = Identifier(
        id="indoor_temp_setting", group=Group.SETTINGS
    )
    SETTINGS_CURVE_INFL_BY_IN_TEMP = Identifier(
        id="curve_infl_by_in_temp", group=Group.SETTINGS
    )
    SETTINGS_SUMMER_DISCONNECTION = Identifier(
        id="summer_disconnection", group=Group.SETTINGS
    )
    SETTINGS_HOTWATER_TARGET = Identifier(id="hot_water_target", group=Group.SETTINGS)
    SETTINGS_HOTWATER_TARGET_HYSTERESIS = Identifier(
        id="hot_water_target_hysteresis", group=Group.SETTINGS
    )
    # System registers, operating times
    OPERATING_TIMES_HP_IN_OPERATION_RAD = Identifier(
        id="heat_pump_in_operation_rad", group=Group.OPERATING_TIMES
    )
    OPERATING_TIMES_HP_IN_OPERATION_DHW = Identifier(
        id="heat_pump_in_operation_dhw", group=Group.OPERATING_TIMES
    )
    OPERATING_TIMES_ADD_HEAT_IN_OPERATION_RAD = Identifier(
        id="add_heat_in_operation_rad", group=Group.OPERATING_TIMES
    )
    OPERATING_TIMES_ADD_HEAT_IN_OPERATION_DHW = Identifier(
        id="add_heat_in_operation_dhw", group=Group.OPERATING_TIMES
    )
