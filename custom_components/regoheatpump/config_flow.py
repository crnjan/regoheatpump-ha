"""Config flow for the Rego Heat Pump integration."""

from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol

from homeassistant.config_entries import ConfigFlow, ConfigFlowResult
from homeassistant.const import CONF_URL
from homeassistant.helpers.selector import (
    SelectSelector,
    SelectSelectorConfig,
    SelectSelectorMode,
)

from .const import CONF_REGO_TYPE, DEFAULT_REGO_TYPE, DOMAIN, REGO_TYPE_LABELS
from .rego600 import HeatPump, RegoError

_LOGGER = logging.getLogger(__name__)


class CannotConnect(Exception):
    """Error to indicate we cannot connect."""


def build_schema(
    url_default: Any = vol.UNDEFINED,
    rego_type_default: Any = DEFAULT_REGO_TYPE,
) -> vol.Schema:
    """Build config flow schema."""
    return vol.Schema(
        {
            vol.Required(CONF_URL, default=url_default): str,
            vol.Required(CONF_REGO_TYPE, default=rego_type_default): SelectSelector(
                SelectSelectorConfig(
                    options=[
                        {"value": key, "label": label}
                        for key, label in REGO_TYPE_LABELS.items()
                    ],
                    mode=SelectSelectorMode.DROPDOWN,
                )
            ),
        }
    )


def normalize_connection_url(url: str) -> str:
    """Normalize connection URL/path for storage and duplicate checks."""
    url = url.strip()

    if "://" not in url:
        return url

    return url.rstrip("/").lower()


async def validate_input(data: dict[str, Any]) -> dict[str, str]:
    """Validate the user input allows us to connect."""
    url = normalize_connection_url(data[CONF_URL])
    rego_type = data[CONF_REGO_TYPE]

    hp = HeatPump.connect(url=url, rego_type=rego_type)

    try:
        await hp.verify(retry=0)
    except (OSError, RegoError) as err:
        raise CannotConnect from err
    finally:
        await hp.dispose()

    return {
        "title": f"Rego Heat Pump ({REGO_TYPE_LABELS[rego_type]}, {url})",
        "url": url,
        "rego_type": rego_type,
    }


class RegoConfigFlow(ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Rego Heat Pump."""

    VERSION = 1

    def _find_existing_entry_by_url(self, url: str):
        """Find an existing config entry by normalized URL."""
        for entry in self._async_current_entries():
            if entry.data.get(CONF_URL) == url:
                return entry
        return None

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Handle the initial step."""
        errors: dict[str, str] = {}

        if user_input is not None:
            try:
                info = await validate_input(user_input)
            except CannotConnect as err:
                _LOGGER.debug("Cannot connect to heat pump: %s", err)
                errors["base"] = "cannot_connect"
            except Exception:
                _LOGGER.exception("Unexpected exception during config flow")
                errors["base"] = "unknown"
            else:
                if self._find_existing_entry_by_url(info["url"]) is not None:
                    return self.async_abort(reason="already_configured")

                return self.async_create_entry(
                    title=info["title"],
                    data={
                        CONF_URL: info["url"],
                        CONF_REGO_TYPE: info["rego_type"],
                    },
                )

        return self.async_show_form(
            step_id="user",
            data_schema=build_schema(),
            errors=errors,
        )

    async def async_step_reconfigure(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Handle reconfiguration of an existing entry."""
        errors: dict[str, str] = {}
        entry = self._get_reconfigure_entry()

        if user_input is not None:
            try:
                info = await validate_input(user_input)
            except CannotConnect as err:
                _LOGGER.debug("Cannot connect to heat pump during reconfigure: %s", err)
                errors["base"] = "cannot_connect"
            except Exception:
                _LOGGER.exception("Unexpected exception during reconfigure")
                errors["base"] = "unknown"
            else:
                existing_entry = self._find_existing_entry_by_url(info["url"])
                if (
                    existing_entry is not None
                    and existing_entry.entry_id != entry.entry_id
                ):
                    return self.async_abort(reason="already_configured")

                return self.async_update_reload_and_abort(
                    entry,
                    data_updates={
                        CONF_URL: info["url"],
                        CONF_REGO_TYPE: info["rego_type"],
                    },
                )

        return self.async_show_form(
            step_id="reconfigure",
            data_schema=build_schema(
                entry.data[CONF_URL],
                entry.data.get(CONF_REGO_TYPE, DEFAULT_REGO_TYPE),
            ),
            errors=errors,
        )
