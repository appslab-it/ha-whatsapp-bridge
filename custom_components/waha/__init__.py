"""WAHA WhatsApp integration."""
from __future__ import annotations

import asyncio
import logging

import aiohttp
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant, ServiceCall
from homeassistant.exceptions import ConfigEntryNotReady, HomeAssistantError
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .const import CONF_API_KEY, CONF_HOST, CONF_PORT, CONF_SESSION, DOMAIN

_LOGGER = logging.getLogger(__name__)
PLATFORMS: list[Platform] = [Platform.SENSOR]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    host = entry.data[CONF_HOST]
    port = entry.data[CONF_PORT]
    api_key = entry.data.get(CONF_API_KEY, "")
    session_name = entry.data[CONF_SESSION]

    base_url = f"http://{host}:{port}"
    headers: dict[str, str] = {}
    if api_key:
        headers["X-Api-Key"] = api_key

    http_session = async_get_clientsession(hass)

    try:
        async with asyncio.timeout(10):
            async with http_session.get(
                f"{base_url}/api/health", headers=headers
            ) as resp:
                if resp.status not in (200, 204):
                    raise ConfigEntryNotReady(
                        f"WAHA returned HTTP {resp.status} at {base_url}"
                    )
    except aiohttp.ClientError as err:
        raise ConfigEntryNotReady(
            f"Cannot connect to WAHA at {base_url}: {err}"
        ) from err

    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = {
        "base_url": base_url,
        "headers": headers,
        "session_name": session_name,
        "http_session": http_session,
    }

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    _register_services(hass)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)
        if not hass.data[DOMAIN]:
            hass.data.pop(DOMAIN)
            for svc in ("send_message", "send_image", "send_video", "send_file", "send_voice"):
                hass.services.async_remove(DOMAIN, svc)
    return unload_ok


def _get_client(hass: HomeAssistant, session_name: str | None) -> dict:
    entries = hass.data.get(DOMAIN, {})
    if not entries:
        raise HomeAssistantError("WAHA integration non configurata")
    if session_name:
        for data in entries.values():
            if data["session_name"] == session_name:
                return data
        raise HomeAssistantError(
            f"Nessuna configurazione WAHA trovata per la sessione '{session_name}'"
        )
    return next(iter(entries.values()))


def _register_services(hass: HomeAssistant) -> None:
    if hass.services.has_service(DOMAIN, "send_message"):
        return

    async def _post(data: dict, path: str, payload: dict) -> None:
        headers = {**data["headers"], "Content-Type": "application/json"}
        async with asyncio.timeout(15):
            async with data["http_session"].post(
                data["base_url"] + path, json=payload, headers=headers
            ) as resp:
                if resp.status not in (200, 201):
                    body = await resp.text()
                    raise HomeAssistantError(
                        f"WAHA API error {resp.status}: {body}"
                    )

    async def send_message(call: ServiceCall) -> None:
        data = _get_client(hass, call.data.get("session_name"))
        await _post(
            data,
            f"/api/{data['session_name']}/sendText",
            {
                "chatId": call.data["phone"] + "@c.us",
                "text": call.data["message"],
            },
        )

    async def send_image(call: ServiceCall) -> None:
        data = _get_client(hass, call.data.get("session_name"))
        await _post(
            data,
            f"/api/{data['session_name']}/sendImage",
            {
                "chatId": call.data["phone"] + "@c.us",
                "file": {"url": call.data["url"]},
                "caption": call.data.get("caption", ""),
            },
        )

    async def send_video(call: ServiceCall) -> None:
        data = _get_client(hass, call.data.get("session_name"))
        await _post(
            data,
            f"/api/{data['session_name']}/sendVideo",
            {
                "chatId": call.data["phone"] + "@c.us",
                "file": {"url": call.data["url"]},
                "caption": call.data.get("caption", ""),
            },
        )

    async def send_file(call: ServiceCall) -> None:
        data = _get_client(hass, call.data.get("session_name"))
        await _post(
            data,
            f"/api/{data['session_name']}/sendFile",
            {
                "chatId": call.data["phone"] + "@c.us",
                "file": {"url": call.data["url"]},
                "filename": call.data.get("filename", ""),
            },
        )

    async def send_voice(call: ServiceCall) -> None:
        data = _get_client(hass, call.data.get("session_name"))
        await _post(
            data,
            f"/api/{data['session_name']}/sendVoice",
            {
                "chatId": call.data["phone"] + "@c.us",
                "file": {"url": call.data["url"]},
            },
        )

    hass.services.async_register(DOMAIN, "send_message", send_message)
    hass.services.async_register(DOMAIN, "send_image", send_image)
    hass.services.async_register(DOMAIN, "send_video", send_video)
    hass.services.async_register(DOMAIN, "send_file", send_file)
    hass.services.async_register(DOMAIN, "send_voice", send_voice)
