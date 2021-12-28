from datetime import datetime
from ftplib import FTP
import os
from .FtpDirLine import FtpDirLine
from ..common.ifile_info import IFileInfo

class FtpFileInfo(IFileInfo):
    
    def __init__(self, path: str, dirline: str):
        # -rw-r--r-- 1 user group           4467 Mar 27  2018  file1.zip
        # -rw-r--r-- 1 user group         124529 Jun 18 15: 31 file2.zip
        super().__init__()
        self._ftpDirLine = FtpDirLine(dirline)
        self.path = path
        self._name = self._ftpDirLine.name
        self._fullname = f'{self.path}/{self._name}'
        self.is_dir = self._ftpDirLine.is_dir
        self.is_file = self._ftpDirLine.is_file
        self._size = self._ftpDirLine.size
        self.metadata['ftp_date'] = self._ftpDirLine.modif_datetime_source
    
    @property
    def size(self) -> int:
        return self._size

    @property
    def basename(self) -> str:
        return self._name

    @property
    def modif_datetime(self) -> datetime:
        return self._ftpDirLine.modif_datetime

    @property
    def ext(self) -> str:
        _, ext = os.path.splitext(self._name)
        return ext

    @property
    def fullnameWithoutExt(self) -> str:
        withoutExt, _ = os.path.splitext(self.fullname)
        return withoutExt

    def relname(self, root: str) -> str:
        return self._fullname.lstrip(root).lstrip("/")
