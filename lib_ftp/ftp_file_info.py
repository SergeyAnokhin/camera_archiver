from datetime import datetime
from ftplib import FTP
import os
from dateutil import parser

from ..common.ifile_info import IFileInfo

class FtpFileInfo(IFileInfo):
    
    def __init__(self, path: str, dirline: str):
        # -rw-r--r-- 1 user group           4467 Mar 27  2018  file1.zip
        # -rw-r--r-- 1 user group         124529 Jun 18 15: 31 file2.zip
        super().__init__()
        self.parts = dirline.split(maxsplit=9)
        self.path = path
        self._name = self.parts[-1]
        self._time_str = self.parts[5] + " " + self.parts[6] + " " + self.parts[7]
        self._fullname = f'{self.path}/{self.parts[-1]}'
        self.is_dir = self.parts[0].startswith('d')
        self.is_file = self.parts[0].startswith('-')
        self.icon = '' if self.is_dir else ''
        self._size = int(self.parts[4])
    
    @property
    def size(self) -> int:
        return self._size

    @property
    def basename(self) -> str:
        return self._name

    @property
    def modif_datetime(self) -> datetime:
        # https://stackoverflow.com/questions/29026709/how-to-get-ftp-files-modify-time-using-python-ftplib
        parser.parse(self._time_str)

    @property
    def ext(self) -> str:
        _, ext = os.path.splitext(self._name)
        return ext

    @property
    def fullnameWithoutExt(self) -> str:
        withoutExt, _ = os.path.splitext(self._name)
        return withoutExt

    def relname(self, root: str) -> str:
        return self._fullname.lstrip(root).lstrip("/")

    def __str__(self):
         return f"{self._name} {self.size()}"
