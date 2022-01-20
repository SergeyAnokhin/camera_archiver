from typing import Any
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from ..common.ifile_info import IFileInfo
from .file_info import FileInfo
from ..common.transfer_component import TransferComponent
from ..const import ATTR_SOURCE_HOST, ATTR_SOURCE_TYPE, CONF_DATETIME_PATTERN
import os, io, logging, socket
from pathlib import Path

_LOGGER = logging.getLogger(__name__)

class DirectoryTransfer(TransferComponent):
    def __init__(self, hass: HomeAssistant, config: ConfigEntry):
        super().__init__(hass, config)

    def get_files(self, max=None) -> list[IFileInfo]:
        ''' OVERRIDE '''
        files: list[IFileInfo] = []
        for root, dirs, walk_files in os.walk(self._path):
            if self._clean_dirs and len(dirs) == len(walk_files) == 0 and root != self._path:
                _LOGGER.debug(f"Remove empty directory: {root}")
                os.rmdir(root)
            for walk_file in walk_files:
                file = FileInfo(f"{root}/{walk_file}")
                if self.validate_file(file):
                    files.append(file)
                if max and len(files) >= max:
                    break
            if max and len(files) >= max:
                break

        return files

    def file_read(self, file: IFileInfo) -> Any:
        ''' OVERRIDE '''
        hostname = socket.gethostname()
        local_ip = socket.gethostbyname(hostname)
        file.metadata[ATTR_SOURCE_HOST] = local_ip
        file.metadata[ATTR_SOURCE_TYPE] = "os"

        with open(file.fullname, 'rb') as infile:
            return io.BytesIO(infile.read())

    def file_delete(self, file: IFileInfo):
        ''' OVERRIDE '''
        # os.remove(file.fullname)
        pass

    def file_save(self, file: IFileInfo, content) -> str:
        ''' OVERRIDE '''
        rel_path = file.datetime.strftime(self._config[CONF_DATETIME_PATTERN])
        filename = f"{self._path}/{rel_path}.{file.ext}"
        self.mkdir(filename)
        if isinstance(content, io.BytesIO): 
            with content:
                with open(filename, 'wb') as outfile:
                    outfile.write(content.read())
                    content.close()
        else:
            raise Exception(f'Unknown content type to save: {type(content)}')

        return filename

    def mkdir(self, filename: str):
        path = Path(Path(filename).parent)
        path.mkdir(parents=True, exist_ok=True)
