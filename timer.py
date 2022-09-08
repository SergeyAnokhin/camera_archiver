from .common.helper import getLogger
from homeassistant.components.timer import Timer
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import ATTR_NAME, CONF_NAME
from homeassistant.core import HomeAssistant
from homeassistant.helpers.typing import ConfigType

_PLATFORM = "timer"
PLATFORM = "timer"


async def async_setup_entry(
    hass: HomeAssistant, config: ConfigEntry, async_add_entities
):
    logger = getLogger(__name__, "Unknown")


async def async_setup(hass: HomeAssistant, config: ConfigType) -> bool:
    logger = getLogger(__name__, "Unknown")


async def async_setup_platform(
    hass: HomeAssistant, config: ConfigEntry, add_entities, discovery_info=None
):
    timer_config = {}
    timer_config[CONF_NAME] = config[CONF_NAME]
    add_entities([Timer(timer_config)])
