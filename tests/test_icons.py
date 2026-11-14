"""Tests for entity icons."""

import json
from pathlib import Path

_COMPONENT = Path(__file__).parents[1] / "custom_components" / "regoheatpump"


def test_last_error_has_alert_icon() -> None:
    """The last error stands out from the default sensor icon."""
    icons = json.loads((_COMPONENT / "icons.json").read_text())

    assert icons["entity"]["sensor"]["info-last_error"] == {
        "default": "mdi:alert-circle-outline"
    }


def test_icons_only_reference_known_entities() -> None:
    """Every icon belongs to an entity that has a name (catches typos)."""
    icons = json.loads((_COMPONENT / "icons.json").read_text())
    translations = json.loads((_COMPONENT / "translations" / "en.json").read_text())

    for platform, entities in icons["entity"].items():
        assert set(entities) <= set(translations["entity"][platform]), platform
