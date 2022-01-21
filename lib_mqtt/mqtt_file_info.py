from datetime import datetime
from ..common.ifile_info import IFileInfo


class MqttFileInfo(IFileInfo):

    def __init__(self, topic: str, buffer: bytes) -> None:
        super().__init__()
        self._ext = ".jpg"
        self._fullname = topic
        self._name = topic
        self._size = len(buffer)
        self._modif_datetime = datetime.now()
        self._datetime = datetime.now()

    @property
    def basename(self) -> str:
        return self._name

    @property
    def modif_datetime(self) -> datetime:
        return self._modif_datetime

    @property
    def ext(self) -> str:
        return self._ext.lstrip(".")

    @property
    def fullnameWithoutExt(self) -> str:
        return self._name
