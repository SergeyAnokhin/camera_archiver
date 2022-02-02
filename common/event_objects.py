from datetime import datetime
from .ifile_info import IFileInfo
from .transfer_state import EventType

class EventObject:
    EventType = None 
    Sender = None   

class ReadEventObject(EventObject):
    EventType = EventType.READ

    def __init__(self) -> None:
        self.File: IFileInfo = None
        self.Content = None

class SaveEventObject(EventObject):
    EventType = EventType.SAVE

    def __init__(self) -> None:
        self.File: IFileInfo = None

class FilesEventObject(EventObject):
    EventType = EventType.REPOSITORY

    def __init__(self) -> None:
        self.Files: list[IFileInfo] = None

class SetSchedulerEventObject(EventObject):
    EventType = EventType.SET_SCHEDULER

    def __init__(self) -> None:
        self.NextRun: datetime = None
