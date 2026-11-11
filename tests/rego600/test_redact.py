"""Tests for URL redaction."""

import pytest

from custom_components.regoheatpump.rego600 import redact_url


@pytest.mark.parametrize(
    ("url", "expected"),
    [
        ("/dev/ttyUSB0", "/dev/ttyUSB0"),
        ("socket://host:5000", "socket://host:5000"),
        (
            "esphome://heatpump.local/?port_name=Rego&key=AbC%2BdEf%3D",
            "esphome://heatpump.local/?port_name=Rego&key=***",
        ),
        (
            "esphome://heatpump.local/?noise_psk=secret&password=pw",
            "esphome://heatpump.local/?noise_psk=***&password=***",
        ),
        ("esphome://heatpump.local:6053/Rego", "esphome://heatpump.local:6053/Rego"),
        ("rfc2217://user:pass@host:4000", "rfc2217://user:***@host:4000"),
        ("rfc2217://user@host:4000", "rfc2217://user@host:4000"),
    ],
)
def test_redact_url(url: str, expected: str) -> None:
    """Secrets are masked, everything else is kept."""
    assert redact_url(url) == expected
