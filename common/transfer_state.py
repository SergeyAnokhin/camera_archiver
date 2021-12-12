from datetime import datetime, timedelta
import os

from .common.ifile_info import IFileInfo

class TransferState:

    def __init__(self) -> None:
        self._files = list[IFileInfo]
        self._size = 0
        self._size_by_ext = {}
        self._start = datetime.now()
        self._stop = datetime.now()
        self._duration = timedelta()

    def start(self) -> None:
        self._start = datetime.now()

    def stop(self) -> int:
        self._stop = datetime.now()
        self._duration = self._stop - self._start
        return self._duration.seconds

    def duration(self) -> timedelta:
        return self._duration

    def add(self, file: IFileInfo) -> None:
        self._files.append(file)

    def files_count(self) -> int:
        return len(self._files)

    def files_ext(self) -> str:
        extensions = set([f.ext for f in self._files])
        return ' '.join(extensions)

    def files_size(self) -> int:
        return sum([f.size for f in self._files])

    def files_size_mb(self) -> float:
        return round(self.files_size() / 1024 / 1024, 2) 

    def __str__(self):
        result = f" Files: {self.files_count()} "
        result += f" Size: {(self._size / 1024 / 1024):.1f} Mb"
        result += " Extension: "
        result += self.files_ext()
        return result
