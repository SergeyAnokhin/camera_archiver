from datetime import datetime

class IFileInfo:

    def __init__(self) -> None:
        self._fullname: str = None
        self._datetime: datetime = None
        self.metadata = {}

    @property
    def size(self) -> int:
        pass

    @property
    def basename(self) -> str:
        pass

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
