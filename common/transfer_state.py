from datetime import datetime, timedelta
from enum import Enum

from ..const import ATTR_TARGET_FILE, MIMETYPE_IMAGE, MIMETYPE_VIDEO
from .ifile_info import IFileInfo


class EventType(Enum):
    REPOSITORY = "Repository"  # Read repository
    READ = "Read"  # Read files from repository in memory
    SAVE = "Save"  # Save file from memory to new repository
    SET_SCHEDULER = "set_scheduler" # scheduler updated

class TransferState:
    def __init__(self, type: EventType = None) -> None:
        self._type = type
        self._files: list[str] = []
        self._size = 0
        self._size_by_ext = {}
        self._start = datetime.now()
        self._stop = datetime.now()
        self._duration = timedelta()
        self._last_image = None
        self._last_video = None
        self._last_datetime = None

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

        type = file.mimetype
        if type == MIMETYPE_VIDEO:
            self._last_video = file
        elif type == MIMETYPE_IMAGE:
            self._last_image = file
        self._last_datetime = file.datetime

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
    def files_exts(self) -> list[str]:
        return list(self._size_by_ext.keys())

    @property
    def files_size(self) -> int:
        return self._size

    @property
    def last_image(self) -> str:
        return self._last_image.metadata[ATTR_TARGET_FILE] \
            if self._last_image and ATTR_TARGET_FILE in self._last_image.metadata \
            else ""

    @property
    def last_video(self) -> str:
        return self._last_video.metadata[ATTR_TARGET_FILE] \
            if self._last_video and ATTR_TARGET_FILE in self._last_video.metadata \
            else ""

    @property
    def last_datetime(self) -> str:
        return self._last_datetime

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
