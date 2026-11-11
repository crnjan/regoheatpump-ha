"""Tests for URL redaction."""

import pytest

from custom_components.regoheatpump.rego600 import redact_url, redact_urls_in_text


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


@pytest.mark.parametrize(
    ("text", "expected"),
    [
        ("My heat pump", "My heat pump"),
        (
            "Rego Heat Pump (Rego 637, esphome://hp.local/?port_name=rego&key=A%2Bb)",
            "Rego Heat Pump (Rego 637, esphome://hp.local/?port_name=rego&key=***)",
        ),
        (
            "Old esphome://a.local/?key=one and new esphome://b.local/?key=two",
            "Old esphome://a.local/?key=*** and new esphome://b.local/?key=***",
        ),
        ("HP on /dev/ttyUSB0", "HP on /dev/ttyUSB0"),
        ("socket://host:5000", "socket://host:5000"),
    ],
)
def test_redact_urls_in_text(text: str, expected: str) -> None:
    """Every URL in free text is redacted; other text is kept."""
    assert redact_urls_in_text(text) == expected
