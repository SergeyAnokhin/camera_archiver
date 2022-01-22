from homeassistant.core import callback
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

from ..const import ATTR_ID, ATTR_TRANSFER_STATE, ATTR_ENABLE
from .ifile_info import IFileInfo
from .transfer_component import TransferComponentId
from .transfer_state import StateType, TransferState


class StateCollector:

    def __init__(self, id: TransferComponentId, stateType: StateType, coordinator: DataUpdateCoordinator) -> None:
        self._state = TransferState()
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

    @callback
    def set(self, _: TransferComponentId, files: list[IFileInfo]) -> None:
        self._state = TransferState()
        self._state.extend(files)
        self._update_coordinator()

    @callback
    def append(self, _: TransferComponentId, file: IFileInfo, content = None) -> None:
        self._state.append(file)
        self._update_coordinator()

    def _coordinator_update_method(self) -> dict:
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
