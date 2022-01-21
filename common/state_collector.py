from .ifile_info import IFileInfo
from homeassistant.core import callback
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator
from .transfer_state import StateType, TransferState


class StateCollector:

    def __init__(self, coordinator: DataUpdateCoordinator) -> None:
        self._states = {type: TransferState(type)  for type in StateType}
        self._coordinator = coordinator

    @callback
    def append_repository(self, files: list[IFileInfo]):
        repo: TransferState = self._states[StateType.REPOSITORY]
        repo.extend(files)

    @callback
    def append_read(self, file: IFileInfo, content):
        read: TransferState = self._states[StateType.READ]
        read.append(file)

    @callback
    def append_save(self, file: IFileInfo):
        save: TransferState = self._states[StateType.SAVE]
        save.append(file)
