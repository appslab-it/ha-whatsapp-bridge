"""WhatsApp Bridge session status sensor."""
from __future__ import annotations

import asyncio
import logging
from datetime import timedelta

import aiohttp
from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import (
    CoordinatorEntity,
    DataUpdateCoordinator,
    UpdateFailed,
)

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    data = hass.data[DOMAIN][entry.entry_id]
    coordinator = WhatsAppBridgeCoordinator(hass, data)
    await coordinator.async_config_entry_first_refresh()
    async_add_entities([WhatsAppBridgeSessionSensor(coordinator, entry, data["session_name"])])


class WhatsAppBridgeCoordinator(DataUpdateCoordinator):
    def __init__(self, hass: HomeAssistant, data: dict) -> None:
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=timedelta(seconds=30),
        )
        self._waha = data

    async def _async_update_data(self) -> dict:
        session_name = self._waha["session_name"]
        url = f"{self._waha['base_url']}/api/sessions/{session_name}"
        try:
            async with asyncio.timeout(10):
                async with self._waha["http_session"].get(
                    url, headers=self._waha["headers"]
                ) as resp:
                    if resp.status == 200:
                        return await resp.json()
                    return {"status": "unknown"}
        except aiohttp.ClientError as err:
            raise UpdateFailed(f"Cannot reach WhatsApp Bridge: {err}") from err


class WhatsAppBridgeSessionSensor(CoordinatorEntity, SensorEntity):
    _attr_icon = "mdi:whatsapp"
    _attr_has_entity_name = True
    _attr_name = "Session Status"

    def __init__(
        self,
        coordinator: WhatsAppBridgeCoordinator,
        entry: ConfigEntry,
        session_name: str,
    ) -> None:
        super().__init__(coordinator)
        self._attr_unique_id = f"{entry.entry_id}_session_status"
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, entry.entry_id)},
            name=f"WhatsApp Bridge ({session_name})",
            manufacturer="devlikeapro / WAHA",
            model="WhatsApp HTTP API",
        )

    @property
    def native_value(self) -> str | None:
        if self.coordinator.data:
            return self.coordinator.data.get("status")
        return None

    @property
    def extra_state_attributes(self) -> dict:
        if not self.coordinator.data:
            return {}
        return {k: v for k, v in self.coordinator.data.items() if k != "status"}
