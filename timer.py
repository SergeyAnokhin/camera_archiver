from homeassistant.components.timer import Timer
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_NAME
from homeassistant.core import HomeAssistant
from homeassistant.helpers.typing import ConfigType


async def async_setup_entry(hass: HomeAssistant, config: ConfigEntry, async_add_entities):
    pass

async def async_setup(hass: HomeAssistant, config: ConfigType) -> bool:
    pass

async def async_setup_platform(hass: HomeAssistant, config: ConfigEntry, add_entities, discovery_info=None):
    timer_config = {}
    timer_config[CONF_NAME] = config[CONF_NAME]
    add_entities([Timer(timer_config)])