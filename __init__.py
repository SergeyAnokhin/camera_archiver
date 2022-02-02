import logging
from enum import Enum

import voluptuous as vol
from homeassistant.const import (CONF_ENTITY_ID, CONF_HOST, CONF_ID,
                                 CONF_PASSWORD, CONF_PLATFORM,
                                 CONF_SCAN_INTERVAL, CONF_SENSORS, CONF_TYPE,
                                 CONF_URL)
from homeassistant.core import Config, HomeAssistant
from homeassistant.helpers import config_validation as cv
from sqlalchemy import true

from .common.builder import Builder
from .common.helper import getLogger
from .const import (CONF_API, CONF_CAMERA, CONF_CLEAN, CONF_COMPONENT,
                    CONF_COMPONENTS, CONF_COPIED_PER_RUN,
                    CONF_DATETIME_PATTERN, CONF_DIRECTORY, CONF_ELASTICSEARCH,
                    CONF_EMPTY_DIRECTORIES, CONF_FILES, CONF_FILTER, CONF_FTP,
                    CONF_IMAP, CONF_INDEX, CONF_LISTENERS, CONF_MIMETYPE,
                    CONF_MQTT, CONF_PATH, CONF_PIPELINES, CONF_REGEX, CONF_SCHEDULER,
                    CONF_SENSOR, CONF_SWITCH, CONF_TOPIC, CONF_TRIGGERS, CONF_USER,
                    DEFAULT_TIME_INTERVAL, DOMAIN)

_LOGGER = logging.getLogger(__name__)


class ComponentPlatforms(Enum):
    MQTT = CONF_MQTT
    DIRECTORY: CONF_DIRECTORY
    FTP = CONF_FTP
    ELASTICSEARCH = CONF_ELASTICSEARCH
    API = CONF_API
    IMAP = CONF_IMAP


class SensorPlatforms(Enum):
    camera = CONF_CAMERA
    sensor = CONF_SENSOR
    switch = CONF_SWITCH


class TriggerPlatforms(Enum):
    SCHEDULER = CONF_SCHEDULER
    MQTT = CONF_MQTT
    SENSOR = CONF_SENSOR


COMPONENT_DEFAULT = vol.Schema({
    vol.Optional(CONF_ID): cv.string,
})

CLEAN_SCHEMA = vol.Schema({
    vol.Required(CONF_EMPTY_DIRECTORIES): cv.boolean,
    vol.Optional(CONF_FILES, default=[]): vol.All(
        cv.ensure_list, [cv.string]
    ),
})


FTP_SCHEMA = COMPONENT_DEFAULT.extend({
    vol.Required(CONF_PLATFORM): CONF_FTP,
    vol.Required(CONF_HOST): cv.string,
    vol.Required(CONF_USER): cv.string,
    vol.Required(CONF_PASSWORD): cv.string,
    vol.Required(CONF_PATH): cv.string,
    vol.Required(CONF_DATETIME_PATTERN): cv.string,
    vol.Optional(CONF_COPIED_PER_RUN, default=100): cv.positive_int,
    vol.Optional(CONF_CLEAN): CLEAN_SCHEMA,
})

DIRECTORY_SCHEMA = COMPONENT_DEFAULT.extend({
    vol.Required(CONF_PLATFORM): CONF_DIRECTORY,
    vol.Required(CONF_PATH): cv.isdir,
    vol.Required(CONF_DATETIME_PATTERN): cv.string,
    vol.Optional(CONF_COPIED_PER_RUN, default=100): cv.positive_int,
    vol.Optional(CONF_CLEAN): CLEAN_SCHEMA,
})

MQTT_SCHEMA = COMPONENT_DEFAULT.extend({
    vol.Required(CONF_PLATFORM): CONF_MQTT,
    vol.Required(CONF_TOPIC): cv.string,
})

ELASTICSEARCH_SCHEMA = COMPONENT_DEFAULT.extend({
    vol.Required(CONF_PLATFORM): CONF_ELASTICSEARCH,
    vol.Required(CONF_INDEX): cv.string,
})

API_SCHEMA = COMPONENT_DEFAULT.extend({
    vol.Required(CONF_PLATFORM): CONF_API,
    vol.Required(CONF_URL): cv.url,
})

IMAP_SCHEMA = COMPONENT_DEFAULT.extend({
    vol.Required(CONF_PLATFORM): CONF_IMAP,
    vol.Required(CONF_HOST): cv.string,
    vol.Required(CONF_USER): cv.string,
    vol.Required(CONF_PASSWORD): cv.string,
    vol.Required(CONF_PATH): cv.string,
})

SCHEDULER_SCHEMA = COMPONENT_DEFAULT.extend({
    vol.Required(CONF_PLATFORM): CONF_SCHEDULER,
    vol.Required(CONF_SCAN_INTERVAL, default=DEFAULT_TIME_INTERVAL): cv.time_period,
})

COMPONENTS_SCHEMA = vol.All(cv.ensure_list, [
    vol.Any(FTP_SCHEMA, DIRECTORY_SCHEMA, MQTT_SCHEMA, IMAP_SCHEMA, API_SCHEMA, ELASTICSEARCH_SCHEMA, SCHEDULER_SCHEMA)
])

FILTER_SCHEMA = vol.Schema({
    vol.Optional(CONF_MIMETYPE): cv.string,
    vol.Optional(CONF_REGEX): cv.is_regex
})

REF_SCHEMA = vol.Schema({
    vol.Optional(CONF_FILTER): FILTER_SCHEMA
})

SENSOR_REF_CAMERA_SCHEMA = REF_SCHEMA.extend({
    vol.Required(CONF_CAMERA): cv.string
})

SENSOR_REF_SENSOR_SCHEMA = REF_SCHEMA.extend({
    vol.Required(CONF_SENSOR): cv.string
})

SENSORS_SCHEMA = vol.All(cv.ensure_list, [
    {
        vol.Required(CONF_ID): cv.string,
        vol.Required(CONF_PLATFORM): cv.string,
        vol.Required(CONF_TYPE): cv.string,
    }
])

# SCHEDULER_TRIGGER_SCHEMA = vol.Schema({
#     vol.Required(CONF_PLATFORM): CONF_SCHEDULER,
#     vol.Required(CONF_SCAN_INTERVAL, default=DEFAULT_TIME_INTERVAL): cv.time_period,
# })

# SENSOR_TRIGGER_SCHEMA = vol.Schema({
#     vol.Required(CONF_PLATFORM): CONF_SENSOR,
#     vol.Required(CONF_ENTITY_ID): cv.entity_id,
# })

# MQTT_TRIGGER_SCHEMA = vol.Schema({
#     vol.Required(CONF_PLATFORM): CONF_MQTT,
#     vol.Required(CONF_TOPIC): cv.string,
# })

# TRIGGERS_SCHEMA = vol.All(cv.ensure_list, [
#     vol.Any(SCHEDULER_TRIGGER_SCHEMA, SENSOR_TRIGGER_SCHEMA, MQTT_TRIGGER_SCHEMA)
# ])

COMPONENT_REF_SCHEMA_L4 = REF_SCHEMA.extend({
    vol.Required(CONF_COMPONENT): cv.string,
})

LISTENERS_SCHEMA_L4 = vol.All(cv.ensure_list, [
    vol.Any(SENSOR_REF_SENSOR_SCHEMA, COMPONENT_REF_SCHEMA_L4, SENSOR_REF_CAMERA_SCHEMA)
])

COMPONENT_REF_SCHEMA_L3 = REF_SCHEMA.extend({
    vol.Required(CONF_COMPONENT): cv.string,
    vol.Optional(CONF_LISTENERS): LISTENERS_SCHEMA_L4,
})

LISTENERS_SCHEMA_L3 = vol.All(cv.ensure_list, [
    vol.Any(SENSOR_REF_SENSOR_SCHEMA, COMPONENT_REF_SCHEMA_L4, SENSOR_REF_CAMERA_SCHEMA)
])

COMPONENT_REF_SCHEMA_L2 = REF_SCHEMA.extend({
    vol.Required(CONF_COMPONENT): cv.string,
    vol.Optional(CONF_LISTENERS): LISTENERS_SCHEMA_L3,
})

LISTENERS_SCHEMA_L2 = vol.All(cv.ensure_list, [
    vol.Any(SENSOR_REF_SENSOR_SCHEMA, COMPONENT_REF_SCHEMA_L2, SENSOR_REF_CAMERA_SCHEMA)
])

COMPONENT_REF_SCHEMA = REF_SCHEMA.extend({
    vol.Required(CONF_COMPONENT): cv.string,
    vol.Optional(CONF_LISTENERS): LISTENERS_SCHEMA_L2,
})

LISTENERS_SCHEMA = vol.All(cv.ensure_list, [
    vol.Any(SENSOR_REF_SENSOR_SCHEMA, COMPONENT_REF_SCHEMA, SENSOR_REF_CAMERA_SCHEMA)
])

PIPELINES_SCHEMA = vol.All(cv.ensure_list, [
    {
        vol.Required(CONF_ID): cv.string,
        vol.Required(CONF_COMPONENT): cv.string,
        vol.Required(CONF_LISTENERS): LISTENERS_SCHEMA,
    }
])

SENSORS_GLOBAL_SCHEMA = vol.All(cv.ensure_list, [{
    vol.Required(CONF_ID): cv.string,
    vol.Required(CONF_PLATFORM): cv.enum(SensorPlatforms),
    vol.Optional(CONF_TYPE): cv.string,
}])

CONFIG_SCHEMA = vol.Schema(
    {
        DOMAIN: vol.Schema(
            {
                vol.Required(CONF_COMPONENTS): COMPONENTS_SCHEMA,
                vol.Required(CONF_PIPELINES): PIPELINES_SCHEMA,
                vol.Required(CONF_SENSORS): SENSORS_GLOBAL_SCHEMA
            }, extra=vol.ALLOW_EXTRA)
    }, extra=vol.ALLOW_EXTRA)

PLATFORMS = ["sensor", "switch", "camera"]  # , "timer", "binary_sensor", "media_player"

# HISTORY EXAMPLE : homeassistant\components\history_stats\sensor.py 228


async def async_setup(hass: HomeAssistant, global_config: Config) -> bool:
    """Set up this integration using YAML."""

    config = global_config[DOMAIN]
    pipelines = config[CONF_PIPELINES]

    builder = Builder(hass, config)

    for pipeline in pipelines:
        builder.build()
        # builder = TransferBuilder(hass, config, entity_config)
        # builder.build()

        # name = entity_config[CONF_NAME]
        # storage = MemoryStorage(hass, name)
        # storage.coordinators = builder.build_coordinators_dict()
        # logger = getLogger(__name__, name)
        # logger.info(f"Init of manager finished with succes")

        # for component in PLATFORMS:
        #     hass.async_create_task(discovery.async_load_platform(
        #         hass, component, DOMAIN, entity_config, global_config))

    return True
