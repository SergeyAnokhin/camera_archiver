#import asyncio
import logging

from homeassistant.helpers.restore_state import RestoreEntity
from . import get_coordinator

from homeassistant.components.switch import DEVICE_CLASS_SWITCH, SwitchEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import (CONF_NAME, STATE_OFF, STATE_ON)
from homeassistant.core import HomeAssistant, ServiceCall
from homeassistant.helpers.entity import DeviceInfo, ToggleEntity
from homeassistant.helpers.update_coordinator import CoordinatorEntity
# from homeassistant.helpers.device_registry import CONNECTION_NETWORK_MAC

# from .common import (get_privacy, set_power_off_in_progress,
#                      set_power_on_in_progress, set_privacy)
from .const import DOMAIN, CONF_ENABLE

_LOGGER = logging.getLogger(__name__)

async def async_setup_platform(hass: HomeAssistant, config: ConfigEntry, add_entities, discovery_info=None):
    coordinator = get_coordinator(hass, config[CONF_NAME])

    add_entities([
        CameraArchiverEnabler(coordinator, config),
    ])


class CameraArchiverEnabler(RestoreEntity, ToggleEntity):
    """Representation of a Yi Camera Switch."""

    def __init__(self, coordinator, config):
        self._attr_state = None
        self._attr_is_on = False
        self.coordinator = coordinator
        self._device_name = config[CONF_NAME]
        self._attr_name = self._device_name + " Enabler"
        self._attr_available = True

    async def update(self):
        self._attr_state = STATE_ON if self._attr_is_on else STATE_OFF
        self.schedule_update_ha_state()
        self.coordinator.data[CONF_ENABLE] = self._attr_is_on
        await self.coordinator.async_request_refresh()

    async def async_turn_on(self, **kwargs):
        """Turn the light on."""
        self._attr_is_on = True
        await self.update()

    async def async_turn_off(self, **kwargs):
        """Turn the entity off."""
        self._attr_is_on = False
        await self.update()

    async def async_added_to_hass(self):
        last_state = await self.async_get_last_state()
        _LOGGER.info(f"#{self._attr_name}# call async_get_last_state STATE={self._attr_state}")
        if last_state and last_state.state:
            self._attr_state = last_state.state
            _LOGGER.info(f"#{self._attr_name}# NEW_STATE={self._attr_state}")

    # @property
    # def device_class(self):
    #     """Return the class of this device, from component DEVICE_CLASSES."""
    #     return DEVICE_CLASS_SWITCH

    # @property
    # def available(self) -> bool:
    #     super().available
    #     return True

    # @property
    # def should_poll(self) -> bool:
    #     """No need to poll. Coordinator notifies entity of updates."""
    #     return False

    # @property
    # def device_info(self) -> DeviceInfo:
    #     """Device information."""
    #     return DeviceInfo(
    #         identifiers={
    #             # Unique identifiers within the domain
    #             (DOMAIN, self.unique_id)
    #         },
    #         manufacturer="TODO",
    #         model="TODO",
    #         name=self.name,
    #         sw_version="TODO",
    #     )

