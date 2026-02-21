import pytest

from rego600 import Identifier, Register
from rego600.identifiers import Identifiers
from rego600.register_repository import RegisterRepository


def verify_read(
    identifer: Identifier,
    expectedPayload: bytes,
    responseBytes: bytes,
    expectedDecodedValue: float,
    expectedValue: float,
) -> Register:
    register = next(r for r in RegisterRepository.registers() if r.identifier == identifer)
    command = register.read()
    assert command.payload == expectedPayload
    assert command.decoder.decode(responseBytes) == expectedDecodedValue
    assert command.transformation.to_value(expectedDecodedValue) == expectedValue
    return register


def test_sensor_values_radiator_return():
    verify_read(
        identifer=Identifiers.SENSOR_VALUES_RADIATOR_RETURN,
        expectedPayload=b"\x81\x02\x00\x04\x09\x00\x00\x00\x0d",
        responseBytes=b"\x01\x00\x02\x25\x27",
        expectedDecodedValue=293,
        expectedValue=29.3,
    )


def test_sensor_values_radiator_forward():
    verify_read(
        identifer=Identifiers.SENSOR_VALUES_RADIATOR_FORWARD,
        expectedPayload=b"\x81\x02\x00\x04\x0c\x00\x00\x00\x08",
        responseBytes=b"\x01\x00\x02\x41\x43",
        expectedDecodedValue=321,
        expectedValue=32.1,
    )


def test_sensor_values_outdoor():
    verify_read(
        identifer=Identifiers.SENSOR_VALUES_OUTDOOR,
        expectedPayload=b"\x81\x02\x00\x04\x0a\x00\x00\x00\x0e",
        responseBytes=b"\x01\x03\x7f\x5a\x26",
        expectedDecodedValue=-38,
        expectedValue=-3.8,
    )


def test_device_values_compressor():
    verify_read(
        identifer=Identifiers.DEVICE_VALUES_COMPRESSOR,
        expectedPayload=b"\x81\x02\x00\x03\x7e\x00\x00\x00\x7d",
        responseBytes=b"\x01\x00\x00\x01\x01",
        expectedDecodedValue=1,
        expectedValue=1,
    )

def test_system_reg_operating_times_hp_in_oper_rad():
    verify_read(
        identifer=Identifiers.OPERATING_TIMES_HP_IN_OPERATION_RAD,
        expectedPayload=b"\x81\x02\x00\x00\x48\x00\x00\x00\x48",
        responseBytes=b"\x01\x01\x67\x1b\x7d",
        expectedDecodedValue=29595,
        expectedValue=29595,
    )

def test_system_reg_operating_times_hp_in_oper_rad_uint16():
    verify_read(
        identifer=Identifiers.OPERATING_TIMES_HP_IN_OPERATION_RAD,
        expectedPayload=b"\x81\x02\x00\x00\x48\x00\x00\x00\x48",
        responseBytes=b"\x01\x02\x06\x3b\x3f",
        expectedDecodedValue=33595,
        expectedValue=33595,
    )

def test_settings_heat_curve():
    register = verify_read(
        identifer=Identifiers.SETTINGS_HEAT_CURVE,
        expectedPayload=b"\x81\x02\x00\x00\x00\x00\x00\x00\x00",
        responseBytes=b"\x01\x00\x00\x1b\x1b",
        expectedDecodedValue=27,
        expectedValue=2.7,
    )
    assert register.transformation.from_value(2.7) == 27
    command = register.write(27)
    assert command.payload == b"\x81\x03\x00\x00\x00\x00\x00\x1b\x1b"
    assert command.decoder.decode(b"\x01") == 0
    assert command.transformation.to_value(0) == 0
    assert str(register.identifier) == "settings-heat_curve"
    assert register.is_writtable


def test_front_panel_power_lamp():
    register = verify_read(
        identifer=Identifiers.FRONT_PANEL_POWER_LAMP,
        expectedPayload=b"\x81\x00\x00\x00\x12\x00\x00\x00\x12",
        responseBytes=b"\x01\x00\x00\x01\x01",
        expectedDecodedValue=1,
        expectedValue=1,
    )
    assert not register.is_writtable
    with pytest.raises(TypeError):
        register.write(0)


def test_sensor_values_indoor_not_available():
    verify_read(
        identifer=Identifiers.SENSOR_VALUES_INDOOR,
        expectedPayload=b"\x81\x02\x00\x04\x0d\x00\x00\x00\x09",
        responseBytes=b"\x01\x03\x7c\x1d\x62",
        expectedDecodedValue=-483,
        expectedValue=None,
    )
