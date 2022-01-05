from io import BytesIO
import os
from datetime import datetime
from ..common.ifile_info import IFileInfo


class MqttFileInfo(IFileInfo):

    def __init__(self, buffer: bytes) -> None:
        super().__init__()
        self._fullname = ""
        self._ext = ".jpg"
        self._size = len(buffer)
        self._modif_datetime = datetime.now()
        self._datetime = datetime.now()

    @property
    def basename(self) -> str:
        return ""

    @property
    def modif_datetime(self) -> datetime:
        return self._modif_datetime

    @property
    def ext(self) -> str:
        return self._ext.lstrip(".")

    @property
    def fullnameWithoutExt(self) -> str:
        return ""
