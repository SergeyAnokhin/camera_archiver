import io
import logging
from typing import Any

from homeassistant.config_entries import ConfigEntry
from ..common.ifile_info import IFileInfo
from ..common.transfer_component import TransferComponent
from ..const import ATTR_PATH, CONF_DATETIME_PATTERN

from .FtpConn import FtpConn
from .ftp_file_info import FtpFileInfo

_LOGGER = logging.getLogger(__name__)

class FtpTransfer(TransferComponent):
    def __init__(self, config: ConfigEntry):
        super().__init__(config)

    def get_files(self) -> list[IFileInfo]:
        ''' OVERRIDE '''
        files: list[IFileInfo] = []
        with FtpConn(self._config) as ftp:
            # ftp.cd(self._config[CONF_PATH])
            self.get_items(ftp, self._path, files)
        return files

    def get_items(self, ftp: FtpConn, path: str, files: list[IFileInfo]):
        items = self.get_file_infos(ftp, path)
        for i in items:
            if i.is_dir:
                self.get_items(ftp, path + '/' + i.basename, files)
            elif self.validate_file(i):
                files.append(i)

    def get_file_infos(self, ftp: FtpConn, path: str) -> list[IFileInfo]:
        lines = ftp.GetFtpDir(path)
        return [FtpFileInfo(path, line) for line in lines]

    def file_read(self, file: IFileInfo) -> Any:
        ''' OVERRIDE '''
        with FtpConn(self._config) as ftp:
            return ftp.DownloadBytes(file.fullname)

    def file_save(self, file: IFileInfo, content) -> None:
        ''' OVERRIDE '''
        rel_path = file.datetime.strftime(self._config[CONF_DATETIME_PATTERN])
        filename = f"{self._path}/{rel_path}{file.ext}"

        if isinstance(content, io.BytesIO): 
            with content:
                with FtpConn(self._config) as ftp:
                    ftp.UploadBytes(content, filename)
                content.close()
        else:
            raise Exception(f'Unknown content type to save: {type(content)}')

        return filename
