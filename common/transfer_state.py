from datetime import datetime, timedelta
import os

from .ifile_info import IFileInfo

class TransferState:

    def __init__(self) -> None:
        self._files: list[str] = []
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

    def add(self, file: IFileInfo) -> None:
        self._files.append(file.fullname)
        self._size += file.size
        if file.ext not in self._size_by_ext:
            self._size_by_ext[file.ext] = 0
        self._size_by_ext[file.ext] += file.size

    @property
    def duration(self) -> timedelta:
        return self._duration

    @property
    def files_count(self) -> int:
        return len(self._files)

    @property
    def files_ext(self) -> str:
        return ' '.join(self._size_by_ext.keys())

    @property
    def files_size(self) -> int:
        return self._size

    @property
    def files_size_mb(self) -> float:
        return round(self.files_size / 1024 / 1024, 2) 

    def __str__(self):
        result = f"[Stat] Files: {self.files_count} "
        result += f" Size: {(self.files_size_mb):.1f} Mb"
        result += " Extension: "
        result += self.files_ext
        return result
