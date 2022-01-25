from datetime import datetime
import mimetypes
from pathlib import Path

mimetypes.init()

class IFileInfo:

    def __init__(self) -> None:
        self._fullname: str = None
        self._datetime: datetime = None
        self.metadata = {}

    @property
    def size(self) -> int:
        return self._size

    @property
    def basename(self) -> str:
        pass

    @property
    def dirname(self) -> str:
        path = Path(self.fullname)
        return path.parent

    @property
    def fullname(self) -> str:
        return self._fullname

    @property
    def modif_datetime(self) -> datetime:
        pass

    @property
    def datetime(self) -> datetime:
        return self._datetime

    @datetime.setter
    def datetime(self, value):
        self._datetime = value

    @property
    def ext(self) -> str:
        pass

    @property
    def fullnameWithoutExt(self) -> str:
        pass

    @property
    def files_size_mb(self) -> float:
        return round(self.size / 1024 / 1024, 2)

    @property
    def mimetype(self) -> str:
        ''' video or image '''
        if not self.basename:
            return "unknown"
        mimestart = mimetypes.guess_type(self.basename)[0] or "unknown/ext"
        return mimestart.split('/')[0]

    def __str__(self):
         return f"{self.basename} @{self.dirname} {self.files_size_mb}Mb"

    def __repr__(self):
        return self.__str__()
