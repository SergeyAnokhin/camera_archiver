"""Config flow for yi_hack integration."""

import logging

import voluptuous as vol
from homeassistant import config_entries
from homeassistant.const import (
    CONF_USERNAME,
)

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

DATA_SCHEMA = {
    vol.Optional(CONF_USERNAME, default="root"): str,
}


class CamArchFlowHandler(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a yi-hack config flow."""

    VERSION = 1
    CONNECTION_CLASS = config_entries.CONN_CLASS_LOCAL_PUSH

    async def async_step_user(self, user_input=None):
        """Handle a flow initiated by the user."""
        errors = {}

        if user_input is not None:
            user = user_input[CONF_USERNAME]

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(DATA_SCHEMA),
            errors=errors,
        )
