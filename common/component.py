from abc import abstractmethod
from datetime import datetime, timedelta
from enum import Enum
from .event_objects import FilesEventObject, ReadEventObject, SaveEventObject, SetSchedulerEventObject
from generic_listener import GenericListener

from homeassistant.const import CONF_ID, CONF_NAME, CONF_SCAN_INTERVAL
from homeassistant.core import (CALLBACK_TYPE, HassJob, HomeAssistant,
                                ServiceCall)
from homeassistant.helpers.event import async_track_point_in_time
from voluptuous.validators import Any

from .. import getLogger
from ..const import (ATTR_ENABLE, ATTR_SOURCE_COMPONENT, ATTR_TARGET_COMPONENT, ATTR_TARGET_FILE, CONF_CLEAN,
                     CONF_COPIED_PER_RUN, CONF_DATETIME_PATTERN,
                     CONF_EMPTY_DIRECTORIES, CONF_FILES, CONF_PATH,
                     DOMAIN, SERVICE_FIELD_COMPONENT,
                     SERVICE_FIELD_INSTANCE, SERVICE_RUN)
from .ifile_info import IFileInfo
from .transfer_state import EventType


class Component(GenericListener):
    platform: str = None

    def __init__(self, hass: HomeAssistant, config: dict) -> None:
        self._hass = hass
        self._id = config[CONF_ID]
        self._logger = getLogger(__name__, self._id)
        self._transfer_file = None
        self._config = config
        self._copied_per_run = config.get(CONF_COPIED_PER_RUN, 100)
        self._path = config.get(CONF_PATH, "")
        self._clean = config.get(CONF_CLEAN, {})
        self._clean_dirs = self._clean.get(CONF_EMPTY_DIRECTORIES, False)
        self._clean_files = self._clean.get(CONF_FILES, list[str])
        self._is_enabled: bool = True

        self._job = HassJob(self.async_run)
        # if self._id.TransferType == TransferType.FROM:
        #     self._schedule_refresh()
        #     self.subscribe_to_service()

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
    def file_save(self, file: IFileInfo, content):
        NotImplementedError()

    @property
    def Id(self):
        return self._id

    def _file_delete(self, file: IFileInfo):
        self._logger.debug(f"Delete: [{file.basename}] @ {file.dirname}")
        self.file_delete(file)

    def _new_file_readed(self, file: IFileInfo, content) -> bool:
        if not self._is_enabled[EventType.SAVE]:
            return False
        if not content:
            raise Exception(f'Content is empty. Components: {self._id} -> {comp_id}')
        file.metadata[ATTR_TARGET_FILE] = self.file_save(file, content)
        file.metadata[ATTR_TARGET_COMPONENT] = self._id.Name
        self._logger.debug(f"Saved: [{file.metadata[ATTR_TARGET_FILE]}] content type: {type(content)}")
        self._invoke_save_listeners(file)
        return True # need ack for file delete permission

    def enabled_change(self, is_enabled: bool) -> None:
        if self._is_enabled == is_enabled:
            return
        self.enabled_changed()
        
    @abstractmethod
    def enabled_changed(self):
        pass

    def add_listener(self, stateType: EventType, update_callback: CALLBACK_TYPE) -> None:
        """Listen for data updates."""
        self.add_listener(update_callback)

    def _invoke_read_listeners(self, file: IFileInfo, content) -> bool:
        eventObj = ReadEventObject()
        eventObj.File = file
        eventObj.Content = content
        return self.invoke_listeners(eventObj)

    def _invoke_repo_listeners(self, files: list[IFileInfo]) -> None:
        eventObj = FilesEventObject()
        eventObj.Files = files
        self.invoke_listeners(eventObj)

    def _invoke_save_listeners(self, file: IFileInfo) -> None:
        eventObj = SaveEventObject()
        eventObj.File = file
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
                content = self.file_read(file)
                file.metadata[ATTR_SOURCE_COMPONENT] = self._id.Name
                if self._invoke_read_listeners(file, content):
                    self.file_delete(file)

        files = self.get_files(max=100)
        self._invoke_repo_listeners(files)
        self._logger.debug(f"Read from [{self._path}]: END")
        self._schedule_refresh()

    async def async_run(self, args):
        ''' External call force start '''
        return self._run()

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