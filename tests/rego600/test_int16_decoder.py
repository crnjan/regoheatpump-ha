import pytest

from rego600.decoders import Decoders
from rego600.regoerror import RegoError


def test_expected_len():
    assert Decoders.INT_16.length == 5


def test_decode_empty_buffer():
    with pytest.raises(RegoError, match="Unexpected size of ''; expecting: 5, got: 0"):
        Decoders.INT_16.decode(b"")


def test_decode_non_empty_buffer_with_invalid_len():
    with pytest.raises(RegoError, match="Unexpected size of '00010203'; expecting: 5, got: 4"):
        Decoders.INT_16.decode(b"\x00\x01\x02\x03")


def test_decode_buffer_with_invalid_header():
    with pytest.raises(RegoError, match="Invalid header for '0203040506'"):
        Decoders.INT_16.decode(b"\x02\x03\x04\x05\x06")


def test_decode_buffer_with_valid_header_and_invalid_checksum():
    with pytest.raises(RegoError, match="Invalid crc of '0103040506'"):
        Decoders.INT_16.decode(b"\x01\x03\x04\x05\x06")


def test_decode_positive_value():
    assert Decoders.INT_16.decode(b"\x01\x00\x02\x2c\x2e") == 300


def test_decode_negative_value():
    assert Decoders.INT_16.decode(b"\x01\x03\x7f\x77\x0b") == -9
    assert Decoders.INT_16.decode(b"\x01\x03\x7c\x1d\x62") == -483


def test_decodings():
    readings = [
        (b"\x01\x03\x7f\x77\x0b", -9),
        (b"\x01\x00\x02\x41\x43", 321),
        (b"\x01\x00\x03\x06\x05", 390),
        (b"\x01\x00\x02\x29\x2b", 297),
        (b"\x01\x00\x00\x20\x20", 32),
        (b"\x01\x00\x00\x06\x06", 6),
        (b"\x01\x00\x03\x0e\x0d", 398),
        (b"\x01\x00\x00\x00\x00", 0),
        (b"\x01\x00\x00\x01\x01", 1),
        (b"\x01\x00\x00\x1b\x1b", 27),
        (b"\x01\x00\x00\x64\x64", 100),
        (b"\x01\x01\x5c\x0a\x57", 28170),
        (b"\x01\x00\x20\x20\x00", 4128),
        (b"\x01\x00\x01\x22\x23", 162),
        (b"\x01\x00\x00\x3e\x3e", 62),
    ]
    for reading in readings:
        assert Decoders.INT_16.decode(reading[0]) == reading[1]
