from datetime import timedelta
import logging
import voluptuous as vol
from .FtpTransfer import FtpTransfer
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
import homeassistant.helpers.config_validation as cv
from homeassistant.components.sensor import PLATFORM_SCHEMA, SensorEntity, STATE_CLASS_TOTAL_INCREASING
from homeassistant.const import CONF_HOST, CONF_NAME, CONF_PASSWORD, CONF_PATH
from homeassistant.helpers.update_coordinator import CoordinatorEntity, DataUpdateCoordinator
from homeassistant.helpers.restore_state import RestoreEntity

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

def get_sensor_unique_id(config, sensor_name: str):
    return f'{config[CONF_NAME]} {sensor_name}'


async def async_setup_entry(hass, config_entry, async_add_entities):
    pass

def get_coordinator(hass: HomeAssistant, config: ConfigEntry):
    instanceName = config[CONF_NAME]
    _LOGGER.debug(f"#{instanceName}# Call sensor.py:get_coordinator() {instanceName}")

    if DOMAIN not in hass.data:
        hass.data[DOMAIN] = {}

    if instanceName in hass.data[DOMAIN]:
        return hass.data[DOMAIN][instanceName]

    sensor1 = get_sensor_unique_id(config, SENSOR_NAME_TO_COPY_FILES)
    sensor2 = get_sensor_unique_id(config, SENSOR_NAME_FILES_COPIED)

    data = {
        sensor1: 101,
        sensor2: 1
    }

    async def async_get_status():
        _LOGGER.info(f"#{instanceName}# Call Callback sensor.py:get_coordinator.async_get_status() ")
        data = hass.data[DOMAIN][instanceName].data
        data[sensor1] = data[sensor1] - 1
        data[sensor2] = data[sensor2] + 1
        # transfer = FtpTransfer(config)
        # files = transfer.State()
        # data[sensor1] = files
        return data

    interval = 5 if instanceName == "Yi1080pWoodSouth" else 10

    coordinator = DataUpdateCoordinator(
        hass,
        logging.getLogger(__name__),
        name=DOMAIN,
        update_method=async_get_status,
        update_interval=timedelta(seconds=interval),
    )
    coordinator.last_update_success = False
    coordinator.data = data

    hass.data[DOMAIN][instanceName] = coordinator

    return coordinator

async def async_setup_platform(hass: HomeAssistant, config: ConfigEntry, add_entities, discovery_info=None):
    _LOGGER.debug("Call sensor.py:async_setup_platform()")
    coordinator = get_coordinator(hass, config)

    add_entities([
        ToCopyFilesSensor(coordinator, config),
        CopiedFilesSensor(coordinator, config)
    ])

class TransferSensor(CoordinatorEntity, RestoreEntity, SensorEntity):

    def __init__(self, coordinator, config, name, icon, unit=""):
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._config = config
        self._name = name
        self._unit = unit
        self._icon = icon
        # self._timestamp = None
        self._state = None
        self._available = False

    @property
    def name(self):
        """Return the name of the sensor."""
        return self._name

    # @property
    # def native_value(self):
    #     """Return native value for entity."""
    #     if self.coordinator.data:
    #         state = self.coordinator.data[self._name]
    #         self._state = state
    #     return self._state

    # async def async_added_to_hass(self) -> None:
    #     """Handle entity which will be added."""
    #     await super().async_added_to_hass()
    #     if state := await self.async_get_last_state():
    #         self._state = state.state

    # @property
    # def available(self) -> bool:
    #     """Return True if entity is available."""
    #     return self._name in self.coordinator.data

    # @property
    # def state(self):
    #     """Return the state of the sensor."""
    #     self._state = self.coordinator.data[self._name]
    #     return self._state

    @property
    def available(self):
        """Return True if entity is available."""
        return self._available

    @property
    def native_value(self):
        """Get the latest reading."""
        return self._state

    @callback
    def _state_update(self):
        """Call when the coordinator has an update."""
        self._available = self.coordinator.last_update_success
        if self._available:
            self._state = self.coordinator.data[self._name]
        _LOGGER.info(f"#{self._name}# Call Callback TransferSensor._state_update() STATE={self._state}")
        self.async_write_ha_state()

    async def async_added_to_hass(self):
        """Subscribe to updates."""
        _LOGGER.info(f"#{self._name}# Call TransferSensor.async_added_to_hass() STATE={self._state}")
        self.async_on_remove(self.coordinator.async_add_listener(self._state_update))

        # If the background update finished before
        # we added the entity, there is no need to restore
        # state.
        _LOGGER.info(f"#{self._name}# coordinator.last_update_success={self.coordinator.last_update_success} STATE={self._state}")
        # if self.coordinator.last_update_success:
        #     return

        last_state = await self.async_get_last_state()
        _LOGGER.info(f"#{self._name}# call async_get_last_state STATE={self._state}")
        if last_state:
            self._state = last_state.state
            self._available = True
            _LOGGER.info(f"#{self._name}# NEW_STATE={self._state}")


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
        name = get_sensor_unique_id(config, SENSOR_NAME_TO_COPY_FILES)
        icon = ICON_TO_COPY
        super().__init__(coordinator, config, name, icon)    

class CopiedFilesSensor(TransferSensor):
    def __init__(self, coordinator, config):
        name = get_sensor_unique_id(config, SENSOR_NAME_FILES_COPIED)
        icon = ICON_COPIED
        super().__init__(coordinator, config, name, icon)    
        self._attr_state_class = STATE_CLASS_TOTAL_INCREASING
