import logging

import voluptuous as vol
from .common.helper import getLogger
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import (CONF_ENTITIES, CONF_HOST, CONF_NAME,
                                 CONF_PASSWORD, CONF_PLATFORM, CONF_SCAN_INTERVAL)
from homeassistant.core import Config, HomeAssistant
from homeassistant.helpers import config_validation as cv, discovery
from sqlalchemy import true

from .const import (CONF_CLEAN, CONF_COPIED_PER_RUN, CONF_DATETIME_PATTERN,
                    CONF_DIRECTORY, CONF_EMPTY_DIRECTORIES, CONF_FILES,
                    CONF_FROM, CONF_FTP, CONF_LOCAL_STORAGE, CONF_MQTT,
                    CONF_PATH, CONF_TO, CONF_TOPIC, CONF_TRIGGERS, CONF_USER,
                    DEFAULT_TIME_INTERVAL, DOMAIN)
from .common.transfer_builder import TransferBuilder

_LOGGER = logging.getLogger(__name__)

CLEAN_SCHEMA = vol.Schema({
    vol.Required(CONF_EMPTY_DIRECTORIES): cv.boolean,
    vol.Optional(CONF_FILES, default=[]): vol.All(
        cv.ensure_list, [cv.string]
    ),
})

FTP_SCHEMA = vol.Schema({
    vol.Required(CONF_PLATFORM): CONF_FTP,
    vol.Required(CONF_HOST): cv.string,
    vol.Required(CONF_USER): cv.string,
    vol.Required(CONF_PASSWORD): cv.string,
    vol.Required(CONF_PATH): cv.string,
    vol.Required(CONF_DATETIME_PATTERN): cv.string,
    vol.Optional(CONF_NAME): cv.string,
    vol.Optional(CONF_SCAN_INTERVAL, default=DEFAULT_TIME_INTERVAL): cv.time_period,
    vol.Optional(CONF_COPIED_PER_RUN, default=100): cv.positive_int,
    vol.Optional(CONF_CLEAN): CLEAN_SCHEMA,
})

DIRECTORY_SCHEMA = vol.Schema({
    vol.Required(CONF_PLATFORM): CONF_DIRECTORY,
    vol.Required(CONF_PATH): cv.string,
    vol.Required(CONF_DATETIME_PATTERN): cv.string,
    vol.Optional(CONF_NAME): cv.string,
    vol.Optional(CONF_SCAN_INTERVAL, default=DEFAULT_TIME_INTERVAL): cv.time_period,
    vol.Optional(CONF_COPIED_PER_RUN, default=100): cv.positive_int,
    vol.Optional(CONF_CLEAN): CLEAN_SCHEMA,
})

MQTT_SCHEMA = vol.Schema({
    vol.Required(CONF_PLATFORM): CONF_MQTT,
    vol.Required(CONF_TOPIC): cv.string,
    vol.Optional(CONF_NAME): cv.string,
})

TO_SCHEMA = FROM_SCHEMA = vol.All(cv.ensure_list, [
    vol.Any(FTP_SCHEMA, DIRECTORY_SCHEMA, MQTT_SCHEMA)
])

ENTITY_SCHEMA = vol.All(cv.ensure_list, [
    {
        vol.Required(CONF_NAME): cv.string,
        vol.Required(CONF_FROM): FROM_SCHEMA,
        vol.Required(CONF_TO): TO_SCHEMA,
        vol.Optional(CONF_LOCAL_STORAGE): cv.string,
        vol.Optional(CONF_TRIGGERS): vol.Any(cv.entity_ids, None),
    }
])

CONFIG_SCHEMA = vol.Schema(
    {
        DOMAIN: vol.Schema(
            {
                vol.Required(CONF_NAME): cv.string,
                vol.Required(CONF_ENTITIES): ENTITY_SCHEMA
            }, extra=vol.ALLOW_EXTRA)
    }, extra=vol.ALLOW_EXTRA)

PLATFORMS = ["sensor"]  # , "switch", "camera", "media_player", "binary_sensor"

# def setup_platform(hass, config, add_devices, discovery_info=None):
#     """Setup the sensor platform."""
#     _LOGGER.info("Start setup_platform")

# HISTORY EXAMPLE : homeassistant\components\history_stats\sensor.py 228

async def async_setup(hass: HomeAssistant, global_config: Config) -> bool:
    """Set up this integration using YAML."""

    if DOMAIN not in hass.data:
        hass.data[DOMAIN] = {}

    config = global_config[DOMAIN]
    entities = config[CONF_ENTITIES]

    for entity_config in entities:
        builder = TransferBuilder(hass, config, entity_config)
        builder.build()

        name = entity_config[CONF_NAME]
        hass.data[DOMAIN][name] = builder.build_coordinators_dict()
        logger = getLogger(__name__, name)
        logger.info(f"Init of manager finished with succes")

        for component in PLATFORMS:
            hass.async_create_task(discovery.async_load_platform(
                hass, component, DOMAIN, entity_config, global_config))

    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up from a config entry."""
    _LOGGER.info("Start async_setup_entry")
    hass.data.setdefault(DOMAIN, {})
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Unload a config entry."""
    _LOGGER.info("Start async_unload_entry")
