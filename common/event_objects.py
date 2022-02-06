from datetime import datetime

from config.custom_components.camera_archiver.common.generic_observable import GenericObservable
from .ifile_info import IFileInfo
from .transfer_state import EventType

class EventObject:
    EventType = None 

    def __init__(self, sender: GenericObservable) -> None:
        self.sender = sender

class FileEventObject(EventObject):
    EventType = EventType.FILE

    def __init__(self, sender) -> None:
        super().__init__()
        self.File: IFileInfo = None
        self.Content = None

class RepositoryEventObject(EventObject):
    EventType = EventType.REPOSITORY

    def __init__(self, sender) -> None:
        self.Files: list[IFileInfo] = None

class StartEventObject(EventObject):
    EventType = EventType.START

    def __init__(self, sender) -> None:
        self.start_time = datetime.now()

class SetSchedulerEventObject(EventObject):
    EventType = EventType.SET_SCHEDULER

    def __init__(self, sender) -> None:
        self.NextRun: datetime = None
