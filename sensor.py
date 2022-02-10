import logging
from datetime import datetime
from typing import cast
from .common.event_objects import EventObject, FileEventObject, RepositoryEventObject, SetSchedulerEventObject, StartEventObject
from .common.types import SensorConnector

from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import ATTR_NAME, CONF_NAME
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .common.helper import (getLogger, to_human_readable, to_short_human_readable,
                            to_short_human_readable_delta)
from .common.transfer_state import EventType, TransferState
from .const import (ATTR_ENABLE, ATTR_EXTENSIONS, ATTR_LAST_DATETIME,
                    ATTR_LAST_DATETIME_FULL, ATTR_LAST_IMAGE, ATTR_LAST_VIDEO, ATTR_PIPELINE_PATH,
                    ATTR_SENSORS, ATTR_SIZE_MB, ATTR_TRANSFER_STATE, CONF_SENSOR_TYPE_LAST_FILE, CONF_SENSOR_TYPE_LAST_TIME, CONF_SENSOR_TYPE_REPOSITORY_STAT, CONF_SENSOR_TYPE_TIMER, CONF_SENSOR_TYPE_TRANSFER_STAT,
                    ICON_COPIED, ICON_DEFAULT, ICON_LAST, ICON_SCREENSHOT,
                    ICON_TIMER, ICON_TO_COPY, ICON_VIDEO)

_LOGGER = logging.getLogger(__name__)

_PLATFORM = "sensor"

class ConnectorSensor(SensorEntity):
    def __init__(self, connector: SensorConnector, icon=ICON_DEFAULT, unit=""):
        self._attr_unit_of_measurement = unit
        self._attr_icon = icon
        self._attr_native_value = None
        self._attr_extra_state_attributes = {}
        self.connector = connector
        self.connector.add_listener(self.callback)
        self._name_prefix = f"{connector.pipeline_id}: {connector.parent}"
        self.set_attr(ATTR_PIPELINE_PATH, connector.pipeline_path)

    def callback(self, eventObj: EventObject):
        if isinstance(eventObj, FileEventObject):
            event = cast(FileEventObject, eventObj)
            self.onFileEvent(event)
        elif isinstance(eventObj, RepositoryEventObject):
            event = cast(RepositoryEventObject, eventObj)
            self.onRepositoryEvent(event)
        elif isinstance(eventObj, StartEventObject):
            event = cast(StartEventObject, eventObj)
            self.onStartEvent(event)
        elif isinstance(eventObj, SetSchedulerEventObject):
            event = cast(SetSchedulerEventObject, eventObj)
            self.onSetSchedulerEvent(event)

    def onFileEvent(self, event: FileEventObject):
        pass

    def onRepositoryEvent(self, event: RepositoryEventObject):
        pass

    def onStartEvent(self, event: StartEventObject):
        pass

    def onSetSchedulerEvent(self, event: SetSchedulerEventObject):
        pass

    def set_attr(self, key: str, value) -> None:
        if value:
            self._attr_extra_state_attributes[key] = value
        elif key in self._attr_extra_state_attributes:
            del(self._attr_extra_state_attributes[key])

class TimerCoordinatorSensor(ConnectorSensor):
    def __init__(self, connector: SensorConnector):
        ConnectorSensor.__init__(self, connector, icon=ICON_TIMER)
        self._attr_name = f"{self._name_prefix} timer"
        self._attr_should_poll = True

    @property
    def should_poll(self) -> bool:
        """No need to poll. Coordinator notifies entity of updates."""
        return True

    def onSetSchedulerEvent(self, event: SetSchedulerEventObject):
        delta = event.NextRun - datetime.now()
        self._attr_native_value = to_short_human_readable_delta(delta)

class TransferCoordinatorSensor(ConnectorSensor):

    def __init__(self, connector: SensorConnector):
        ConnectorSensor.__init__(self, connector)
        self._attr_name = f"{self._name_prefix} files"
        self._state = TransferState()

    def update(self):
        state = self._state
        self._attr_native_value = state.files_count
        self.set_attr(ATTR_SIZE_MB, state.files_size_mb)
        self.set_attr(ATTR_EXTENSIONS, state.files_ext)
        self.set_attr(ATTR_LAST_IMAGE, state.last_image)
        self.set_attr(ATTR_LAST_VIDEO, state.last_video)
        last_time = to_short_human_readable(state.last_datetime)
        self.set_attr(ATTR_LAST_DATETIME, last_time)
        last_time = to_human_readable(state.last_datetime)
        self.set_attr(ATTR_LAST_DATETIME_FULL, last_time)

class ComponentLastTimeSensor(ConnectorSensor):
    def __init__(self, connector: SensorConnector):
        super().__init__(connector)
        self._attr_name = f"{self._name_prefix}: last time"
        self._attr_icon = ICON_LAST

    def onFileEvent(self, event: FileEventObject):
        self._attr_native_value = to_human_readable(event.File)

class ComponentLastFileSensor(ConnectorSensor):
    def __init__(self, connector: SensorConnector):
        super().__init__(connector, icon=connector.icon)
        self._attr_name = f"{self._name_prefix} {connector.id}"

    def onFileEvent(self, event: FileEventObject):
        self._attr_native_value = event.File.fullname

class ComponentRepoSensor(TransferCoordinatorSensor):
    def __init__(self, connector: SensorConnector):
        super().__init__(connector)
        self._attr_icon = ICON_TO_COPY

    def onRepositoryEvent(self, event: RepositoryEventObject):
        self._state = TransferState()
        self._state.extend(event.Files)
        self.update()

class ComponentFileSensor(TransferCoordinatorSensor):
    def __init__(self, connector: SensorConnector):
        super().__init__(connector)
        self._state = TransferState()
        self._attr_icon = ICON_COPIED

    def onFileEvent(self, event: FileEventObject):
        self._state.append(event.File)
        self.update()


_SENSOR_TYPES = {
    CONF_SENSOR_TYPE_REPOSITORY_STAT: ComponentRepoSensor,
    CONF_SENSOR_TYPE_TRANSFER_STAT: ComponentFileSensor,
    CONF_SENSOR_TYPE_TIMER: TimerCoordinatorSensor,
    CONF_SENSOR_TYPE_LAST_FILE: ComponentLastFileSensor,
    CONF_SENSOR_TYPE_LAST_TIME: ComponentLastTimeSensor
}

class SensorBuilder:

    def __init__(self, desc: SensorConnector) -> None:
        self._description = desc

    def build(self) -> SensorEntity:
        ctor = _SENSOR_TYPES[self._description.type]
        return ctor(self._description)

async def async_setup_platform(hass: HomeAssistant, config: ConfigEntry, add_entities, discovery_info=None):
    instName = discovery_info[ATTR_NAME]
    sensors_desc: list[SensorConnector] = discovery_info[ATTR_SENSORS]
    # storage = MemoryStorage(hass, instName)
    logger = getLogger(__name__, instName)

    sensors = []
    for desc in sensors_desc:
        if desc.platform.value != _PLATFORM:
            continue

        ctor = _SENSOR_TYPES[desc.type]
        sensor = ctor(desc)
        sensors.append(sensor)
        logger.debug(f"Add sensor -> path: '{desc.pipeline_path}'; name: '{sensor.name}'")

    add_entities(sensors)


