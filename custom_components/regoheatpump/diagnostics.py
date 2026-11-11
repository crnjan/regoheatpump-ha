"""Diagnostics support for the Rego Heat Pump integration."""

from __future__ import annotations

from typing import Any

from homeassistant.const import CONF_URL
from homeassistant.core import HomeAssistant
from homeassistant.helpers import entity_registry as er

from . import RegoConfigEntry
from .rego600 import redact_url


async def async_get_config_entry_diagnostics(
    hass: HomeAssistant, entry: RegoConfigEntry
) -> dict[str, Any]:
    """Return diagnostics for a config entry.

    Uses the entity states Home Assistant already has, so downloading
    diagnostics does not add any traffic on the serial link.
    """
    url = entry.data.get(CONF_URL, "")

    entities = []
    for entity_entry in er.async_entries_for_config_entry(
        er.async_get(hass), entry.entry_id
    ):
        state = hass.states.get(entity_entry.entity_id)
        entities.append(
            {
                "entity_id": entity_entry.entity_id,
                "register": entity_entry.unique_id.removeprefix(f"{entry.entry_id}-"),
                "disabled_by": entity_entry.disabled_by,
                "state": state.state if state else None,
                "attributes": dict(state.attributes) if state else None,
            }
        )

    # Not set if setup failed (e.g. pump unreachable) or the entry is unloaded
    runtime_data = getattr(entry, "runtime_data", None)
    if runtime_data is None:
        heat_pump: dict[str, Any] = {"available": False}
    else:
        heat_pump = {
            "available": True,
            "offline": runtime_data.heat_pump.is_offline,
            "register_count": len(runtime_data.heat_pump.registers),
        }

    return {
        "entry": {
            # The title is left out on purpose: it is free text (legacy or
            # user-chosen) that can contain URLs with secrets.
            "data": {**entry.data, CONF_URL: redact_url(url)},
            "version": entry.version,
            "state": entry.state,
            # Setup error message, e.g. why the pump was not reachable
            "reason": entry.reason,
        },
        "heat_pump": heat_pump,
        "entities": sorted(entities, key=lambda item: item["entity_id"]),
    }
