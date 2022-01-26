from abc import abstractmethod
from datetime import datetime

from homeassistant.core import callback
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

from ..const import (ATTR_CONTENT, ATTR_ENABLE, ATTR_ID, ATTR_TRANSFER_STATE,
                     MIMETYPE_IMAGE)
from .ifile_info import IFileInfo
from .transfer_component import TransferComponentId
from .transfer_state import EventType, TransferState


class AbstractCollector:
    def __init__(self, id: TransferComponentId, stateType: EventType, coordinator: DataUpdateCoordinator) -> None:
        self._state = None
        self._listeners = []
        self._coordinator = coordinator
        self._coordinator.data = {
            ATTR_ID: id,
            ATTR_ENABLE: True,
            ATTR_TRANSFER_STATE: None,
        }
        self._coordinator.async_add_listener(self._coordinator_updated)
        self._coordinator.update_method = self._coordinator_update_method
        self._id = id
        self._stateType = stateType

    @property
    def coordinator(self) -> DataUpdateCoordinator:
        return self._coordinator

    async def _coordinator_update_method(self):
        data = self._coordinator.data
        data[ATTR_TRANSFER_STATE] = self._state
        return data

    def _update_coordinator(self) -> None:
        data = self._coordinator.data
        data[ATTR_TRANSFER_STATE] = self._state
        self._coordinator.async_set_updated_data(data)

    def _coordinator_updated(self):
        for callback in self._listeners:
            callback(self._stateType, self._coordinator.data)

    def add_listener(self, callback):
        self._listeners.append(callback)

    def __str__(self):
        return f"[Collector: ID# {self._id} {self._state}]"

    def __repr__(self):
        return self.__str__()

    @abstractmethod
    @callback
    def append(self, _: TransferComponentId, value) -> None:
        pass


class SetObjectCollector(AbstractCollector):

    def __init__(self, id: TransferComponentId, stateType: EventType, coordinator: DataUpdateCoordinator) -> None:
        super().__init__(id, stateType, coordinator)

    @callback
    def append(self, _: TransferComponentId, value) -> None:
        self._state = value
        self._update_coordinator()

class FilesSetCollector(AbstractCollector):

    def __init__(self, id: TransferComponentId, stateType: EventType, coordinator: DataUpdateCoordinator) -> None:
        super().__init__(id, stateType, coordinator)
        self._state = TransferState()

    @callback
    def append(self, _: TransferComponentId, files: list[IFileInfo]) -> None:
        self._state = TransferState()
        self._state.extend(files)
        self._update_coordinator()

class FileAppenderCollector(AbstractCollector):

    def __init__(self, id: TransferComponentId, stateType: EventType, coordinator: DataUpdateCoordinator) -> None:
        super().__init__(id, stateType, coordinator)
        self._state = TransferState()

    @callback
    def append(self, _: TransferComponentId, file: IFileInfo, content = None) -> None:
        self._state.append(file)
        self._update_coordinator() 

