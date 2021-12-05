from datetime import timedelta
import logging
import voluptuous as vol
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
import homeassistant.helpers.config_validation as cv
from homeassistant.components.sensor import PLATFORM_SCHEMA, SensorEntity, STATE_CLASS_TOTAL_INCREASING
from homeassistant.const import CONF_HOST, CONF_NAME, CONF_PASSWORD, CONF_PATH
from homeassistant.helpers.update_coordinator import CoordinatorEntity, DataUpdateCoordinator

from .const import CONF_DATETIME_PARSER, CONF_DATETIME_PATTERN, CONF_FROM, CONF_FTP, CONF_LOCAL_STORAGE, CONF_TO, CONF_USER, DOMAIN, \
                    ICON_COPIED, ICON_DEFAULT, ICON_TO_COPY, SENSOR_NAME_FILES_COPIED, SENSOR_NAME_TO_COPY_FILES

FTP_SCHEMA = vol.Schema({
        vol.Required(CONF_HOST): cv.string,
        vol.Required(CONF_USER): cv.string,
        vol.Required(CONF_PASSWORD): cv.string,
        vol.Required(CONF_PATH): cv.string,
    })

FROM_SCHEMA = vol.Schema({
        vol.Required(CONF_FTP): FTP_SCHEMA,
        vol.Required(CONF_DATETIME_PARSER): cv.string
    })

TO_SCHEMA = vol.Schema({
        vol.Required(CONF_FTP): FTP_SCHEMA,
        vol.Required(CONF_DATETIME_PATTERN): cv.string
    })

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend({
        vol.Required(CONF_NAME): cv.string,
        vol.Required(CONF_LOCAL_STORAGE): cv.string,
        vol.Required(CONF_FROM): FROM_SCHEMA,
        vol.Required(CONF_TO): TO_SCHEMA
    })

_LOGGER = logging.getLogger(__name__)

def get_sensor_unique_id(config: ConfigEntry, sensor_name: str):
    return f'{config[CONF_NAME]} {sensor_name}'


async def async_setup_entry(hass, config_entry, async_add_entities):
    pass

def get_coordinator(hass: HomeAssistant, config: ConfigEntry):
    instanceName = config[CONF_NAME]

    if DOMAIN not in hass.data:
        hass.data[DOMAIN] = {}

    if instanceName in hass.data[DOMAIN]:
        return hass.data[DOMAIN][instanceName]

    sensor1 = get_sensor_unique_id(config, SENSOR_NAME_TO_COPY_FILES)
    sensor2 = get_sensor_unique_id(config, SENSOR_NAME_FILES_COPIED)

    data = {
        sensor1: 100,
        sensor2: 0
    }

    async def async_get_status():
        _LOGGER.info(f"Get Status Call")
        data = hass.data[DOMAIN][instanceName].data
        data[sensor1] = data[sensor1] - 1
        data[sensor2] = data[sensor2] + 1
        return data

    interval = 5 if instanceName == "Yi1080pWoodSouth" else 10

    coordinator = DataUpdateCoordinator(
        hass,
        logging.getLogger(__name__),
        name=DOMAIN,
        update_method=async_get_status,
        update_interval=timedelta(seconds=interval),
    )
    coordinator.data = data

    hass.data[DOMAIN][instanceName] = coordinator

    return coordinator

async def async_setup_platform(hass: HomeAssistant, config: ConfigEntry, add_entities, discovery_info=None):
    coordinator = get_coordinator(hass, config)

    add_entities([
        ToCopyFilesSensor(coordinator, config),
        CopiedFilesSensor(coordinator, config)
    ])


class TransferSensor(CoordinatorEntity, SensorEntity):

    def __init__(self, coordinator, config, name, icon, unit=""):
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._config = config
        self._name = name
        self._unit = unit
        self._icon = icon
        self._timestamp = None
        self._state = None

    @property
    def name(self):
        """Return the name of the sensor."""
        return self._name

    @property
    def available(self) -> bool:
        """Return True if entity is available."""
        return self._name in self.coordinator.data

    @property
    def state(self):
        """Return the state of the sensor."""
        self._state = self.coordinator.data[self._name]
        return self._state

    @property
    def unit_of_measurement(self):
        """Return the unit of measurement."""
        return self._unit

    @property
    def icon(self):
        """Return the icon of the sensor."""
        return self._icon

    # def set_data(self, timestamp, state):
    #     """Update sensor data"""
    #     self._state = state
    #     self._timestamp = timestamp

class ToCopyFilesSensor(TransferSensor):
    def __init__(self, coordinator, config):
        instanceName = config[CONF_NAME]
        name = get_sensor_unique_id(config, SENSOR_NAME_TO_COPY_FILES)
        icon = ICON_TO_COPY
        super().__init__(coordinator, config, name, icon)    

class CopiedFilesSensor(TransferSensor):
    def __init__(self, coordinator, config):
        instanceName = config[CONF_NAME]
        name = get_sensor_unique_id(config, SENSOR_NAME_FILES_COPIED)
        icon = ICON_COPIED
        super().__init__(coordinator, config, name, icon)    
        self._attr_state_class = STATE_CLASS_TOTAL_INCREASING
