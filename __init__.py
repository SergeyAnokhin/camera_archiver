from datetime import timedelta
import logging, threading, json, ast

from homeassistant.helpers.debounce import Debouncer

from .common.transfer_state import TransferState
from .common.transfer_runner import TransferRunner
from homeassistant.helpers.update_coordinator import REQUEST_REFRESH_DEFAULT_COOLDOWN, DataUpdateCoordinator, UpdateFailed
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_MAC, CONF_NAME, CONF_SCAN_INTERVAL, EVENT_HOMEASSISTANT_STARTED
from homeassistant.core import Config, CoreState, HomeAssistant, ServiceCall

from .const import (ATTR_TRANSFER_RESULT, DOMAIN, CONF_ENABLE, SENSOR_NAME_TO_COPY_FILES, SERVICE_RUN)

PLATFORMS = ["sensor", "binary_sensor", "switch"]

_LOGGER = logging.getLogger(__name__)

lock = threading.Lock()
runner: TransferRunner = None
# def setup_platform(hass, config, add_devices, discovery_info=None):
#     """Setup the sensor platform."""
#     _LOGGER.info("Start setup_platform")

# HISTORY EXAMPLE : homeassistant\components\history_stats\sensor.py 228

def get_coordinator(hass: HomeAssistant, instanceName: str, config: ConfigEntry = None, set_update_method=False):
    if config:
        runner = TransferRunner(config, hass)

    async def async_get_status():
        _LOGGER.info(f"|{instanceName}| Call Callback sensor.py:get_coordinator.async_get_status() ")
        coordinatorInst = hass.data[DOMAIN][instanceName]
        if not hass.is_running:
            raise UpdateFailed(f"|{instanceName}| Hass starting in progress")

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
        #hass.data[DOMAIN].update_interval = timedelta(days=10)


    with lock:
        _LOGGER.debug(f"|{instanceName}| Check coordinator existing")
        if instanceName in hass.data[DOMAIN]:
            coordinatorInst = hass.data[DOMAIN][instanceName]
            _LOGGER.debug(f"|{instanceName}| Coordinator reuse Succes: ID# {id(coordinatorInst)}")
        else:
            coordinatorInst = DataUpdateCoordinator(
                hass,
                logging.getLogger(__name__),
                name=DOMAIN,
                update_interval = timedelta(days=10),
                request_refresh_debouncer=Debouncer(
                    hass, _LOGGER, cooldown=600, immediate=False
                )
            )
            _LOGGER.debug(f"|{instanceName}| Coordinator created: ID# {id(coordinatorInst)}")
            coordinatorInst.last_update_success = False
            coordinatorInst.data = {
                    CONF_ENABLE: True,
                }
            hass.data[DOMAIN][instanceName] = coordinatorInst
            

    # def _enable_scheduled_speedtests(*_):
    #     """Activate the data update coordinator."""
    #     coordinatorInst.update_interval = timedelta(days = 10)

    if config: # only sensor has right config for async_get_status
        # coordinatorInst.update_interval = config[CONF_SCAN_INTERVAL]
        coordinatorInst.update_method = async_get_status

    # if hass.state == CoreState.running:
    #     _enable_scheduled_speedtests()
    # else:
    #     # Running a speed test during startup can prevent
    #     # integrations from being able to setup because it
    #     # can saturate the network interface.
    #     hass.bus.async_listen_once(
    #         EVENT_HOMEASSISTANT_STARTED, _enable_scheduled_speedtests
    #     )

    # scan_interval = config.get(CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL)
    # await async_setup_sensor_registry_updates(hass, sensor_registry, scan_interval)

    return coordinatorInst

async def async_setup(hass: HomeAssistant, global_config: Config):
    """Set up this integration using YAML."""
    
    # config = global_config[DOMAIN]
    
    # archiver = CameraArchive(hass, config)
    # archiver.FileCopiedCallBack = FileTransferCallback

    async def _service_run(call: ServiceCall) -> None:
        _LOGGER.info("service camera archive call")
        data = dict(call.data)
        return

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
