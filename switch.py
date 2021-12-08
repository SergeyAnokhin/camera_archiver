#import asyncio
import logging

from homeassistant.components.switch import SwitchEntity
from homeassistant.const import (CONF_HOST, CONF_MAC, CONF_NAME,
                                  CONF_PASSWORD, CONF_PORT, CONF_USERNAME)
from homeassistant.core import ServiceCall
# from homeassistant.helpers.device_registry import CONNECTION_NETWORK_MAC

# from .common import (get_privacy, set_power_off_in_progress,
#                      set_power_on_in_progress, set_privacy)
from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass, config_entry, async_add_entities):
    async_add_entities([CameraArchiverSwitch(hass, config_entry)], True)
    _LOGGER.info("Start switch async_setup_entry")

def setup_platform(hass, config, add_devices, discovery_info=None):
    """Setup the sensor platform."""
    add_devices([CameraArchiverEnabler(hass, config)])
    _LOGGER.info("Start switch setup_platform")

    # async def archive(call: ServiceCall):
    #     _LOGGER.info("service archive call")
    # hass.services.register(DOMAIN, 'archive2', archive)


class CameraArchiverEnabler(SwitchEntity):
    """Representation of a Yi Camera Switch."""

    def __init__(self, hass, config):
        self._state = None
        self._device_name = config[CONF_NAME]
        self._unique_id = "CameraArchiverSwitch_swpr"
        _LOGGER.info("Start switch __init__")

    def update(self):
        """Return the state of the switch."""
        pass

    def turn_off(self):
        self._state = False

    def turn_on(self):
        self._state = True

    @property
    def is_on(self):
        """Return true if the switch is on."""
        return self._state

    @property
    def name(self):
        """Return the name of the device."""
        return "camera_archiver_switch"

    @property
    def unique_id(self) -> str:
        """Return the unique ID of the device."""
        return self._unique_id

    @property
    def device_info(self):
        """Return device specific attributes."""
        return {
            "name": self._device_name,
            "model": DOMAIN,
        }
