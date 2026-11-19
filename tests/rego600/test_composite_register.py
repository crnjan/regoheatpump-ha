"""Tests for composite registers."""

import pytest

from custom_components.regoheatpump.rego600 import (
    CompositeRegister,
    Identifier,
    Type,
    Value,
)
from custom_components.regoheatpump.rego600.compositions import Composition
from custom_components.regoheatpump.rego600.group import Group
from custom_components.regoheatpump.rego600.identifiers import Identifiers
from custom_components.regoheatpump.rego600.regoerror import RegoProtocolError
from custom_components.regoheatpump.rego600.repositories.register_factory import (
    RegisterFactory,
)


class _Recording(Composition):
    """Remembers the part values it got; returns their count."""

    def __init__(self) -> None:
        self.received: list[Value] | None = None

    def combine(self, values: list[Value]) -> float:
        self.received = list(values)
        return float(len(values))


class _Sum(Composition):
    def combine(self, values: list[Value]) -> float:
        return sum(v for v in values if isinstance(v, float))


def _register(address: int):
    return RegisterFactory.system_unitless(Identifiers.SETTINGS_HEAT_CURVE, address)


def _composite(*parts, composition: Composition | None = None):
    return CompositeRegister(
        identifier=Identifier(id="test", group=Group.INFO),
        type=Type.UNITLESS,
        parts=parts,
        composition=composition or _Recording(),
    )


def test_read_commands_are_the_parts_commands_in_order():
    first, second = _register(0x0001), _register(0x0002)

    assert _composite(first, second).read_commands() == [
        *first.read_commands(),
        *second.read_commands(),
    ]


def test_nested_composite_reads_all_commands_and_splits_the_values():
    inner = _composite(_register(0x0002), _register(0x0003), composition=_Sum())
    recording = _Recording()
    outer = _composite(
        _register(0x0001), inner, _register(0x0004), composition=recording
    )

    assert [c.payload for c in outer.read_commands()] == [
        r.read_commands()[0].payload for r in map(_register, (1, 2, 3, 4))
    ]
    # Each part combines its own share: the inner one sums 2.0 and 3.0
    assert outer.combine([1.0, 2.0, 3.0, 4.0]) == 3.0
    assert recording.received == [1.0, 5.0, 4.0]


@pytest.mark.parametrize("values", [[1.0], [1.0, 2.0, 3.0]])
def test_wrong_number_of_values_is_a_protocol_error(values):
    with pytest.raises(RegoProtocolError):
        _composite(_register(0x0001), _register(0x0002)).combine(values)


def test_composite_is_read_only():
    clock = RegisterFactory.real_time_clock(Identifiers.REAL_TIME_CLOCK)

    assert clock.is_writable is False
    assert clock.type is Type.CLOCK


def test_composite_cannot_be_written():
    clock = RegisterFactory.real_time_clock(Identifiers.REAL_TIME_CLOCK)

    with pytest.raises(TypeError):
        clock.write(1.0)
