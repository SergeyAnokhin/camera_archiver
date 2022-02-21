from ..common.ifile_info import IFileInfo
from ..const import CONF_METADATA
from homeassistant.core import HomeAssistant
from ..common.component import Component

class MetadataComponent(Component):
    Platform = CONF_METADATA

    def __init__(self, hass: HomeAssistant, config: dict) -> None:
        super().__init__(hass, config)

    def file_save(self, file: IFileInfo, _) -> IFileInfo:
        for key, value in self._data:
            file.metadata[key] = value
        return file
