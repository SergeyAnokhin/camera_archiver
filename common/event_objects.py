from datetime import datetime

from sqlalchemy import false

from .ifile_info import IFileInfo
from .transfer_state import EventType

class EventObject:
    EventType = None 

    def __init__(self, sender) -> None:
        self.sender = sender

class FileEventObject(EventObject):
    EventType = EventType.FILE

    def __init__(self, sender) -> None:
        super().__init__(sender)
        self.File: IFileInfo = None
        self.Content = None

class RepositoryEventObject(EventObject):
    EventType = EventType.REPOSITORY

    def __init__(self, sender) -> None:
        super().__init__(sender)
        self.Files: list[IFileInfo] = None

class StartEventObject(EventObject):
    EventType = EventType.START

    def __init__(self, sender) -> None:
        super().__init__(sender)
        self.start_time = datetime.now()

class SetSchedulerEventObject(EventObject):
    EventType = EventType.SET_SCHEDULER

    def __init__(self, sender) -> None:
        super().__init__(sender)
        self.NextRun: datetime = None

class SwitchEventObject(EventObject):
    EventType = EventType.SWITCH

    def __init__(self, sender) -> None:
        super().__init__(sender)
        self.enable: bool = false
