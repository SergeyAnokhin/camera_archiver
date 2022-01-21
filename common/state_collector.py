from ntpath import join

from .transfer_component import TransferComponentId
from .ifile_info import IFileInfo
from homeassistant.core import CALLBACK_TYPE, callback
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator
from .transfer_state import StateType, TransferState


class StateCollector:

    def __init__(self) -> None:
        self._states = {type: {}  for type in StateType}
        self._listeners = []

    @callback
    def append_repository(self, sender: TransferComponentId, files: list[IFileInfo]):
        ''' override old values '''
        #repo: TransferState = self._states[StateType.REPOSITORY]
        repo = TransferState(StateType.REPOSITORY)
        repo.extend(files)
        self._states[StateType.REPOSITORY] = repo
        self._invoke_listeners(StateType.REPOSITORY, sender)

    @callback
    def append_read(self, sender: TransferComponentId, file: IFileInfo, content):
        read: TransferState = self._states[StateType.READ]
        read.append(file)
        self._invoke_listeners(StateType.REPOSITORY, sender)

    @callback
    def append_save(self, sender: TransferComponentId, file: IFileInfo):
        save: TransferState = self._states[StateType.SAVE]
        save.append(file)
        self._invoke_listeners(StateType.SAVE, sender)

    def add_listener(self, update_callback: CALLBACK_TYPE) -> None:
        """Listen for data updates."""
        self._listeners.append(update_callback)

    def _invoke_listeners(self, stateType: StateType, sender: TransferComponentId) -> None:
        for callback in self._listeners:
            callback(stateType, sender, self)

    def __str__(self):
        types = " ".join([f"{key}:{state.files_count}" for key, state in self._states.items()])
        return f"[Collector: {types}"

    def __repr__(self):
        return self.__str__()
