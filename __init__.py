from datetime import timedelta
import logging, os

from .transfer_runner import TransferRunner
from .TransferState import TransferState
from .lib_directory.DirectoryTransfer import DirectoryTransfer
from .lib_ftp.FtpTransfer import FtpTransfer
from homeassistant.helpers.config_validation import string

from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_MAC, CONF_NAME
from homeassistant.core import Config, HomeAssistant, ServiceCall

from .const import (CONF_DIRECTORY, CONF_FROM, CONF_FTP, CONF_MQTT, DOMAIN, SENSOR_NAME_TO_COPY_FILES)

PLATFORMS = ["sensor", "binary_sensor", "switch"]

_LOGGER = logging.getLogger(__name__)

# def setup_platform(hass, config, add_devices, discovery_info=None):
#     """Setup the sensor platform."""
#     _LOGGER.info("Start setup_platform")

def get_coordinator(hass: HomeAssistant, config: ConfigEntry):
    instanceName = config[CONF_NAME]
    _LOGGER.debug(f"#{instanceName}# Call sensor.py:get_coordinator() {instanceName}")

    if DOMAIN not in hass.data:
        hass.data[DOMAIN] = {}

    if instanceName in hass.data[DOMAIN]:
        return hass.data[DOMAIN][instanceName]

    async def async_get_status():
        _LOGGER.info(f"#{instanceName}# Call Callback sensor.py:get_coordinator.async_get_status() ")
        coordinatorInst = hass.data[DOMAIN][instanceName]
        runner = TransferRunner(config, coordinatorInst)
        return runner.stat()

    coordinator = DataUpdateCoordinator(
        hass,
        logging.getLogger(__name__),
        name=DOMAIN,
        update_method=async_get_status,
        update_interval=timedelta(seconds=5),
    )
    coordinator.data = {}
    coordinator.last_update_success = False

    hass.data[DOMAIN][instanceName] = coordinator

    return coordinator



async def async_setup(hass: HomeAssistant, global_config: Config):
    """Set up this integration using YAML."""
    # config = global_config[DOMAIN]
    
    # archiver = CameraArchive(hass, config)
    # archiver.FileCopiedCallBack = FileTransferCallback

    # async def service_archive_private(call: ServiceCall) -> None:
    #     _LOGGER.info("service camera archive call")
    #     archiver.run(call)

    # hass.services.async_register(DOMAIN, 'archive', service_archive_private)

    # data = {
    #     SENSOR_NAME_TO_COPY_FILES: 100,
    #     SENSOR_NAME_FILES_COPIED: 0
    # }

    # async def async_get_status():
    #     _LOGGER.info(f"Get Status Call")
    #     data = hass.data[DOMAIN].data
    #     data[SENSOR_NAME_TO_COPY_FILES] = data[SENSOR_NAME_TO_COPY_FILES] - 1
    #     data[SENSOR_NAME_FILES_COPIED] = data[SENSOR_NAME_FILES_COPIED] + 1
    #     return data

    # coordinator = DataUpdateCoordinator(
    #     hass,
    #     logging.getLogger(__name__),
    #     name=DOMAIN,
    #     update_method=async_get_status,
    #     update_interval=timedelta(seconds=5),
    # )
    # coordinator.data = data

    # # instance_name = global_config[DOMAIN][CONF_NAME]
    # hass.data[DOMAIN] = coordinator

    return True

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up from a config entry."""
    _LOGGER.info("Start async_setup_entry")
    hass.data.setdefault(DOMAIN, {})
    return True

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Unload a config entry."""
    _LOGGER.info("Start async_unload_entry")


# def get_coordinator(hass: HomeAssistant, config: Config):
#     instance_name = config[DOMAIN][CONF_NAME]
#     return hass.data[DOMAIN][instance_name]
