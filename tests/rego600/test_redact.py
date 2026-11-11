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
        # ")" inside secrets (review regression cases)
        (
            "rfc2217://operator:demo)password@hp.local:4000",
            "rfc2217://operator:***@hp.local:4000",
        ),
        (
            "esphome://hp.local/?password=pa)ssword&key=SECRET",
            "esphome://hp.local/?password=***&key=***",
        ),
    ],
)
def test_redact_url(url: str, expected: str) -> None:
    """Secrets are masked, everything else is kept."""
    assert redact_url(url) == expected
