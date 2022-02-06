from abc import abstractmethod
from datetime import datetime
from typing import cast

from homeassistant.const import CONF_ID, CONF_NAME, CONF_SCAN_INTERVAL
from homeassistant.core import (CALLBACK_TYPE, HassJob, HomeAssistant,
                                ServiceCall)
from homeassistant.helpers.event import async_track_point_in_time
from voluptuous.validators import Any

from generic_observable import GenericObservable

from .. import getLogger
from ..const import (ATTR_ENABLE, ATTR_SOURCE_COMPONENT, ATTR_SOURCE_FILE,
                     ATTR_TARGET_COMPONENT, ATTR_TARGET_FILE, CONF_CLEAN,
                     CONF_COPIED_PER_RUN, CONF_DATETIME_PATTERN,
                     CONF_EMPTY_DIRECTORIES, CONF_FILES, CONF_PATH, DOMAIN,
                     SERVICE_FIELD_COMPONENT, SERVICE_FIELD_INSTANCE,
                     SERVICE_RUN)
from .event_objects import (FileEventObject, FilesEventObject, ReadEventObject,
                            RepositoryEventObject, SaveEventObject,
                            SetSchedulerEventObject, StartEventObject)
from .ifile_info import IFileInfo
from .transfer_state import EventType


class Component(GenericObservable):
    Platform: str = None

    def __init__(self, hass: HomeAssistant, config: dict) -> None:
        self._hass = hass
        self.id = config[CONF_ID]
        self.pipeline_path = None
        self._logger = getLogger(__name__, self._id)
        self._transfer_file = None
        self._config = config
        self._copied_per_run = config.get(CONF_COPIED_PER_RUN, 100)
        self._path = config.get(CONF_PATH, "")
        self._clean = config.get(CONF_CLEAN, {})
        self._clean_dirs = self._clean.get(CONF_EMPTY_DIRECTORIES, False)
        self._clean_files = self._clean.get(CONF_FILES, list[str])
        self._is_enabled: bool = True

    @abstractmethod
    def file_read(self, file: IFileInfo) -> Any:
        NotImplementedError()

    @abstractmethod
    def file_delete(self, file: IFileInfo) -> Any:
        NotImplementedError()

    @abstractmethod
    def get_files(self) -> list[IFileInfo]:
        NotImplementedError()

    @abstractmethod
    def file_save(self, file: IFileInfo, content) -> IFileInfo:
        NotImplementedError()

    @property
    def Id(self):
        return self.id

    def _file_delete(self, file: IFileInfo):
        self._logger.debug(f"Delete: [{file.basename}] @ {file.dirname}")
        self.file_delete(file)

    def callback(self, eventObj) -> bool:
        if isinstance(eventObj, StartEventObject):
            self._run()
        elif isinstance(eventObj, FileEventObject):
            readEO = cast(FileEventObject, eventObj)
            if not readEO.Content:
                raise Exception(f'Content is empty. Components: {readEO.sender.id} -> {self.id}. Pipeline path: {self.pipeline_path}')
            file = readEO.File
            new_file = self.file_save(file, readEO.Content)
            new_file.source_file = file
            self._logger.debug(f"Saved: [{file.metadata[ATTR_TARGET_FILE]}] content type: {type(readEO.Content)}")
            self._invoke_file_listeners(file)
            return True # need ack for file delete permission

    def enabled_change(self, is_enabled: bool) -> None:
        if self._is_enabled == is_enabled:
            return
        self.enabled_changed()
        
    @abstractmethod
    def enabled_changed(self):
        pass

    def _invoke_file_listeners(self, file: IFileInfo, content) -> bool:
        eventObj = FileEventObject(self)
        eventObj.File = file
        eventObj.Content = content
        return self.invoke_listeners(eventObj)

    def _invoke_repo_listeners(self, files: list[IFileInfo]) -> None:
        eventObj = RepositoryEventObject(self)
        eventObj.Files = files
        self.invoke_listeners(eventObj)

    def _run(self):
        self._logger.debug(f"Read from [{self._path}]: START")
        if not self._is_enabled[EventType.REPOSITORY]:
            return

        if self._is_enabled[EventType.READ]:
            files: list[IFileInfo] = self.get_files(self._copied_per_run)
            self._logger.debug(f"Found files for copy: {len(files)}")
            for file in files:
                self._logger.debug(f"Read: [{file.fullname}]")
                file.add_processing_path(self.id)
                content = self.file_read(file)
                file.metadata[ATTR_SOURCE_COMPONENT] = self._id.Name
                if self._invoke_file_listeners(file, content):
                    self.file_delete(file)

        files = self.get_files(max=100)
        self._invoke_repo_listeners(files)
        self._logger.debug(f"Read from [{self._path}]: END")

    def run(self, args):
        ''' External call force start '''
        return self._run()

    def validate_file(self, file: IFileInfo) -> bool:
        dt = self.filename_datetime(file)
        if dt == None:
            return False  # ignore file
        file.datetime = dt
        return True

    def filename_datetime(self, file: IFileInfo):
        #p = re.compile(".*(?P<year>\d{4})Y(?P<month>\d\d)M(?P<day>\d\d)D(?P<hour>\d\d)H/E1(?P<min>\d\d)M(?P<sec>\d\d)S(?P<msec>\d\d).*")
        #m = p.match(self.fullname())
        #d = m.groupdict()
        try:
            path = file.fullnameWithoutExt.replace(self._path, '').lstrip('\\').lstrip('/')
            pattern = self._config[CONF_DATETIME_PATTERN]
            return datetime.strptime(path, pattern)
        except Exception as e:
            self._logger.warn(f"Can't parse datetime from: '{path}' pattern: '{pattern}' Exception: {e}")
            return None
