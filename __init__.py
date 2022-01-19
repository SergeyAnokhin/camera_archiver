from datetime import timedelta
import logging, threading, json, ast
from config.custom_components.camera_archiver.transfer_manager import TransferManager
from homeassistant.components import mqtt

from homeassistant.helpers.debounce import Debouncer

from .common.transfer_state import TransferState
from .common.transfer_runner import TransferRunner
from homeassistant.helpers.update_coordinator import REQUEST_REFRESH_DEFAULT_COOLDOWN, DataUpdateCoordinator, UpdateFailed
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_MAC, CONF_NAME, CONF_SCAN_INTERVAL, EVENT_HOMEASSISTANT_STARTED
from homeassistant.core import Config, CoreState, HomeAssistant, ServiceCall, callback

from .const import (ATTR_TRANSFER_RESULT, DOMAIN, CONF_ENABLE, SENSOR_NAME_TO_COPY_FILES, SERVICE_RUN)

PLATFORMS = ["sensor", "binary_sensor", "switch"]

_LOGGER = logging.getLogger(__name__)


# def setup_platform(hass, config, add_devices, discovery_info=None):
#     """Setup the sensor platform."""
#     _LOGGER.info("Start setup_platform")

# HISTORY EXAMPLE : homeassistant\components\history_stats\sensor.py 228

manager: TransferManager = None

async def async_setup(hass: HomeAssistant, global_config: Config):
    """Set up this integration using YAML."""

    manager = TransferManager(hass)

    # config = global_config[DOMAIN]
    
    # archiver = CameraArchive(hass, config)
    # archiver.FileCopiedCallBack = FileTransferCallback

    # @callback
    # def message_received(msg):
    #     """Handle new MQTT messages."""
    #     data = msg.payload

    # mqtt_subscription = await mqtt.async_subscribe(
    #     hass, "yicam_1080p/#", message_received
    # )

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
