from typing import Any
from homeassistant.config_entries import ConfigEntry

from ..common.ifile_info import IFileInfo
from .file_info import FileInfo
from ..common.transfer_component import TransferComponent
from ..const import ATTR_PATH, ATTR_SOURCE_HOST, CONF_DATETIME_PATTERN
import os, io, logging, socket
from pathlib import Path

_LOGGER = logging.getLogger(__name__)

class DirectoryTransfer(TransferComponent):
    def __init__(self, config: ConfigEntry):
        super().__init__(config)

    def get_files(self) -> list[IFileInfo]:
        ''' OVERRIDE '''
        files: list[IFileInfo] = []
        for root, _, walk_files in os.walk(self._path):
            for walk_file in walk_files:
                file = FileInfo(f"{root}/{walk_file}")
                if self.validate_file(file):
                    files.append(file)
        return files

    def file_read(self, file: IFileInfo) -> Any:
        ''' OVERRIDE '''
        hostname = socket.gethostname()
        local_ip = socket.gethostbyname(hostname)
        file.metadata[ATTR_SOURCE_HOST] = local_ip

        with open(file.fullname, 'rb') as infile:
            return io.BytesIO(infile.read())

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
