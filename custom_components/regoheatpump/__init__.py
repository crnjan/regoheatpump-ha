"""The Rego Heat Pump integration."""

from __future__ import annotations

from dataclasses import dataclass
import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_URL, Platform
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryNotReady
from homeassistant.helpers.device_registry import DeviceInfo

from .const import CONF_REGO_TYPE, DEFAULT_REGO_TYPE, DOMAIN
from .rego600 import HeatPump, RegoError

_LOGGER = logging.getLogger(__name__)


@dataclass
class RegoHeatPumpRuntimeData:
    """Runtime data stored on the config entry."""

    heat_pump: HeatPump
    device_info: DeviceInfo


type RegoConfigEntry = ConfigEntry[RegoHeatPumpRuntimeData]


_PLATFORMS: list[Platform] = [Platform.BINARY_SENSOR, Platform.NUMBER, Platform.SENSOR]


async def async_setup_entry(hass: HomeAssistant, entry: RegoConfigEntry) -> bool:
    """Set up Rego Heat Pump from a config entry."""

    hp = HeatPump.connect(
        url=entry.data[CONF_URL],
        rego_type=entry.data.get(CONF_REGO_TYPE, DEFAULT_REGO_TYPE),
    )

    try:
        await hp.verify()
    except (OSError, RegoError) as err:
        _LOGGER.debug("Heat pump not ready: %s", err)
        await hp.dispose()
        raise ConfigEntryNotReady("Heat pump not reachable") from err

    device_info = DeviceInfo(identifiers={(DOMAIN, entry.entry_id)}, name="Heat Pump")

    entry.runtime_data = RegoHeatPumpRuntimeData(hp, device_info)
    entry.async_on_unload(hp.dispose)

    await hass.config_entries.async_forward_entry_setups(entry, _PLATFORMS)

    return True


async def async_unload_entry(hass: HomeAssistant, entry: RegoConfigEntry) -> bool:
    """Unload a config entry."""
    return await hass.config_entries.async_unload_platforms(entry, _PLATFORMS)
