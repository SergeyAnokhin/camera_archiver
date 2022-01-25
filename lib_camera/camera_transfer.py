from typing import Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from ..common.ifile_info import IFileInfo
from ..common.transfer_component import TransferComponent
from ..common.transfer_component_id import TransferComponentId
from ..const import CONF_CAMERA


class CameraTransfer(TransferComponent):
    platform = CONF_CAMERA

    def __init__(self, id: TransferComponentId, hass: HomeAssistant, config: ConfigEntry):
        super().__init__(id, hass, config)

    def get_files(self, max=None) -> list[IFileInfo]:
        ''' OVERRIDE '''
        files: list[IFileInfo] = []
        return files

    def file_read(self, file: IFileInfo) -> Any:
        ''' OVERRIDE '''
        pass

    def file_delete(self, file: IFileInfo):
        ''' OVERRIDE '''
        pass

    def file_save(self, file: IFileInfo, content) -> str:
        ''' OVERRIDE '''
        return None
