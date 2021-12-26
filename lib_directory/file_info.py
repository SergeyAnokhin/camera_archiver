import os
from datetime import datetime
from ..common.ifile_info import IFileInfo

class FileInfo(IFileInfo):

    def __init__(self, fullname: str) -> None:
        super().__init__()
        self._fullname = fullname
        self._fullname_without_ext, self._ext = os.path.splitext(self._fullname)

    @property
    def size(self) -> int:
        return os.path.getsize(self._fullname)

    @property
    def basename(self) -> str:
        return os.path.basename(self._fullname)

    @property
    def modif_datetime(self) -> datetime:
        return datetime.fromtimestamp(os.path.getmtime(self._fullname))

    @property
    def ext(self) -> str:
        return self._ext.lstrip(".")

    @property
    def fullnameWithoutExt(self) -> str:
        return self._fullname_without_ext
