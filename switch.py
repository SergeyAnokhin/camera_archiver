#import asyncio
import logging
from . import get_coordinator

from homeassistant.components.switch import DEVICE_CLASS_SWITCH, SwitchEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import (CONF_NAME)
from homeassistant.core import HomeAssistant, ServiceCall
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity
# from homeassistant.helpers.device_registry import CONNECTION_NETWORK_MAC

# from .common import (get_privacy, set_power_off_in_progress,
#                      set_power_on_in_progress, set_privacy)
from .const import DOMAIN, CONF_ENABLE

_LOGGER = logging.getLogger(__name__)

async def async_setup_platform(hass: HomeAssistant, config: ConfigEntry, add_entities, discovery_info=None):
    coordinator = get_coordinator(hass, config)

    add_entities([
        CameraArchiverEnabler(coordinator, config),
    ])


class CameraArchiverEnabler(CoordinatorEntity, SwitchEntity):
    """Representation of a Yi Camera Switch."""

    def __init__(self, coordinator, config):
        super().__init__(coordinator)
        self._state = True
        self._device_name = config[CONF_NAME]
        self._name = self._device_name + " Enabler"

    def update(self):
        """Return the state of the switch."""
        pass


    async def async_turn_on(self, **kwargs):
        """Turn the light on."""
        self._attr_is_on = True
        self._state = True
        await self.coordinator.async_request_refresh()

    async def async_turn_off(self, **kwargs):
        """Turn the entity off."""
        self._attr_is_on = False
        self._state = False
        await self.coordinator.async_request_refresh()

    # def turn_off(self):
    #     """Turn the device off."""
    #     self._attr_is_on = False
    #     self._state = False
    #     self.coordinator.data[CONF_ENABLE] = False
    #     self.schedule_update_ha_state()

    # def turn_on(self):
    #     """Turn the switch on."""
    #     self._attr_is_on = True
    #     self._state = True
    #     self.coordinator.data[CONF_ENABLE] = True
    #     self.schedule_update_ha_state()

    @property
    def device_class(self):
        """Return the class of this device, from component DEVICE_CLASSES."""
        # if self.module.device == "plug":
        #     return DEVICE_CLASS_OUTLET
        return DEVICE_CLASS_SWITCH

    @property
    def available(self) -> bool:
        return True

    @property
    def is_on(self) -> bool:
        """Return true if the switch is on."""
        if self.coordinator.data.get(CONF_ENABLE):
            return True
        return False

    @property
    def name(self):
        """Return the name of the device."""
        return self._name

    def switch(self, on: bool):
        self._state = on
        self.coordinator.data[CONF_ENABLE] = on

    @property
    def device_info(self) -> DeviceInfo:
        """Device information."""
        return DeviceInfo(
            identifiers={
                # Unique identifiers within the domain
                (DOMAIN, self.unique_id)
            },
            manufacturer="TODO",
            model="TODO",
            name=self.name,
            sw_version="TODO",
        )

    # async def async_turn_on(self, **kwargs):
    #     """Turn the switch on."""
    #     await self.hass.async_add_executor_job(self._api.wifi.set_wifi, True)

    # async def async_turn_off(self, **kwargs):
    #     """Turn the switch off."""
    #     # parameters = {"Enable": "false", "Status": "false"}
    #     await self.hass.async_add_executor_job(self._api.wifi.set_wifi, False)
