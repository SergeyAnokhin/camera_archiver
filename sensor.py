import logging
from abc import abstractmethod
from typing import Dict

from homeassistant.components.sensor import STATE_CLASS_TOTAL_INCREASING, SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_NAME
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.update_coordinator import (CoordinatorEntity,
                                                      DataUpdateCoordinator)

from .common.state_collector import StateCollector
from .common.transfer_component_id import TransferComponentId, TransferType
from .common.transfer_state import StateType, TransferState
from .const import (ATTR_ARCHIVER_STATE, ATTR_DURATION, ATTR_ENABLE, ATTR_EXTENSIONS,
                    ATTR_LAST, ATTR_LAST_FILE, ATTR_SIZE, ATTR_SIZE_MB, ATTR_TRANSFER_STATE, CONF_FROM, DOMAIN, ICON_COPIED,
                    ICON_DEFAULT, ICON_TO_COPY, SENSOR_NAME_FILES_COPIED,
                    SENSOR_NAME_FILES_COPIED_LAST, SENSOR_NAME_TO_COPY_FILES)

_LOGGER = logging.getLogger(__name__)

# from homeassistant.helpers.entity import generate_entity_id

async def async_setup_entry(hass, config_entry, async_add_entities):
    pass

async def async_setup_platform(hass: HomeAssistant, config: ConfigEntry, add_entities, discovery_info=None):
    entity_config = discovery_info
    instName = entity_config[CONF_NAME]
    coordinators: Dict[TransferComponentId:  Dict[StateType: DataUpdateCoordinator]] = hass.data[DOMAIN][instName]

    sensors = []
    for comp_id, coords_by_state in coordinators.items():
        id: TransferComponentId = comp_id
        if id.TransferType == TransferType.FROM:
            coordinator = coords_by_state[StateType.REPOSITORY]
            sensors.append(FromComponentRepoSensor(id, coordinator))
            coordinator = coords_by_state[StateType.READ]
            sensors.append(FromComponentReadSensor(id, coordinator))
        elif id.TransferType == TransferType.TO:
            coordinator = coords_by_state[StateType.SAVE]
            sensors.append(ToComponentSaveSensor(id, coordinator))

    add_entities(sensors)

class TransferCoordinatorSensor(CoordinatorEntity, SensorEntity):

    def __init__(self, comp_id: TransferComponentId, stateType: StateType, coordinator, icon=ICON_DEFAULT, unit=""):
        """Initialize the sensor."""
        CoordinatorEntity.__init__(self, coordinator)
        self._attr_name = f"{comp_id.Entity}: {comp_id.Name} {stateType.value} files"
        self._attr_unit_of_measurement = unit
        self._attr_icon = icon
        self._attr_native_value = None
        # self._attr_available = False
        self._attr_extra_state_attributes = {}
        self._stateType: StateType = stateType
        self.data = self.coordinator.data

    @property
    def available(self) -> bool:
        """Return True if entity is available."""
        return self.coordinator.data[ATTR_ENABLE]

    @property
    def enabled(self) -> bool:
        return self.coordinator.data[ATTR_ENABLE]
    @property
    def has_transfer_state(self) -> bool:
        return ATTR_TRANSFER_STATE in self.data \
            and self.data[ATTR_TRANSFER_STATE] \
            and isinstance(self.data[ATTR_TRANSFER_STATE], TransferState)

    @callback
    def _handle_coordinator_update(self):
        """Call when the coordinator has an update."""
        if self.enabled and not self.has_transfer_state:
            self.coordinator.data[ATTR_TRANSFER_STATE] = TransferState(self._stateType)

        state: TransferState = self.coordinator.data[ATTR_TRANSFER_STATE]
        self.coordinator_updated(state)
        super()._handle_coordinator_update()


    #@abstractmethod
    def coordinator_updated(self, state: TransferState):
        self.set_attr(ATTR_ENABLE, self.available)
        if not state:
            return
        self._attr_native_value = state.files_count
        self.set_attr(ATTR_SIZE_MB, state.files_size_mb)
        self.set_attr(ATTR_EXTENSIONS, state.files_ext)
        self.set_attr(ATTR_LAST_FILE, state.last)

    def set_attr(self, key: str, value) -> None:
        self._attr_extra_state_attributes[key] = value

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
    def __init__(self, comp_id: TransferComponentId, coordinator):
        super().__init__(comp_id, 
            StateType.REPOSITORY, 
            coordinator, 
            ICON_TO_COPY)


class FromComponentReadSensor(TransferCoordinatorSensor):
    def __init__(self, comp_id: TransferComponentId, coordinator):
        super().__init__(comp_id, 
            StateType.READ, 
            coordinator, 
            ICON_COPIED)

class ToComponentSaveSensor(TransferCoordinatorSensor):
    def __init__(self, comp_id: TransferComponentId, coordinator):
        super().__init__(comp_id, 
            StateType.SAVE, 
            coordinator, 
            ICON_COPIED)





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


