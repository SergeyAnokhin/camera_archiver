import re
from typing import Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from ..common.ifile_info import IFileInfo
from ..common.transfer_component import TransferComponent
from ..common.transfer_component_id import TransferComponentId
from ..const import ATTR_HASS_STORAGE_MEMORY, CONF_CAMERA, CONF_FILTER, DOMAIN


class CameraTransfer(TransferComponent):
    platform = CONF_CAMERA

    def __init__(self, id: TransferComponentId, hass: HomeAssistant, config: ConfigEntry):
        super().__init__(id, hass, config)
        self._regex_filter = None
        if CONF_FILTER in config:
            pattern = config[CONF_FILTER]
            self._regex_filter = re.compile(pattern)

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
        if not self._regex_filter.match(file.basename):
            return None

        entity_storage = self._hass.data[DOMAIN][self._id.Entity]
        if ATTR_HASS_STORAGE_MEMORY not in entity_storage:
            entity_storage[ATTR_HASS_STORAGE_MEMORY] = {}

        entity_storage[ATTR_HASS_STORAGE_MEMORY][self._id.id] = content

        return self._id.id
