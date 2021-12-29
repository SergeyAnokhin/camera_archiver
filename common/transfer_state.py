from datetime import datetime, timedelta
from enum import Enum
import os

from .ifile_info import IFileInfo


class StateType(Enum):
    READ = "Read"
    COPY = "Copy"

class TransferState:

    def __init__(self) -> None:
        self.read = RunState(StateType.READ)
        self.copy = RunState(StateType.COPY)

    @property
    def Read(self):
        return self.read

    @property
    def Copy(self):
        return self.copy

class RunState: 
    def __init__(self, type: StateType) -> None:
        self._type = type
        self._files: list[str] = []
        self._size = 0
        self._size_by_ext = {}
        self._start = datetime.now()
        self._stop = datetime.now()
        self._duration = timedelta()
        self._last = None
        self._last_by_ext = {}

    def start(self) -> None:
        self._start = datetime.now()

    def stop(self) -> int:
        self._stop = datetime.now()
        self._duration = self._stop - self._start
        return self._duration.seconds

    def append(self, file: IFileInfo) -> None:
        self._files.append(file.fullname)
        self._size += file.size
        if file.ext not in self._size_by_ext:
            self._size_by_ext[file.ext] = 0
        self._size_by_ext[file.ext] += file.size
        self._last = file.fullname
        self._last_by_ext[file.ext] = file.fullname

    def extend(self, files: list[IFileInfo]) -> None:
        [self.append(f) for f in files]

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
    def last(self) -> str:
        return self._last

    @property
    def last_by_ext(self, ext: str) -> str:
        return self._last_by_ext[ext]

    @property
    def files_size_mb(self) -> float:
        return round(self.files_size / 1024 / 1024, 2) 

    def __str__(self):
        result = f"[Stat:{self._type.name}] Files: {self.files_count} "
        result += f" Size: {(self.files_size_mb):.1f}Mb"
        result += " Extensions: "
        result += self.files_ext
        return result

    def __repr__(self):
        return self.__str__()
