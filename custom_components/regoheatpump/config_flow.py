"""Config flow for the Rego Heat Pump integration."""

from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol

from homeassistant.config_entries import ConfigFlow, ConfigFlowResult
from homeassistant.const import CONF_URL
from homeassistant.core import HomeAssistant

from .const import DOMAIN
from .rego600 import HeatPump

_LOGGER = logging.getLogger(__name__)

STEP_USER_DATA_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_URL): str,
    }
)


async def validate_input(hass: HomeAssistant, data: dict[str, Any]) -> dict[str, Any]:
    """Validate the user input allows us to connect."""

    hp = HeatPump.connect(url=data[CONF_URL])

    try:
        await hp.verify(retry=0)
    finally:
        await hp.dispose()

    return {"address": data[CONF_URL]}


class RegoConfigFlow(ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Rego Heat Pump."""

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Handle the initial step."""
        errors: dict[str, str] = {}
        if user_input is not None:
            try:
                info = await validate_input(self.hass, user_input)
            except Exception as e:
                _LOGGER.exception("Unexpected exception")
                errors["base"] = str(e)
            else:
                return self.async_create_entry(title=info["address"], data=user_input)

        return self.async_show_form(data_schema=STEP_USER_DATA_SCHEMA, errors=errors)
