from datetime import timedelta
import logging, threading, json, ast

from .common.transfer_state import TransferState
from .common.transfer_runner import TransferRunner
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_MAC, CONF_NAME, CONF_SCAN_INTERVAL
from homeassistant.core import Config, HomeAssistant, ServiceCall

from .const import (ATTR_TRANSFER_RESULT, DOMAIN, CONF_ENABLE, SENSOR_NAME_TO_COPY_FILES, SERVICE_RUN)

PLATFORMS = ["sensor", "binary_sensor", "switch"]

_LOGGER = logging.getLogger(__name__)

lock = threading.Lock()

# def setup_platform(hass, config, add_devices, discovery_info=None):
#     """Setup the sensor platform."""
#     _LOGGER.info("Start setup_platform")

# HISTORY EXAMPLE : homeassistant\components\history_stats\sensor.py 228

def get_coordinator(hass: HomeAssistant, instanceName: str, config: ConfigEntry = None, set_update_method=False):
    async def async_get_status():
        _LOGGER.info(f"|{instanceName}| Call Callback sensor.py:get_coordinator.async_get_status() ")
        coordinatorInst = hass.data[DOMAIN][instanceName]
        runner = TransferRunner(config, hass)
        result: TransferState = None
        if not coordinatorInst.data.get(CONF_ENABLE, False):
            result = runner.stat()
        else:
            result = runner.run()
        coordinatorInst.data[ATTR_TRANSFER_RESULT] = result
        return coordinatorInst.data

    _LOGGER.debug(f"|{instanceName}| Call sensor.py:get_coordinator() {instanceName} HasConfig:{'Yes' if config else 'No'}")

    if DOMAIN not in hass.data:
        hass.data[DOMAIN] = {}

    with lock:
        _LOGGER.debug(f"|{instanceName}| Check coordinator existing")
        if instanceName in hass.data[DOMAIN]:
            coordinatorInst = hass.data[DOMAIN][instanceName]
            _LOGGER.debug(f"|{instanceName}| Coordinator reuse Succes: ID# {id(coordinatorInst)}")
        else:
            coordinatorInst = DataUpdateCoordinator(
                hass,
                logging.getLogger(__name__),
                name=DOMAIN
            )
            _LOGGER.debug(f"|{instanceName}| Coordinator created: ID# {id(coordinatorInst)}")
            coordinatorInst.last_update_success = False
            coordinatorInst.data = {
                    CONF_ENABLE: True,
                }
            hass.data[DOMAIN][instanceName] = coordinatorInst

    if config: # only sensor has right config for async_get_status
        coordinatorInst.update_interval = config[CONF_SCAN_INTERVAL]
        coordinatorInst.update_method = async_get_status

    return coordinatorInst

async def async_setup(hass: HomeAssistant, global_config: Config):
    """Set up this integration using YAML."""
    
    # config = global_config[DOMAIN]
    
    # archiver = CameraArchive(hass, config)
    # archiver.FileCopiedCallBack = FileTransferCallback

    async def _service_run(call: ServiceCall) -> None:
        _LOGGER.info("service camera archive call")
        data = dict(call.data)
        description = data['description']
        js = ast.literal_eval(description)
        name = data['name']
        id = description.id

    hass.services.async_register(DOMAIN, SERVICE_RUN, _service_run)
    return True

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up from a config entry."""
    _LOGGER.info("Start async_setup_entry")
    hass.data.setdefault(DOMAIN, {})
    return True

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Unload a config entry."""
    _LOGGER.info("Start async_unload_entry")
