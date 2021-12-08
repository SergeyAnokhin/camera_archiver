from datetime import datetime, timedelta
import os

class TransferState:

    def __init__(self) -> None:
        self._filenames = []
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

    def add(self, filename: str, size: int) -> None:
        self._filenames.append(filename)
        self._size += size
        _, ext = os.path.splitext(filename)

        if ext not in self._size_by_ext:
            self._size_by_ext[ext] = 0

        self._size_by_ext[ext] += size

    def duration(self) -> timedelta:
        return self._duration

    def files_count(self) -> int:
        return len(self._filenames)

    def files_ext(self) -> str:
        return ' '.join([ ext.lstrip(".") for ext in self._size_by_ext ])

    def files_size(self) -> int:
        return self._size

    def files_size_mb(self) -> float:
        return round(self.files_size() / 1024 / 1024, 2) 

    def __str__(self):
        result = ""
        result += f" Files: {self.files_count()} "
        result += f" Size: {(self._size / 1024 / 1024):.1f} Mb"
        result += " Extension: "
        result += ', '.join([ ext for ext in self._size_by_ext ])
        return result