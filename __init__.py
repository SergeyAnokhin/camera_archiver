import logging

import voluptuous as vol
from homeassistant.components import discovery
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import (
    ATTR_NAME,
    CONF_HOST,
    CONF_ID,
    CONF_NAME,
    CONF_PASSWORD,
    CONF_PLATFORM,
    CONF_PORT,
    CONF_SCAN_INTERVAL,
    CONF_SENSORS,
    CONF_TYPE,
    CONF_URL,
    Platform,
)
from homeassistant.core import Config, HomeAssistant
from homeassistant.helpers import config_validation as cv

from .common.builder import Builder
from .common.helper import getLogger
from .common.types import SensorPlatforms
from .const import (
    ATTR_SENSORS,
    CONF_API,
    CONF_CAMERA,
    CONF_CLEAN,
    CONF_COMPONENT,
    CONF_COMPONENTS,
    CONF_COPIED_PER_RUN,
    CONF_DATA,
    CONF_DATETIME_PATTERN,
    CONF_DIRECTORY,
    CONF_ELASTICSEARCH,
    CONF_EMPTY_DIRECTORIES,
    CONF_FILES,
    CONF_FILTER,
    CONF_FTP,
    CONF_IMAP,
    CONF_INDEX,
    CONF_LISTENERS,
    CONF_METADATA,
    CONF_MIMETYPE,
    CONF_MQTT,
    CONF_PATH,
    CONF_PIPELINES,
    CONF_REGEX,
    CONF_SCHEDULER,
    CONF_SENSOR,
    CONF_SERVICE,
    CONF_SERVICE_CALLER,
    CONF_TOPIC,
    CONF_USER,
    DEFAULT_TIME_INTERVAL,
    DOMAIN,
)

_LOGGER = logging.getLogger(__name__)

COMPONENT_DEFAULT = vol.Schema(
    {
        vol.Optional(CONF_ID): cv.string,
    }
)

CLEAN_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_EMPTY_DIRECTORIES): cv.boolean,
        vol.Optional(CONF_FILES, default=[]): vol.All(cv.ensure_list, [cv.string]),
    }
)


FTP_SCHEMA = COMPONENT_DEFAULT.extend(
    {
        vol.Required(CONF_PLATFORM): CONF_FTP,
        vol.Required(CONF_HOST): cv.string,
        vol.Required(CONF_USER): cv.string,
        vol.Required(CONF_PASSWORD): cv.string,
        vol.Required(CONF_PATH): cv.string,
        vol.Required(CONF_DATETIME_PATTERN): cv.string,
        vol.Optional(CONF_COPIED_PER_RUN, default=100): cv.positive_int,
        vol.Optional(CONF_CLEAN): CLEAN_SCHEMA,
    }
)

DIRECTORY_SCHEMA = COMPONENT_DEFAULT.extend(
    {
        vol.Required(CONF_PLATFORM): CONF_DIRECTORY,
        vol.Required(CONF_PATH): cv.string,
        vol.Required(CONF_DATETIME_PATTERN): cv.string,
        vol.Optional(CONF_COPIED_PER_RUN, default=100): cv.positive_int,
        vol.Optional(CONF_CLEAN): CLEAN_SCHEMA,
    }
)

FILTER_SCHEMA = COMPONENT_DEFAULT.extend(
    {
        vol.Required(CONF_PLATFORM): CONF_FILTER,
        vol.Optional(CONF_MIMETYPE): cv.string,
    }
)

MQTT_SCHEMA = COMPONENT_DEFAULT.extend(
    {
        vol.Required(CONF_PLATFORM): CONF_MQTT,
        vol.Required(CONF_TOPIC): cv.string,
    }
)

METADATA_SCHEMA = COMPONENT_DEFAULT.extend(
    {
        vol.Required(CONF_PLATFORM): CONF_METADATA,
    }
)

ELASTICSEARCH_SCHEMA = COMPONENT_DEFAULT.extend(
    {
        vol.Required(CONF_PLATFORM): CONF_ELASTICSEARCH,
        vol.Required(CONF_INDEX): cv.string,
        vol.Required(CONF_HOST): cv.string,
        vol.Optional(CONF_PORT): cv.string,
    }
)

API_SCHEMA = COMPONENT_DEFAULT.extend(
    {
        vol.Required(CONF_PLATFORM): CONF_API,
        vol.Required(CONF_URL): cv.url,
    }
)

SERVICE_SCHEMA = COMPONENT_DEFAULT.extend(
    {
        vol.Required(CONF_PLATFORM): CONF_SERVICE,
    }
)

SERVICE_CALLER_SCHEMA = COMPONENT_DEFAULT.extend(
    {
        vol.Required(CONF_PLATFORM): CONF_SERVICE_CALLER,
    }
)

IMAP_SCHEMA = COMPONENT_DEFAULT.extend(
    {
        vol.Required(CONF_PLATFORM): CONF_IMAP,
        vol.Required(CONF_HOST): cv.string,
        vol.Required(CONF_USER): cv.string,
        vol.Required(CONF_PASSWORD): cv.string,
        vol.Required(CONF_PATH): cv.string,
    }
)

SCHEDULER_SCHEMA = COMPONENT_DEFAULT.extend(
    {
        vol.Required(CONF_PLATFORM): CONF_SCHEDULER,
        vol.Required(CONF_SCAN_INTERVAL, default=DEFAULT_TIME_INTERVAL): cv.time_period,
    }
)

COMPONENTS_SCHEMA = vol.All(
    cv.ensure_list,
    [
        vol.Any(
            FTP_SCHEMA,
            DIRECTORY_SCHEMA,
            MQTT_SCHEMA,
            IMAP_SCHEMA,
            API_SCHEMA,
            ELASTICSEARCH_SCHEMA,
            SCHEDULER_SCHEMA,
            SERVICE_SCHEMA,
            FILTER_SCHEMA,
            METADATA_SCHEMA,
            SERVICE_CALLER_SCHEMA,
        )
    ],
)

FILTER_SCHEMA = vol.Schema(
    {vol.Optional(CONF_MIMETYPE): cv.string, vol.Optional(CONF_REGEX): cv.is_regex}
)

REF_SCHEMA = vol.Schema({vol.Optional(CONF_FILTER): FILTER_SCHEMA})

SENSOR_REF_CAMERA_SCHEMA = REF_SCHEMA.extend({vol.Required(CONF_CAMERA): cv.string})

SENSOR_REF_SENSOR_SCHEMA = REF_SCHEMA.extend({vol.Required(CONF_SENSOR): cv.string})

SENSORS_SCHEMA = vol.All(
    cv.ensure_list,
    [
        {
            vol.Required(CONF_ID): cv.string,
            vol.Required(CONF_PLATFORM): cv.string,
            vol.Required(CONF_TYPE): cv.string,
        }
    ],
)

### LEVEL 5 ###
COMPONENT_REF_SCHEMA_L5 = REF_SCHEMA.extend(
    {
        vol.Required(CONF_COMPONENT): cv.string,
        vol.Optional(CONF_DATA): cv.ensure_list,
    }
)

LISTENERS_SCHEMA_L5 = vol.All(
    cv.ensure_list,
    [
        vol.Any(
            SENSOR_REF_SENSOR_SCHEMA, COMPONENT_REF_SCHEMA_L5, SENSOR_REF_CAMERA_SCHEMA
        )
    ],
)


### LEVEL 4 ###
COMPONENT_REF_SCHEMA_L4 = REF_SCHEMA.extend(
    {
        vol.Optional(CONF_LISTENERS): LISTENERS_SCHEMA_L5,
        vol.Optional(CONF_DATA): cv.ensure_list,
        vol.Required(CONF_COMPONENT): cv.string,
    }
)

LISTENERS_SCHEMA_L4 = vol.All(
    cv.ensure_list,
    [
        vol.Any(
            SENSOR_REF_SENSOR_SCHEMA, COMPONENT_REF_SCHEMA_L4, SENSOR_REF_CAMERA_SCHEMA
        )
    ],
)

### LEVEL 3 ###
COMPONENT_REF_SCHEMA_L3 = REF_SCHEMA.extend(
    {
        vol.Required(CONF_COMPONENT): cv.string,
        vol.Optional(CONF_DATA): cv.ensure_list,
        vol.Optional(CONF_LISTENERS): LISTENERS_SCHEMA_L4,
    }
)

LISTENERS_SCHEMA_L3 = vol.All(
    cv.ensure_list,
    [
        vol.Any(
            SENSOR_REF_SENSOR_SCHEMA, COMPONENT_REF_SCHEMA_L3, SENSOR_REF_CAMERA_SCHEMA
        )
    ],
)

### LEVEL 2 ###
COMPONENT_REF_SCHEMA_L2 = REF_SCHEMA.extend(
    {
        vol.Required(CONF_COMPONENT): cv.string,
        vol.Optional(CONF_DATA): cv.ensure_list,
        vol.Optional(CONF_LISTENERS): LISTENERS_SCHEMA_L3,
    }
)

LISTENERS_SCHEMA_L2 = vol.All(
    cv.ensure_list,
    [
        vol.Any(
            SENSOR_REF_SENSOR_SCHEMA, COMPONENT_REF_SCHEMA_L2, SENSOR_REF_CAMERA_SCHEMA
        )
    ],
)

### LEVEL 1 ###
COMPONENT_REF_SCHEMA = REF_SCHEMA.extend(
    {
        vol.Required(CONF_COMPONENT): cv.string,
        vol.Optional(CONF_DATA): cv.ensure_list,
        vol.Optional(CONF_LISTENERS): LISTENERS_SCHEMA_L2,
    }
)

LISTENERS_SCHEMA = vol.All(
    cv.ensure_list,
    [vol.Any(SENSOR_REF_SENSOR_SCHEMA, COMPONENT_REF_SCHEMA, SENSOR_REF_CAMERA_SCHEMA)],
)

PIPELINES_SCHEMA = vol.All(
    cv.ensure_list,
    [
        {
            vol.Required(CONF_ID): cv.string,
            vol.Required(CONF_COMPONENT): cv.string,
            vol.Required(CONF_LISTENERS): LISTENERS_SCHEMA,
        }
    ],
)

SENSORS_GLOBAL_SCHEMA = vol.All(
    cv.ensure_list,
    [
        {
            vol.Required(CONF_ID): cv.string,
            vol.Required(CONF_PLATFORM): cv.enum(SensorPlatforms),
            vol.Optional(CONF_TYPE): cv.string,
        }
    ],
)

CONFIG_SCHEMA = vol.Schema(
    {
        DOMAIN: vol.Schema(
            {
                vol.Required(CONF_COMPONENTS): COMPONENTS_SCHEMA,
                vol.Required(CONF_PIPELINES): PIPELINES_SCHEMA,
                vol.Required(CONF_SENSORS): SENSORS_GLOBAL_SCHEMA,
            },
            extra=vol.ALLOW_EXTRA,
        )
    },
    extra=vol.ALLOW_EXTRA,
)

PLATFORMS = [Platform.CAMERA, Platform.SENSOR, Platform.SWITCH, "timer"]

# PLATFORMS = ["sensor", "switch", "camera"]  # , "binary_sensor", "media_player"
PLATFORMS_NOMEDIA = ["camera", "sensor", "switch"]

# HISTORY EXAMPLE : homeassistant\components\history_stats\sensor.py 228


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up from a config entry."""
    hass.config_entries.async_setup_platforms(entry, PLATFORMS)
    # for component in PLATFORMS:
    #     hass.async_create_task(
    #         hass.config_entries.async_forward_entry_setup(entry, component)
    #     )
    return True


async def async_setup(hass: HomeAssistant, global_config: Config) -> bool:
    """Set up this integration using YAML."""

    config = global_config[DOMAIN]
    pipelines = config[CONF_PIPELINES]

    builder = Builder(hass, config)
    builder.build_components()
    builder.build_sensors()

    # hass.states.set("timer.mytimer", "0")

    for pipeline in pipelines:
        sensors = builder.build_pipeline(pipeline)
        name = pipeline[CONF_ID]
        # storage = MemoryStorage(hass, name)
        # storage.sensors = sensors
        logger = getLogger(__name__, name)
        logger.info(f"{name}:: Init of pipeline finished with succes")

        discovery_info = {ATTR_NAME: name, ATTR_SENSORS: sensors}

        for component in PLATFORMS:
            hass.async_create_task(
                discovery.async_load_platform(
                    hass, component, DOMAIN, discovery_info, global_config
                )
            )

        # hass.config_entries.async_forward_entry_setup(entry, component)
    # for component in PLATFORMS:
    #     hass.async_create_task(
    #         hass.config_entries.async_forward_entry_setup(global_config, component)
    #     )

    return True
