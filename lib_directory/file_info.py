import os
from datetime import datetime
from ..common.ifile_info import IFileInfo

class FileInfo(IFileInfo):

    def __init__(self, fullname: str) -> None:
        super().__init__()
        self._fullname = fullname
        self._fullname_without_ext, self._ext = os.path.splitext(self._fullname)
        self._stat = os.stat(self._fullname)
        self._size = self._stat.st_size
        self._modif_datetime = self._stat.st_mtime

    @property
    def basename(self) -> str:
        return os.path.basename(self._fullname)

    @property
    def modif_datetime(self) -> datetime:
        return datetime.fromtimestamp(self._modif_datetime)

    @property
    def ext(self) -> str:
        return self._ext.lstrip(".")

    @property
    def fullnameWithoutExt(self) -> str:
        return self._fullname_without_ext
