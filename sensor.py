import logging
from abc import abstractmethod

from homeassistant.components.sensor import STATE_CLASS_TOTAL_INCREASING
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_NAME
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .common.state_collector import StateCollector
from .common.transfer_component import TransferType
from .common.transfer_manager import TransferManager
from .common.transfer_state import StateType, TransferState
from .const import (ATTR_ARCHIVER_STATE, ATTR_COLLECTOR_LAST_TYPE_UPDATED,
                    ATTR_DURATION, ATTR_EXTENSIONS, ATTR_LAST, ATTR_SIZE,
                    ATTR_TRANSFER_RESULT, CONF_FROM, CONF_TO, DOMAIN,
                    ICON_COPIED, ICON_DEFAULT, ICON_TO_COPY,
                    SENSOR_NAME_FILES_COPIED, SENSOR_NAME_FILES_COPIED_LAST,
                    SENSOR_NAME_TO_COPY_FILES)

_LOGGER = logging.getLogger(__name__)

# from homeassistant.helpers.entity import generate_entity_id

async def async_setup_entry(hass, config_entry, async_add_entities):
    pass

async def async_setup_platform(hass: HomeAssistant, config: ConfigEntry, add_entities, discovery_info=None):
    config = discovery_info
    instName = config[CONF_NAME]
    manager: TransferManager = hass.data[DOMAIN][instName]
    coordinator = manager.coordinator

    sensors = []
    for comp_config in config[CONF_FROM]:
        sensors.append(FromComponentRepoSensor(instName, comp_config, coordinator))
        # sensors.append(FromComponentReadSensor(coordinator, comp_config))

    # for comp_config in config[CONF_TO]:
    #     sensors.append(ToComponentSaveSensor(coordinator, comp_config))

    add_entities(sensors)
    # add_entities([
    #     ToCopyFilesSensor(coordinator, config),
    #     CopiedFilesSensor(coordinator, config),
    #     LastFilesCopiedSensor(coordinator, config),
    # ])

class TransferCoordinatorSensor(CoordinatorEntity):

    def __init__(self, instName: str, stateType: StateType, transferType: TransferType, config: dict, coordinator, icon=ICON_DEFAULT, unit=""):
        """Initialize the sensor."""
        CoordinatorEntity.__init__(self, coordinator)
        self._config = config
        self._transferType = transferType
        self._attr_name = f"{instName} {stateType} files"
        self._attr_unit_of_measurement = unit
        self._attr_icon = icon
        self._attr_native_value = None
        self._attr_available = False
        self._attr_extra_state_attributes = {}
        self._stateType: StateType = stateType

    @callback
    def _handle_coordinator_update(self):
        """Call when the coordinator has an update."""
        if not self.available:
            return
        collector: StateCollector = self.coordinator.data[ATTR_ARCHIVER_STATE]
        last_type_updated: StateType = self.coordinator.data[ATTR_COLLECTOR_LAST_TYPE_UPDATED]
        self.coordinator_updated(collector, last_type_updated)
        super()._handle_coordinator_update()

    @abstractmethod
    def coordinator_updated(self, collector: StateCollector, last_type_updated: StateType):
        NotImplementedError()

    # def add_attr(self, key: str, value) -> None:
    #     self._attr_extra_state_attributes[key] = value

    # def add_attrs(self, keyvalues: dict) -> None:
    #     self._attr_extra_state_attributes = {
    #         **self._attr_extra_state_attributes,
    #         **keyvalues
    #     }

    # def attr_add_float(self, key: str, new_value: float):
    #     old_value = self._attr_extra_state_attributes.get(key, 0.0)
    #     result = round(old_value + new_value, 2)
    #     self.add_attr(key, result)

    # def attr_add_set(self, key: str, new_value: list):
    #     old_value: dict = self._attr_extra_state_attributes.get(key, set())
    #     self.add_attr(key, set(list(old_value) + new_value))

class FromComponentRepoSensor(TransferCoordinatorSensor):
    def __init__(self, instName: str, config, coordinator):
        super().__init__(instName, 
            StateType.REPOSITORY, 
            TransferType.FROM, 
            config, 
            coordinator, 
            ICON_TO_COPY)

    def coordinator_updated(self, collector: StateCollector, last_type_updated: StateType):
        pass


class FromComponentReadSensor(TransferCoordinatorSensor):
    pass

class ToComponentSaveSensor(TransferCoordinatorSensor):
    pass


class ToCopyFilesSensor(TransferCoordinatorSensor):
    def __init__(self, coordinator, config):
        name = SENSOR_NAME_TO_COPY_FILES
        icon = ICON_TO_COPY
        super().__init__(coordinator, config, name, icon)

    def coordinator_updated(self, state: TransferState):
        self.add_attrs({
            ATTR_EXTENSIONS: state.Read.files_ext,
            ATTR_DURATION: state.Read.duration.seconds,
            ATTR_SIZE: f"{state.Read.files_size_mb}Mb",
            ATTR_LAST: state.Read.last
        })
        self._attr_native_value = state.Read.files_count

        # If the background update finished before
        # we added the entity, there is no need to restore
        # state.
        # _LOGGER.info(f"#{self._name}# coordinator.last_update_success={self.coordinator.last_update_success} STATE={self._state}")
        # if self.coordinator.last_update_success:
        #     return

        # last_state = await self.async_get_last_state()
        # _LOGGER.info(f"#{self._name}# call async_get_last_state STATE={self._state}")
        # if last_state:
        #     self._state = last_state.state
        #     self._available = True
        #     _LOGGER.info(f"#{self._name}# NEW_STATE={self._state}")


class LastFilesCopiedSensor(TransferCoordinatorSensor):
    def __init__(self, coordinator, config):
        name = SENSOR_NAME_FILES_COPIED_LAST
        super().__init__(coordinator, config, name)

    def coordinator_updated(self, state: TransferState):
        self.add_attrs({
            ATTR_EXTENSIONS: state.Copy.files_ext,
            ATTR_DURATION: state.Copy.duration.seconds,
            ATTR_SIZE: f"{state.Copy.files_size_mb}Mb",
            ATTR_LAST: state.Copy.last
        })
        self._attr_native_value = state.Copy.files_count


class CopiedFilesSensor(TransferCoordinatorSensor):
    def __init__(self, coordinator, config):
        # name = get_sensor_unique_id(config, SENSOR_NAME_FILES_COPIED)
        name = SENSOR_NAME_FILES_COPIED
        icon = ICON_COPIED
        self._attr_native_value = 0
        super().__init__(coordinator, config, name, icon)
        self._attr_state_class = STATE_CLASS_TOTAL_INCREASING


    def coordinator_updated(self, state: TransferState):
        self.attr_add_set(ATTR_EXTENSIONS, state.Copy.files_exts)
        self.attr_add_float(ATTR_DURATION, state.Copy.duration.seconds)
        self.attr_add_float(ATTR_SIZE, state.Copy.files_size_mb)
        if not self._attr_native_value:
            self._attr_native_value = 0
        self._attr_native_value = int(self._attr_native_value) + state.Copy.files_count

# class TransferRestoreSensor(CoordinatorEntity, TransferSensor):
#     def __init__(self, coordinator, config, name, icon, unit=""):
#         CoordinatorEntity.__init__(self, coordinator)
#         TransferSensor.__init__(self, config, name, icon, unit)

#     @property
#     def available(self):
#         return self._state and self._state.isdigit()

#     @property
#     def native_value(self):
#         return self._state

#     @callback
#     def _state_update(self):
#         _LOGGER.debug(f"#{self._name}# Call Callback TransferRestoreSensor._state_update() STATE={self._state}")
#         coor = self.coordinator
#         if not self.available:
#             self._state = '0'
#         self._state = str(int(self._state) + 1)
#         id = self.entity_id
#         self.async_write_ha_state()
#         # #CHECK
#         # last_state = await self.async_get_last_state()
#         # state = last_state.state

#     async def async_update(self):
#         pass

#     async def async_added_to_hass(self):
#         _LOGGER.info(f"#{self._name}# Call TransferRestoreSensor.async_added_to_hass()")
#         """Subscribe to updates."""
#         #self.async_on_remove(self._state_update)
#         # TIME CHANGE
#         # self.async_on_remove(
#         #     async_track_time_change(
#         #         self.hass, self.async_update_prices, second=30
#         #     )
#         # )
#         # # SIGNAL
#         # self.async_on_remove(
#         #     async_dispatcher_connect(
#         #         self.hass, f"{DOMAIN}_data_updated", self._schedule_immediate_update
#         #     )
#         # )
#         # async_track_state_change_event(
#         #     self.hass, [self._sensor_source_id], calc_integration
#         # )

#         self.async_on_remove(
#             self.coordinator.async_add_listener(
#                 self._state_update
#             )
#         )

#         # if self.hass.state == CoreState.running:
#         #     start_refresh()
#         #     return

    # async def async_added_to_hass(self):
    #     """Create listeners when the entity is added."""

    #     @callback
    #     def start_refresh(*args):
    #         """Register state tracking."""

    #         @callback
    #         def force_refresh(*args):
    #             """Force the component to refresh."""
    #             self.async_schedule_update_ha_state(True)

    #         force_refresh()
    #         self.async_on_remove(
    #             async_track_state_change_event(
    #                 self.hass, [self._entity_id], force_refresh
    #             )
    #         )

    #     if self.hass.state == CoreState.running:
    #         start_refresh()
    #         return

    #     # Delay first refresh to keep startup fast
    #     self.hass.bus.async_listen_once(EVENT_HOMEASSISTANT_START, start_refresh)


#         last_state = await self.async_get_last_state()
#         _LOGGER.info(f"#{self._name}# call async_get_last_state STATE={self._state}")
#         if last_state and last_state.state and last_state.state.isdigit():
#             self._state = last_state.state
#             _LOGGER.info(f"#{self._name}# NEW_STATE={self._state}")


