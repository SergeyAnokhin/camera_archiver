import logging
import voluptuous as vol
import homeassistant.helpers.config_validation as cv
from homeassistant.components.sensor import PLATFORM_SCHEMA, SensorEntity, STATE_CLASS_TOTAL_INCREASING
from homeassistant.const import CONF_HOST, CONF_NAME, CONF_PASSWORD, CONF_PATH

from .const import CONF_DATETIME_PARSER, CONF_DATETIME_PATTERN, CONF_FROM, CONF_LOCAL_STORAGE, CONF_TO, CONF_USER, \
                    HA_MEGABYTES_COPIED, HA_FILES_COPIED, ICON_DEFAULT, ICONS_MAPPING

FTP_SCHEMA = vol.Schema({
        vol.Required(CONF_HOST): cv.string,
        vol.Required(CONF_USER): cv.string,
        vol.Required(CONF_PASSWORD): cv.string,
        vol.Required(CONF_PATH): cv.string,
    })

FROM_SCHEMA = vol.Schema({
        vol.Required(CONF_FROM): FTP_SCHEMA,
        vol.Required(CONF_DATETIME_PARSER): cv.string
    })

TO_SCHEMA = vol.Schema({
        vol.Required(CONF_FROM): FTP_SCHEMA,
        vol.Required(CONF_DATETIME_PATTERN): cv.string
    })

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend({
        vol.Required(CONF_NAME): cv.string,
        vol.Required(CONF_LOCAL_STORAGE): cv.string,
        vol.Required(CONF_FROM): FROM_SCHEMA,
        vol.Required(CONF_TO): TO_SCHEMA
    })

_LOGGER = logging.getLogger(__name__)

class TransferSensor(SensorEntity):

    def __init__(self, name, icon, unit=""):
        """Initialize the sensor."""
        self._name = name
        self._unit = unit
        self._icon = icon
        self._timestamp = None
        self._state = None

        if self._name in [HA_FILES_COPIED, HA_MEGABYTES_COPIED]:
            self._attr_state_class = STATE_CLASS_TOTAL_INCREASING

    @property
    def name(self):
        """Return the name of the sensor."""
        return self._name

    @property
    def state(self):
        """Return the state of the sensor."""
        return self._state

    @property
    def unit_of_measurement(self):
        """Return the unit of measurement."""
        return self._unit

    @property
    def icon(self):
        """Return the icon of the sensor."""
        return self._icon

    def set_data(self, timestamp, state):
        """Update sensor data"""
        self._state = state
        self._timestamp = timestamp
