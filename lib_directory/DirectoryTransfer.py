from homeassistant.config_entries import ConfigEntry

from ..common.ifile_info import IFileInfo
from .file_info import FileInfo
from ..common.transfer_component import TransferComponent
from ..common.transfer_state import TransferState
from ..const import CONF_DATETIME_PATTERN, CONF_PATH
import os
import logging

_LOGGER = logging.getLogger(__name__)

class DirectoryTransfer(TransferComponent):
    def __init__(self, config: ConfigEntry):
        super().__init__(config)

    def state(self) -> TransferState:
        path = self._config[CONF_PATH]
        return self.list_files(path)

    def list_files(self, startpath: str, local_path: str) -> TransferState:
        _LOGGER.debug(f"Stat from [{startpath}]: START")
        state = TransferState()
        for root, dirs, files in os.walk(startpath):
            # os.path.basename(root)
            for f in files:
                # rel_path = root.replace(startpath, '').lstrip('/').lstrip('\\')  # .count(os.sep)
                full_path = f"{root}/{f}"
                fileInfo = FileInfo(full_path)
                dt = self.filename_datetime(fileInfo)
                if dt == None:
                    continue # ignore file
                fileInfo.datetime = dt

                state.add(fileInfo)
                if local_path:
                    localfile = self.download(fileInfo, local_path)
                    self._on_file_transfer(localfile)

        _LOGGER.debug(f"Stat from [{startpath}]: END, {state}")
        return state

    def run(self, local_path: str) -> TransferState:
        path = self._config[CONF_PATH]
        return self.list_files(path, local_path)

    def download(self, file: IFileInfo, local_path: str) -> IFileInfo:
        pass

     def create_local_filename(self, file: IFileInfo, local_path: str) -> str:
        return f'{local_path}/camera.{self.config["camera"]["name"]}.{file.extension}'
