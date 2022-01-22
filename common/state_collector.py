from homeassistant.core import callback
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

from ..const import ATTR_ID, ATTR_TRANSFER_STATE, CONF_ENABLE
from .ifile_info import IFileInfo
from .transfer_component import TransferComponentId
from .transfer_state import TransferState


class StateCollector:

    def __init__(self, id: TransferComponentId, coordinator: DataUpdateCoordinator) -> None:
        self._state = TransferState()
        self._coordinator = coordinator
        self._coordinator.data = {
            ATTR_ID: id,
            CONF_ENABLE: True,
            ATTR_TRANSFER_STATE: None,
        }
        self._id = id

    @property
    def coordinator(self) -> DataUpdateCoordinator:
        return self._coordinator

    @callback
    def set(self, _: TransferComponentId, files: list[IFileInfo]):
        self._state = TransferState()
        self._state.extend(files)
        self._update_coordinator()

    @callback
    def append(self, _: TransferComponentId, file: IFileInfo, content = None):
        self._state.append(file)
        self._update_coordinator()

    def _update_coordinator(self) -> None:
        data = self._coordinator.data
        data[ATTR_TRANSFER_STATE] = self._state
        self._coordinator.async_set_updated_data(data)

    def __str__(self):
        return f"[Collector: ID# {self._id} {self._state}]"

    def __repr__(self):
        return self.__str__()
