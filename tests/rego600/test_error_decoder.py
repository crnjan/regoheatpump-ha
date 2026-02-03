import datetime
import pytest

from rego600.decoders import Decoders
from rego600.regoerror import RegoError


def test_expected_len():
    assert Decoders.ERROR.length == 42


def test_decode_empty_buffer():
    with pytest.raises(RegoError, match="Unexpected size of ''; expecting: 42, got: 0"):
        Decoders.ERROR.decode(b"")


def test_decode_non_empty_buffer_with_invalid_len():
    with pytest.raises(RegoError, match="Unexpected size of '00010203'; expecting: 42, got: 4"):
        Decoders.ERROR.decode(b"\x00\x01\x02\x03")


def test_decode_buffer_with_invalid_header():
    with pytest.raises(
        RegoError,
        match="Invalid header for '000000000000000000000000000000000000000000000000000000000000000000000000000000000000'",
    ):
        Decoders.ERROR.decode(bytes(42))


def test_decode_buffer_with_valid_header_and_invalid_checksum():
    with pytest.raises(
        RegoError,
        match="Invalid crc of '010200000000000000000000000000000000000000000000000000000000000000000000000000000000'",
    ):
        Decoders.ERROR.decode(b"\x01\x02" + bytes(40))


def test_decode_no_error():
    assert Decoders.ERROR.decode(b"\x01\xff" + bytes(39) + b"\xff") is None


def test_decode_value():
    last_error = Decoders.ERROR.decode(
        b"\x01\x00\x0b\x03\x02\x03\x05\x03\x00\x03\x01\x03\x02\x03\x08\x02\x00\x03\x00\x03\x05\x03\x0a\x03\x01\x03"
        + b"\x01\x03\x0a\x03\x05\x03\x02\x00\x00\x02\x01\x0b\x02\x01\x07\x0b",
    )
    assert last_error.code == 11
    assert last_error.timestamp == datetime.datetime(2025, 1, 28, 5, 11, 52)
