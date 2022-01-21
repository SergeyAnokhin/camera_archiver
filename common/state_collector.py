from .ifile_info import IFileInfo
from homeassistant.core import callback
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator
from .transfer_state import StateType, TransferState


class StateCollector:

    def __init__(self, coordinator: DataUpdateCoordinator) -> None:
        self._states = {type: TransferState(type)  for type in StateType}
        self._coordinator = coordinator

    @callback
    def new_state(self, stateType: StateType, file: IFileInfo):
        state = self._states[stateType]
        state.append(file)