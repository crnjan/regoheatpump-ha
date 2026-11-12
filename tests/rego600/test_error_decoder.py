import datetime
import pytest

from custom_components.regoheatpump.rego600.decoders import Decoders
from custom_components.regoheatpump.rego600.regoerror import RegoError, RegoProtocolError


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


def _frame(code: int, timestamp: str) -> bytes:
    """Build a valid 42 byte last error frame (header and checksum OK)."""
    body = [(code >> 4) & 0x0F, code & 0x0F]
    for char in timestamp.encode():
        body += [(char >> 4) & 0x0F, char & 0x0F]
    body += [0] * (40 - len(body))
    checksum = 0
    for value in body:
        checksum ^= value
    return bytes([0x01, *body, checksum])


@pytest.mark.parametrize(
    "timestamp",
    [
        "000000 00:00:00",  # e.g. controller clock never set
        "251328 05:11:52",  # month 13
        "25??28 05:11:52",  # not a number
    ],
)
def test_decode_invalid_timestamp_raises_protocol_error(timestamp):
    """An unparsable payload is a protocol error, not an unhandled ValueError."""
    with pytest.raises(RegoProtocolError, match="Invalid payload"):
        Decoders.ERROR.decode(_frame(11, timestamp))


def test_frame_helper_matches_valid_value():
    """Sanity check: the helper builds frames the decoder accepts."""
    last_error = Decoders.ERROR.decode(_frame(11, "250128 05:11:52"))
    assert last_error.code == 11
    assert last_error.timestamp == datetime.datetime(2025, 1, 28, 5, 11, 52)
