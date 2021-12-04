import logging, os

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_MAC, CONF_NAME
from homeassistant.core import Config, HomeAssistant, ServiceCall

from .FtpTransfer import FtpTransfer

from .const import (DOMAIN)

PLATFORMS = ["sensor", "binary_sensor", "switch"]

_LOGGER = logging.getLogger(__name__)


# def setup_platform(hass, config, add_devices, discovery_info=None):
#     """Setup the sensor platform."""
#     _LOGGER.info("Start setup_platform")

CFG = {}

def FileTransferCallback(stat):
    print(f"🔁 Callback: {stat}")

def service_archive(call, cfg):
        _LOGGER.info("service archive call")
        
        for config in cfg["entities"]:
            config["local_storage"] = cfg["local_storage"]
            tr = FtpTransfer(config)
            tr.OnFileTransferCallback(FileTransferCallback)
            tr.Copy(max=1)



async def async_setup(hass: HomeAssistant, config: Config):
    """Set up this integration using YAML."""
    cfg = config[DOMAIN]
    
    async def service_archive_private(call: ServiceCall) -> None:
        service_archive(call, cfg)

    hass.services.async_register(DOMAIN, 'archive', service_archive_private)
    return True

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up yi-hack from a config entry."""
    _LOGGER.info("Start async_setup_entry")
    hass.data.setdefault(DOMAIN, {})
    return True

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Unload a config entry."""
    _LOGGER.info("Start async_unload_entry")
