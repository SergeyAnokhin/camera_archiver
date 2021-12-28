from datetime import datetime
import os, logging

from voluptuous.schema_builder import validate

from ..common.ifile_info import IFileInfo
from ..common.transfer_component import TransferComponent
from ..common.transfer_state import TransferState
from ..const import ATTR_DESTINATION_FILE, ATTR_LOCAL_FILE, CONF_COPIED_PER_RUN, CONF_DATETIME_PATTERN, CONF_FROM, CONF_FTP, CONF_PATH, CONF_TO

from .FtpConn import FtpConn
from .ftp_file_info import FtpFileInfo

_LOGGER = logging.getLogger(__name__)

class FtpTransfer(TransferComponent):
    def __init__(self, config: dict):
        self._config = config

    def get_files(self) -> list[IFileInfo]:
        stat = TransferState()
        with FtpConn(self._config) as ftp:
            # ftp.cd(self._config[CONF_PATH])
            items = self.get_items(ftp, self._config[CONF_PATH], stat)
        return items

    def get_items(self, ftp: FtpConn, path: str, stat: TransferState)  -> list[IFileInfo]:
        items = self.get_file_infos(ftp, path)
        files: list[IFileInfo] = []
        for i in items:
            if i.is_dir:
                sub_files = self.get_items(ftp, path + '/' + i.basename, stat)
                files.extend(sub_files)
            elif self.validate_file(i):
                stat.append(i)
                files.append(i)

            if stat.files_count >= self._config[CONF_COPIED_PER_RUN]:
                break

        return files

    def get_file_infos(self, ftp: FtpConn, path: str) -> list[IFileInfo]:
        lines = ftp.GetFtpDir(path)
        return [FtpFileInfo(path, line) for line in lines]

    def state(self) -> TransferState:
        _LOGGER.debug(f"Stat from [{self._config[CONF_PATH]}]: START")
        state = TransferState()
        res = self.get_files()
        state.extend(res)
        state.stop()
        _LOGGER.debug(f"Stat from [{self._config[CONF_PATH]}]: END, {state}")
        return state

    def run(self):
        _LOGGER.debug(f"Copy from [{self._config[CONF_PATH]}]: START")
        state = TransferState()
        files = self.get_files()
        state.extend(files)

        with FtpConn(self._config) as ftp:
            for file in files:
                file.Content = ftp.DownloadBytes(file.fullname)
                self._on_file_transfer(file)

        state.stop()
        _LOGGER.debug(f"Copy from [{self._config[CONF_PATH]}]: END, {state}")
        return state

    def from_component_download_to_local_finished_callback(self, callbackObject: IFileInfo) -> None:
        rel_path = callbackObject.datetime.strftime(self._config[CONF_DATETIME_PATTERN])
        filename = f"{self._config[CONF_PATH]}/{rel_path}{callbackObject.ext}"

        with callbackObject.Content:
            with FtpConn(self._config) as ftp:
                _LOGGER.debug(f"Save file: [memory] => [{filename}]")
                ftp.UploadBytes(callbackObject.Content, filename)
            callbackObject.Content.close()

        ''' File transffered declaration '''
        if self.copiedFileCallback:
            self.copiedFileCallback({
                ATTR_LOCAL_FILE: callbackObject,
                ATTR_DESTINATION_FILE: filename
            })
