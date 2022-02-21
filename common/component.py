from abc import abstractmethod
from datetime import datetime
from typing import cast

from homeassistant.const import CONF_ID
from homeassistant.core import HomeAssistant
from voluptuous.validators import Any

from ..const import (ATTR_SOURCE_COMPONENT, ATTR_TARGET_FILE, CONF_CLEAN,
                     CONF_COPIED_PER_RUN, CONF_DATA, CONF_DATETIME_PATTERN,
                     CONF_EMPTY_DIRECTORIES, CONF_FILES, CONF_PATH)
from .event_objects import (FileEventObject, RepositoryEventObject,
                            StartEventObject, SwitchEventObject)
from .generic_observable import GenericObservable
from .helper import getLogger
from .ifile_info import IFileInfo
from .transfer_state import EventType


class Component(GenericObservable):
    Platform: str = None

    def __init__(self, hass: HomeAssistant, config: dict) -> None:
        super().__init__()
        self._hass = hass
        self.id = config[CONF_ID]
        self.pipeline_path: str = None
        self.pipeline_id: str = None
        self.parent: Component = None
        self._logger = getLogger(__name__, self.id)
        self._transfer_file = None
        self._config = config
        self._data: list = config.get(CONF_DATA, [])
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
    def get_files(self, max: int) -> list[IFileInfo]:
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
        if isinstance(eventObj, SwitchEventObject):
            switchEO = cast(SwitchEventObject, eventObj)
            self.enabled_change(switchEO.enable)
        elif isinstance(eventObj, FileEventObject):
            readEO = cast(FileEventObject, eventObj)
            file = readEO.File
            new_file = self.file_save(file, readEO.Content)
            new_file.source_file = file
            self._logger.debug(f"Saved: [{new_file}] content type: {type(readEO.Content)}")
            self._invoke_file_listeners(new_file, None)
            return True # need ack for file delete permission

    def enabled_change(self, is_enabled: bool) -> None:
        if self._is_enabled == is_enabled:
            return
        self._is_enabled = is_enabled
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
        if not self._is_enabled:
            return

        files: list[IFileInfo] = self.get_files(max=100)
        self._invoke_repo_listeners(files)
        self._logger.debug(f"Found files: {len(files)}")
        files_to_read = min(len(files), self._copied_per_run)
        files = files[0:files_to_read]
        for file in files:
            self._logger.debug(f"Read: [{file.fullname}]")
            file.add_processing_path(self.id)
            content = self.file_read(file)
            file.metadata[ATTR_SOURCE_COMPONENT] = self.id
            if self._invoke_file_listeners(file, content):
                self.file_delete(file)

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
