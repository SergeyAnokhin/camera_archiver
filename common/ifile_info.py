from datetime import datetime

class IFileInfo:
    @property
    def size(self) -> int:
        pass

    @property
    def basename(self) -> str:
        pass

    @property
    def modif_datetime(self) -> datetime:
        pass

    @property
    def ext(self) -> str:
        pass

    @property
    def files_size_mb(self) -> float:
        return round(self.size / 1024 / 1024, 2)
