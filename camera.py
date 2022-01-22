# custom_components\yi_hack\camera.py

from homeassistant.components.camera import Camera
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_NAME
from homeassistant.core import HomeAssistant


async def async_setup_entry(hass: HomeAssistant, config: ConfigEntry, async_add_entities, discovery_info=None):
    camera = Camera()
    camera.name = config[CONF_NAME]
    async_add_entities([camera])