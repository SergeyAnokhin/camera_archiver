from homeassistant.config_entries import ConfigEntry

from ..common.ifile_info import IFileInfo
from .file_info import FileInfo
from ..common.transfer_component import TransferComponent
from ..common.transfer_state import TransferState
from ..const import ATTR_DESTINATION_FILE, ATTR_LOCAL_FILE, ATTR_SOURCE_FILE, ATTR_SOURCE_FILE_CREATED, ATTR_SOURCE_HOST, CONF_DATETIME_PATTERN, CONF_PATH
import os, io, logging, shutil, socket
from pathlib import Path

_LOGGER = logging.getLogger(__name__)

class DirectoryTransfer(TransferComponent):
    def __init__(self, config: ConfigEntry):
        super().__init__(config)

    def state(self) -> TransferState:
        path = self._config[CONF_PATH]
        return self.list_files(path)

    def list_files(self, startpath: str, local_path: str = None) -> TransferState:
        _LOGGER.debug(f"Stat from [{startpath}]: START")
        state = TransferState()
        for root, dirs, files in os.walk(startpath):
            # os.path.basename(root)
            for f in files:
                # rel_path = root.replace(startpath, '').lstrip('/').lstrip('\\')  # .count(os.sep)
                root = root.replace('\\', '/')
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
        local_file = f"{local_path}.{file.ext}"
        _LOGGER.debug(f"Read file: [{file.fullname}] => [memory]")
        #_LOGGER.debug(f"Copy file: [{file.fullname}] => [{local_file}]")
        # shutil.copyfile(file.fullname, local_file)
        new_file = FileInfo(local_file)
        new_file.datetime = file.datetime
        new_file.metadata[ATTR_SOURCE_FILE] = file.fullname
        new_file.metadata[ATTR_SOURCE_FILE_CREATED] = file.modif_datetime

        hostname = socket.gethostname()
        local_ip = socket.gethostbyname(hostname)
        new_file.metadata[ATTR_SOURCE_HOST] = local_ip

        with open(file.fullname, 'rb') as infile:
            new_file.Content=io.BytesIO(infile.read())

        return new_file

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


# import io

# with open("/config/www/snapshot/camera.Yi1080pWoodSouth.mp4",'rb') as infile:
#     buffer=io.BytesIO(infile.read())
# print(buffer)
# with open("/config/www/snapshot/camera.Yi1080pWoodSouth_2.mp4",'wb') as outfile: ## Open temporary file as bytes
#     outfile.write(buffer.read())                ## Read bytes into file
