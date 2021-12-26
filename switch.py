#import asyncio
import logging

from homeassistant.helpers.restore_state import RestoreEntity
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
    coordinator = get_coordinator(hass, config[CONF_NAME])

    add_entities([
        CameraArchiverEnabler(coordinator, config),
    ])


class CameraArchiverEnabler(RestoreEntity, SwitchEntity):
    """Representation of a Yi Camera Switch."""

    def __init__(self, coordinator, config):
        # super().__init__(coordinator)
        self._state = None
        self._device_name = config[CONF_NAME]
        self._name = self._device_name + " Enabler"
        # _LOGGER.debug(f"|{self._name}| Switch created: with coordinator ID# {id(self.coordinator)}")

    def update(self):
        """Return the state of the switch."""
        pass


    async def async_turn_on(self, **kwargs):
        """Turn the light on."""
        self._attr_is_on = True
        self._state = 'on'
        self.schedule_update_ha_state()
        # self.coordinator.data[CONF_ENABLE] = True
        #_LOGGER.debug(f"|{self._name}| Switch ON: with coordinator ID# {id(self.coordinator)}")
        # await self.coordinator.async_request_refresh()

    async def async_turn_off(self, **kwargs):
        """Turn the entity off."""
        self._attr_is_on = False
        self._state = 'off'
        self.schedule_update_ha_state()
        # self.coordinator.data[CONF_ENABLE] = False
        # _LOGGER.debug(f"|{self._name}| Switch OFF: with coordinator ID# {id(self.coordinator)}")
        # await self.coordinator.async_request_refresh()

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
    def is_on(self):
        """Return true if the switch is on."""
        return self._state == 'on'
        # _LOGGER.debug(f"|{self._name}| Switch CHECK: with coordinator ID# {id(self.coordinator)}")
        # if self.coordinator.data.get(CONF_ENABLE):
        #     return True
        # return False

    @property
    def name(self):
        """Return the name of the device."""
        return self._name

    def switch(self, new_state):
        self._state = new_state
        # self.coordinator.data[CONF_ENABLE] = on

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

    async def async_added_to_hass(self):

        last_state = await self.async_get_last_state()
        _LOGGER.info(f"#{self._name}# call async_get_last_state STATE={self._state}")
        if last_state and last_state.state:
            self._state = last_state.state
            _LOGGER.info(f"#{self._name}# NEW_STATE={self._state}")

    # async def async_turn_on(self, **kwargs):
    #     """Turn the switch on."""
    #     await self.hass.async_add_executor_job(self._api.wifi.set_wifi, True)

    # async def async_turn_off(self, **kwargs):
    #     """Turn the switch off."""
    #     # parameters = {"Enable": "false", "Status": "false"}
    #     await self.hass.async_add_executor_job(self._api.wifi.set_wifi, False)
