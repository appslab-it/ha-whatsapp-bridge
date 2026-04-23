"""Config flow for WAHA WhatsApp."""
from __future__ import annotations

import asyncio
import logging

import aiohttp
import voluptuous as vol
from homeassistant.config_entries import ConfigFlow, ConfigFlowResult
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .const import (
    CONF_API_KEY,
    CONF_HOST,
    CONF_PORT,
    CONF_SESSION,
    DEFAULT_PORT,
    DEFAULT_SESSION,
    DOMAIN,
)

_LOGGER = logging.getLogger(__name__)


class WahaConfigFlow(ConfigFlow, domain=DOMAIN):
    VERSION = 1

    async def async_step_user(
        self, user_input: dict | None = None
    ) -> ConfigFlowResult:
        errors: dict[str, str] = {}

        if user_input is not None:
            host = user_input[CONF_HOST]
            port = user_input[CONF_PORT]
            api_key = user_input.get(CONF_API_KEY, "")
            session_name = user_input[CONF_SESSION]

            headers: dict[str, str] = {}
            if api_key:
                headers["X-Api-Key"] = api_key

            try:
                http_session = async_get_clientsession(self.hass)
                async with asyncio.timeout(10):
                    async with http_session.get(
                        f"http://{host}:{port}/ping", headers=headers
                    ) as resp:
                        if resp.status not in (200, 204):
                            errors["base"] = "cannot_connect"
            except (aiohttp.ClientError, TimeoutError):
                errors["base"] = "cannot_connect"
            except Exception:
                _LOGGER.exception("Unexpected error connecting to WAHA")
                errors["base"] = "unknown"

            if not errors:
                await self.async_set_unique_id(f"{host}:{port}:{session_name}")
                self._abort_if_unique_id_configured()
                return self.async_create_entry(
                    title=f"WAHA ({session_name})",
                    data={
                        CONF_HOST: host,
                        CONF_PORT: port,
                        CONF_API_KEY: api_key,
                        CONF_SESSION: session_name,
                    },
                )

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_HOST, default="localhost"): str,
                    vol.Required(CONF_PORT, default=DEFAULT_PORT): int,
                    vol.Optional(CONF_API_KEY, default=""): str,
                    vol.Required(CONF_SESSION, default=DEFAULT_SESSION): str,
                }
            ),
            errors=errors,
        )
