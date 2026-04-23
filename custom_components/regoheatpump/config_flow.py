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
from .rego600 import HeatPump, RegoError, RegoType

_LOGGER = logging.getLogger(__name__)


class CannotConnect(Exception):
    """Error to indicate we cannot connect."""


def build_schema(
    url_default: Any = vol.UNDEFINED,
    rego_type_default: RegoType = DEFAULT_REGO_TYPE,
) -> vol.Schema:
    """Build config flow schema."""
    return vol.Schema(
        {
            vol.Required(CONF_URL, default=url_default): str,
            vol.Required(
                CONF_REGO_TYPE, default=rego_type_default.value
            ): SelectSelector(
                SelectSelectorConfig(
                    options=[
                        {"value": rego_type.value, "label": label}
                        for rego_type, label in REGO_TYPE_LABELS.items()
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


async def check_connection(url: str, rego_type: RegoType):
    """Validate if we can successfully connect to selected url."""

    hp = HeatPump.connect(url=url, rego_type=rego_type)

    try:
        await hp.verify(retry=0)
    except (OSError, RegoError) as err:
        raise CannotConnect from err
    finally:
        await hp.dispose()


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
        """Handle the initial config step."""
        errors: dict[str, str] = {}

        if user_input is not None:
            try:
                url = normalize_connection_url(user_input[CONF_URL])
                rego_type = RegoType(user_input[CONF_REGO_TYPE])

                if self._find_existing_entry_by_url(url) is not None:
                    return self.async_abort(reason="already_configured")
                await check_connection(url, rego_type)

            except CannotConnect as err:
                _LOGGER.debug("Cannot connect to heat pump: %s", err)
                errors["base"] = "cannot_connect"
            except Exception:
                _LOGGER.exception("Unexpected exception during config flow")
                errors["base"] = "unknown"
            else:
                return self.async_create_entry(
                    title=f"Rego Heat Pump ({REGO_TYPE_LABELS[rego_type]}, {url})",
                    data={
                        CONF_URL: url,
                        CONF_REGO_TYPE: rego_type.value,
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
                url = normalize_connection_url(user_input[CONF_URL])
                rego_type = RegoType(user_input[CONF_REGO_TYPE])

                existing_entry = self._find_existing_entry_by_url(url)
                if (
                    existing_entry is not None
                    and existing_entry.entry_id != entry.entry_id
                ):
                    return self.async_abort(reason="already_configured")

                await check_connection(url, rego_type)
                return self.async_update_reload_and_abort(
                    entry,
                    data_updates={
                        CONF_URL: url,
                        CONF_REGO_TYPE: rego_type.value,
                    },
                )

            except CannotConnect as err:
                _LOGGER.debug("Cannot connect to heat pump during reconfigure: %s", err)
                errors["base"] = "cannot_connect"
            except Exception:
                _LOGGER.exception("Unexpected exception during reconfigure")
                errors["base"] = "unknown"

        rego_type_str = entry.data.get(CONF_REGO_TYPE, DEFAULT_REGO_TYPE.value)
        rego_type = (
            RegoType(rego_type_str)
            if rego_type_str in REGO_TYPE_LABELS
            else DEFAULT_REGO_TYPE
        )

        return self.async_show_form(
            step_id="reconfigure",
            data_schema=build_schema(
                entry.data[CONF_URL],
                rego_type,
            ),
            errors=errors,
        )
