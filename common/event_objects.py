from datetime import datetime
from .ifile_info import IFileInfo
from .transfer_state import EventType

class EventObject:
    EventType = None    

class ReadEventObject:
    EventType = EventType.READ

    def __init__(self) -> None:
        self.File: IFileInfo = None
        self.Content = None

class SaveEventObject:
    EventType = EventType.SAVE

    def __init__(self) -> None:
        self.File: IFileInfo = None

class FilesEventObject:
    EventType = EventType.REPOSITORY

    def __init__(self) -> None:
        self.Files: list[IFileInfo] = None

class SetSchedulerEventObject:
    EventType = EventType.SET_SCHEDULER

    def __init__(self) -> None:
        self.NextRun: datetime = None
