import logging, os
from .CameraArchiver import CameraArchive

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
    _LOGGER.Info(f"🔁 Callback: {stat}")

async def async_setup(hass: HomeAssistant, global_config: Config):
    """Set up this integration using YAML."""
    config = global_config[DOMAIN]
    
    archiver = CameraArchive(hass, config)
    archiver.FileCopiedCallBack = FileTransferCallback

    async def service_archive_private(call: ServiceCall) -> None:
        _LOGGER.info("service camera archive call")
        archiver.run(call)

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
