import logging
from datetime import datetime

from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_NAME
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .common.helper import to_human_readable, to_short_human_readable, to_short_human_readable_delta
from .common.memory_storage import MemoryStorage
from .common.transfer_component_id import TransferComponentId, TransferType
from .common.transfer_state import EventType, TransferState
from .const import (ATTR_ENABLE, ATTR_EXTENSIONS, ATTR_LAST_DATETIME,
                    ATTR_LAST_DATETIME_FULL, ATTR_LAST_IMAGE, ATTR_LAST_VIDEO,
                    ATTR_SIZE_MB, ATTR_TRANSFER_STATE, ICON_COPIED,
                    ICON_DEFAULT, ICON_LAST, ICON_SCREENSHOT, ICON_TIMER,
                    ICON_TO_COPY, ICON_VIDEO)

_LOGGER = logging.getLogger(__name__)

async def async_setup_platform(hass: HomeAssistant, config: ConfigEntry, add_entities, discovery_info=None):
    entity_config = discovery_info
    instName = entity_config[CONF_NAME]
    storage = MemoryStorage(hass, instName)

    sensors = []
    for comp_id, coords_by_state in storage.coordinators.items():
        id: TransferComponentId = comp_id
        if id.TransferType == TransferType.FROM:
            coordinator = coords_by_state[EventType.REPOSITORY]
            sensors.append(FromComponentRepoSensor(id, coordinator))
            coordinator = coords_by_state[EventType.READ]
            sensors.append(FromComponentReadSensor(id, coordinator))
            coordinator = coords_by_state[EventType.SET_SCHEDULER]
            sensors.append(TimerCoordinatorSensor(id, coordinator))
        elif id.TransferType == TransferType.TO:
            coordinator = coords_by_state[EventType.SAVE]
            sensors.append(ToComponentSaveSensor(id, coordinator))
            coordinator = coords_by_state[EventType.SAVE]
            sensors.append(ComponentLastTimeSensor(id, coordinator))
            coordinator = coords_by_state[EventType.SAVE]
            sensors.append(ComponentLastImageSensor(id, coordinator))
            coordinator = coords_by_state[EventType.SAVE]
            sensors.append(ComponentLastVideoSensor(id, coordinator))

    add_entities(sensors)


class CoordinatorSensor(CoordinatorEntity, SensorEntity):
    def __init__(self, comp_id: TransferComponentId, eventType: EventType, coordinator, icon=ICON_DEFAULT, unit=""):
        CoordinatorEntity.__init__(self, coordinator)
        self._attr_unit_of_measurement = unit
        self._attr_icon = icon
        self._attr_native_value = None
        self._attr_extra_state_attributes = {}
        self._eventType: EventType = eventType
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
            and self.data[ATTR_TRANSFER_STATE] is not None

    def set_attr(self, key: str, value) -> None:
        if value:
            self._attr_extra_state_attributes[key] = value
        elif key in self._attr_extra_state_attributes:
            del(self._attr_extra_state_attributes[key])

class TimerCoordinatorSensor(CoordinatorSensor):
    def __init__(self, comp_id: TransferComponentId, coordinator):
        CoordinatorSensor.__init__(self, comp_id, EventType.SET_SCHEDULER, coordinator, icon=ICON_TIMER)
        self._attr_name = f"{comp_id.Entity}: {comp_id.Name} timer"
        self._attr_should_poll = True

    @property
    def should_poll(self) -> bool:
        """No need to poll. Coordinator notifies entity of updates."""
        return True

    @property
    def has_transfer_state(self) -> bool:
        return super().has_transfer_state \
            and isinstance(self.data[ATTR_TRANSFER_STATE], datetime)

    @callback
    def _handle_coordinator_update(self):
        """Call when the coordinator has an update."""
        if self.enabled and not self.has_transfer_state:
            self.coordinator.data[ATTR_TRANSFER_STATE] = None

        state: datetime = self.coordinator.data[ATTR_TRANSFER_STATE]
        self.set_attr(ATTR_ENABLE, self.available)
        if state:
            self.coordinator_updated(state)
        super()._handle_coordinator_update()

    def coordinator_updated(self, state: datetime):
        delta = state - datetime.now()
        self._attr_native_value = to_short_human_readable_delta(delta)

class TransferCoordinatorSensor(CoordinatorSensor):

    def __init__(self, comp_id: TransferComponentId, eventType: EventType, coordinator, icon=ICON_DEFAULT, unit=""):
        CoordinatorSensor.__init__(self, comp_id, eventType, coordinator, icon=icon)
        self._attr_name = f"{comp_id.Entity}: {comp_id.Name} {eventType.value} files"

    @property
    def has_transfer_state(self) -> bool:
        return super().has_transfer_state \
            and isinstance(self.data[ATTR_TRANSFER_STATE], TransferState)

    @callback
    def _handle_coordinator_update(self):
        """Call when the coordinator has an update."""
        if self.enabled and not self.has_transfer_state:
            self.coordinator.data[ATTR_TRANSFER_STATE] = TransferState(self._eventType)

        state: TransferState = self.coordinator.data[ATTR_TRANSFER_STATE]
        self.set_attr(ATTR_ENABLE, self.available)
        if state:
            self.coordinator_updated(state)
        super()._handle_coordinator_update()

    def coordinator_updated(self, state: TransferState):
        self._attr_native_value = state.files_count
        self.set_attr(ATTR_SIZE_MB, state.files_size_mb)
        self.set_attr(ATTR_EXTENSIONS, state.files_ext)
        self.set_attr(ATTR_LAST_IMAGE, state.last_image)
        self.set_attr(ATTR_LAST_VIDEO, state.last_video)
        last_time = to_short_human_readable(state.last_datetime)
        self.set_attr(ATTR_LAST_DATETIME, last_time)
        last_time = to_human_readable(state.last_datetime)
        self.set_attr(ATTR_LAST_DATETIME_FULL, last_time)

class ComponentLastTimeSensor(TransferCoordinatorSensor):
    def __init__(self, comp_id: TransferComponentId, coordinator):
        super().__init__(comp_id, EventType.SAVE, coordinator, icon=ICON_LAST)
        self._attr_name = f"{comp_id.Entity}: last time"

    def coordinator_updated(self, state: TransferState):
        self._attr_native_value = to_human_readable(state.last_datetime)


class ComponentLastImageSensor(TransferCoordinatorSensor):
    def __init__(self, comp_id: TransferComponentId, coordinator):
        super().__init__(comp_id, EventType.SAVE, coordinator, icon=ICON_SCREENSHOT)
        self._attr_name = f"{comp_id.Entity}: last image"

    def coordinator_updated(self, state: TransferState):
        self._attr_native_value = state.last_image


class ComponentLastVideoSensor(TransferCoordinatorSensor):
    def __init__(self, comp_id: TransferComponentId, coordinator):
        super().__init__(comp_id, EventType.SAVE, coordinator, icon=ICON_VIDEO)
        self._attr_name = f"{comp_id.Entity}: last video"

    def coordinator_updated(self, state: TransferState):
        self._attr_native_value = state.last_video


class FromComponentRepoSensor(TransferCoordinatorSensor):
    def __init__(self, comp_id: TransferComponentId, coordinator):
        super().__init__(comp_id,
                         EventType.REPOSITORY,
                         coordinator,
                         icon=ICON_TO_COPY)


class FromComponentReadSensor(TransferCoordinatorSensor):
    def __init__(self, comp_id: TransferComponentId, coordinator):
        super().__init__(comp_id,
                         EventType.READ,
                         coordinator,
                         icon=ICON_COPIED)


class ToComponentSaveSensor(TransferCoordinatorSensor):
    def __init__(self, comp_id: TransferComponentId, coordinator):
        super().__init__(comp_id,
                         EventType.SAVE,
                         coordinator,
                         icon=ICON_COPIED)
