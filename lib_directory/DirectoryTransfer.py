from homeassistant.config_entries import ConfigEntry

from ..common.ifile_info import IFileInfo
from .file_info import FileInfo
from ..common.transfer_component import TransferComponent
from ..common.transfer_state import TransferState
from ..const import ATTR_DESTINATION_FILE, ATTR_LOCAL_FILE, ATTR_SOURCE_HOST, CONF_DATETIME_PATTERN, CONF_PATH
import os, io, logging, shutil, socket
from pathlib import Path

_LOGGER = logging.getLogger(__name__)

class DirectoryTransfer(TransferComponent):
    def __init__(self, config: ConfigEntry):
        super().__init__(config)

    def state(self) -> TransferState:
        return self.list_files()

    def list_files(self, onfileCallback = None) -> TransferState:
        startpath = self._config[CONF_PATH]
        _LOGGER.debug(f"Stat from [{startpath}]: START")
        state = TransferState()
        for root, _, files in os.walk(startpath):
            for f in files:
                root = root.replace('\\', '/')
                full_path = f"{root}/{f}"
                fileInfo = FileInfo(full_path)
                dt = self.filename_datetime(fileInfo)
                if dt == None:
                    continue # ignore file
                fileInfo.datetime = dt

                state.append(fileInfo)
                if onfileCallback:
                    onfileCallback(fileInfo)
                
                if state.files_count >= self._copied_per_run:
                    break
            if state.files_count >= self._copied_per_run:
                break

        _LOGGER.debug(f"Stat from [{startpath}]: END, {state}")
        return state

    def run(self) -> TransferState:
        def onfile(fileInfo: IFileInfo):
            self.download(fileInfo)
            self._on_file_transfer(fileInfo)

        return self.list_files(onfile)

    def download(self, file: IFileInfo) -> None:
        _LOGGER.debug(f"Read file: [{file.fullname}] => [memory]")
        hostname = socket.gethostname()
        local_ip = socket.gethostbyname(hostname)
        file.metadata[ATTR_SOURCE_HOST] = local_ip

        with open(file.fullname, 'rb') as infile:
            file.Content=io.BytesIO(infile.read())

    def from_component_download_to_local_finished_callback(self, callbackObject: IFileInfo) -> None:
        print(callbackObject)
        rel_path = callbackObject.datetime.strftime(self._config[CONF_DATETIME_PATTERN])
        filename = f"{self._config[CONF_PATH]}/{rel_path}.{callbackObject.ext}"
        self.mkdir(filename)
        if callbackObject.Content:
            _LOGGER.debug(f"Save file: [memory] => [{filename}]")
            with callbackObject.Content:
                with open(filename, 'wb') as outfile:
                    outfile.write(callbackObject.Content.read())
                    callbackObject.Content.close()
        else:
            _LOGGER.debug(f"Copy file: [{callbackObject.fullname}] => [{filename}]")
            shutil.copyfile(callbackObject.fullname, filename)

        ''' File transffered declaration '''
        if self.copiedFileCallback:
            self.copiedFileCallback({
                ATTR_LOCAL_FILE: callbackObject,
                ATTR_DESTINATION_FILE: filename
            })

    def mkdir(self, filename: str):
        path = Path(Path(filename).parent)
        path.mkdir(parents=True, exist_ok=True)
