from abc import abstractmethod
from datetime import datetime

from homeassistant.const import CONF_NAME, CONF_SCAN_INTERVAL
from homeassistant.core import (CALLBACK_TYPE, HassJob, HomeAssistant,
                                ServiceCall)
from homeassistant.helpers.event import async_track_point_in_time
from voluptuous.validators import Any

from .. import getLogger
from ..const import (ATTR_DESTINATION_FILE, ATTR_DESTINATION_PLATFORM,
                     ATTR_SOURCE_PLATFORM, CONF_CLEAN, CONF_COPIED_PER_RUN,
                     CONF_DATETIME_PATTERN, CONF_EMPTY_DIRECTORIES, CONF_FILES,
                     CONF_PATH, DOMAIN, SERVICE_FIELD_COMPONENT,
                     SERVICE_FIELD_INSTANCE, SERVICE_RUN)
from .ifile_info import IFileInfo
from .transfer_state import StateType


class TransferComponent:
    platform: str = None

    def __init__(self, instName: str, hass: HomeAssistant, config: dict) -> None:
        self._hass = hass
        self._instName = instName
        self._name = config.get(CONF_NAME, self.platform)
        self._logger = getLogger(__name__, instName, self._name)
        self._transfer_file = None
        self._config = config
        self._copied_per_run = config.get(CONF_COPIED_PER_RUN, 100)
        self._path = config.get(CONF_PATH, "")
        self._clean = config.get(CONF_CLEAN, {})
        self._clean_dirs = self._clean.get(CONF_EMPTY_DIRECTORIES, False)
        self._clean_files = self._clean.get(CONF_FILES, list[str])

        self._listeners = {t: [] for t in StateType}

        self._job = HassJob(self.run)
        self._unsub_refresh: CALLBACK_TYPE = None
        self._schedule_refresh()

        self.subscribe_to_service()

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

    def _file_delete(self, file: IFileInfo):
        self._logger.debug(f"Delete: [{file.basename}] @ {file.dirname}")
        self.file_delete(file)

    def _new_file_readed(self, file: IFileInfo, content):
        if not content:
            raise Exception('Content is empty')
        file.metadata[ATTR_DESTINATION_FILE] = self.file_save(file, content)
        file.metadata[ATTR_DESTINATION_PLATFORM] = self.platform
        self._logger.debug(f"Saved: [{file.metadata[ATTR_DESTINATION_FILE]}] content type: {type(content)}")
        self._invoke_save_listeners(file)

    def subscribe_to_service(self) -> None:
        async def _service_run(call: ServiceCall) -> None:
            self._logger.info("service camera archive call")
            data = dict(call.data)
            if self._instName != data[SERVICE_FIELD_INSTANCE]:
                return
            if self._name != data[SERVICE_FIELD_COMPONENT]:
                return
            self.run()

        self._hass.services.async_register(DOMAIN, SERVICE_RUN, _service_run)


    def _schedule_refresh(self):
        if CONF_SCAN_INTERVAL not in self._config:
            return 

        scan_interval = self._config[CONF_SCAN_INTERVAL]
        if self._unsub_refresh:
            self._unsub_refresh()
            self._unsub_refresh = None

        self._unsub_refresh = async_track_point_in_time(
            self._hass,
            self._job,
            datetime.now().replace(microsecond=0) + scan_interval,
        )        

    def add_listener(self, stateType: StateType, update_callback: CALLBACK_TYPE) -> None:
        """Listen for data updates."""
        self._listeners[stateType].append(update_callback)

    def _invoke_read_listeners(self, file: IFileInfo, content) -> None:
        for callback in self._listeners[StateType.READ]:
            callback(file, content)

    def _invoke_repo_listeners(self, files: list[IFileInfo]) -> None:
        for callback in self._listeners[StateType.REPOSITORY]:
            callback(files)

    def _invoke_save_listeners(self, file: IFileInfo) -> None:
        for callback in self._listeners[StateType.SAVE]:
            callback(file)

    def _run(self):
        self._logger.debug(f"Read from [{self._path}]: START")

        files: list[IFileInfo] = self.get_files(self._copied_per_run)
        self._logger.debug(f"Found files for copy: {len(files)}")
        for file in files:
            self._logger.debug(f"Read: [{file.fullname}]")
            content = self.file_read(file)
            file.metadata[ATTR_SOURCE_PLATFORM] = self.platform
            self._invoke_read_listeners(file, content)
            self.file_delete(file)

        files = self.get_files(max=100)
        self._invoke_repo_listeners(files)
        self._logger.debug(f"Read from [{self._path}]: END")
        self._schedule_refresh()

    def run(self, args):
        ''' External call force start '''
        return self._run()

    def validate_file(self, file: IFileInfo) -> bool:
        dt = self.filename_datetime(file)
        if dt == None:
            return False # ignore file
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
