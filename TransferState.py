import os

class TransferState:

    def __init__(self) -> None:
        self._filenames = []
        self._size = 0
        self._size_by_ext = {}

    def add(self, filename: str, size: int) -> None:
        self._filenames.append(filename)
        self._size += size
        _, ext = os.path.splitext(filename)

        if ext not in self._size_by_ext:
            self._size_by_ext[ext] = 0

        self._size_by_ext[ext] += size

    def files_count(self) -> int:
        return len(self._filenames)

    def files_size(self) -> int:
        return self._size