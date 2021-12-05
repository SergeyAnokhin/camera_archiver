from datetime import timedelta
import logging, os

from homeassistant.helpers.update_coordinator import DataUpdateCoordinator
from .CameraArchiver import CameraArchive

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_MAC, CONF_NAME
from homeassistant.core import Config, HomeAssistant, ServiceCall

from .FtpTransfer import FtpTransfer

from .const import (DOMAIN, HA_FILES_COPIED, HA_NOT_PROCESSED_FILES)

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
    # config = global_config[DOMAIN]
    
    # archiver = CameraArchive(hass, config)
    # archiver.FileCopiedCallBack = FileTransferCallback

    # async def service_archive_private(call: ServiceCall) -> None:
    #     _LOGGER.info("service camera archive call")
    #     archiver.run(call)

    # hass.services.async_register(DOMAIN, 'archive', service_archive_private)

    data = {
        HA_NOT_PROCESSED_FILES: 100,
        HA_FILES_COPIED: 0
    }


    async def async_get_status():
        _LOGGER.info(f"Get Status Call")
        coordinator: DataUpdateCoordinator = hass.data[DOMAIN]
        # data[HA_NOT_PROCESSED_FILES] = data[HA_NOT_PROCESSED_FILES] - 1
        # data[HA_FILES_COPIED] = data[HA_FILES_COPIED] - 1
        coordinator.data[HA_NOT_PROCESSED_FILES] = coordinator.data[HA_NOT_PROCESSED_FILES] - 1
        coordinator.data[HA_FILES_COPIED] = coordinator.data[HA_FILES_COPIED] + 1
        return coordinator.data

    coordinator = DataUpdateCoordinator(
        hass,
        logging.getLogger(__name__),
        name=DOMAIN,
        update_method=async_get_status,
        update_interval=timedelta(seconds=5),
    )
    coordinator.data = data

    hass.data[DOMAIN] = coordinator

    return True

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up from a config entry."""
    _LOGGER.info("Start async_setup_entry")
    hass.data.setdefault(DOMAIN, {})
    return True

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Unload a config entry."""
    _LOGGER.info("Start async_unload_entry")
