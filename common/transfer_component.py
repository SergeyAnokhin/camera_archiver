from abc import abstractmethod
from datetime import datetime
from enum import Enum

from homeassistant.const import CONF_NAME, CONF_SCAN_INTERVAL
from homeassistant.core import (CALLBACK_TYPE, HassJob, HomeAssistant,
                                ServiceCall)
from homeassistant.helpers.event import async_track_point_in_time
from voluptuous.validators import Any

from .. import getLogger
from ..const import (ATTR_DESTINATION_FILE, ATTR_DESTINATION_PLATFORM,
                     ATTR_SOURCE_PLATFORM, CONF_CLEAN, CONF_COPIED_PER_RUN,
                     CONF_DATETIME_PATTERN, CONF_EMPTY_DIRECTORIES, ATTR_ENABLE, CONF_FILES,
                     CONF_FROM, CONF_PATH, CONF_TO, DEFAULT_TIME_INTERVAL,
                     DOMAIN, SERVICE_FIELD_COMPONENT, SERVICE_FIELD_DIRECTION,
                     SERVICE_FIELD_INSTANCE, SERVICE_RUN)
from .ifile_info import IFileInfo
from .transfer_component_id import TransferComponentId, TransferType
from .transfer_state import StateType


class TransferComponent:
    platform: str = None

    def __init__(self, id: TransferComponentId, hass: HomeAssistant, config: dict) -> None:
        self._hass = hass
        self._id = id
        if not self._id.Name:
            self._id.Name = config.get(CONF_NAME, self.platform)
        self._logger = getLogger(__name__, self._id.id)
        self._transfer_file = None
        self._config = config
        self._copied_per_run = config.get(CONF_COPIED_PER_RUN, 100)
        self._path = config.get(CONF_PATH, "")
        self._clean = config.get(CONF_CLEAN, {})
        self._clean_dirs = self._clean.get(CONF_EMPTY_DIRECTORIES, False)
        self._clean_files = self._clean.get(CONF_FILES, list[str])
        self._is_enabled: dict[StateType] = {t: True for t in StateType}

        self._listeners = {t: [] for t in StateType}

        self._job = HassJob(self.async_run)
        self._unsub_refresh: CALLBACK_TYPE = None
        if self._id.TransferType == TransferType.FROM:
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

    @property
    def Id(self):
        return self._id

    def _file_delete(self, file: IFileInfo):
        self._logger.debug(f"Delete: [{file.basename}] @ {file.dirname}")
        self.file_delete(file)

    def _new_file_readed(self, comp_id: TransferComponentId, file: IFileInfo, content) -> bool:
        if not self._is_enabled[StateType.SAVE]:
            return False
        if not content:
            raise Exception(f'Content is empty. Components: {self._id} -> {comp_id}')
        file.metadata[ATTR_DESTINATION_FILE] = self.file_save(file, content)
        file.metadata[ATTR_DESTINATION_PLATFORM] = self.platform
        self._logger.debug(f"Saved: [{file.metadata[ATTR_DESTINATION_FILE]}] content type: {type(content)}")
        self._invoke_save_listeners(file)
        return True # need ack for file delete permission

    def settings_changed(self, stateType: StateType, data) -> None:
        if self._is_enabled[stateType] == data[ATTR_ENABLE]:
            return
        self._is_enabled[stateType] = data[ATTR_ENABLE]
        if stateType == StateType.REPOSITORY:
            self._schedule_refresh()

    def subscribe_to_service(self) -> None:
        async def _service_run(call: ServiceCall) -> None:
            self._logger.info("service camera archive call")
            data = dict(call.data)
            if self._id.Entity != data[SERVICE_FIELD_INSTANCE]:
                return
            if self._id.Name != data[SERVICE_FIELD_COMPONENT]:
                return
            if self._id.TransferType != TransferType.FROM:
                return
            self.run()

        self._hass.services.async_register(DOMAIN, SERVICE_RUN, _service_run)

    def _schedule_off(self):
        if self._unsub_refresh:
            self._unsub_refresh()
            self._unsub_refresh = None

    def _schedule_refresh(self):
        self._schedule_off()
        if CONF_SCAN_INTERVAL not in self._config \
            or not self._is_enabled[StateType.REPOSITORY]:
            return

        scan_interval = self._config.get(CONF_SCAN_INTERVAL, DEFAULT_TIME_INTERVAL)
        self._unsub_refresh = async_track_point_in_time(
            self._hass,
            self._job,
            datetime.now().replace(microsecond=0) + scan_interval,
        )

    def add_listener(self, stateType: StateType, update_callback: CALLBACK_TYPE) -> None:
        """Listen for data updates."""
        self._listeners[stateType].append(update_callback)

    def _invoke_read_listeners(self, file: IFileInfo, content) -> bool:
        results: list = []
        for callback in self._listeners[StateType.READ]:
            results.append(callback(self._id, file, content))

        return True in results # check if any compinent recieved and saved file

    def _invoke_repo_listeners(self, files: list[IFileInfo]) -> None:
        for callback in self._listeners[StateType.REPOSITORY]:
            callback(self._id, files)

    def _invoke_save_listeners(self, file: IFileInfo) -> None:
        for callback in self._listeners[StateType.SAVE]:
            callback(self._id, file)

    def _run(self):
        self._logger.debug(f"Read from [{self._path}]: START")
        if not self._is_enabled[StateType.REPOSITORY]:
            return

        if self._is_enabled[StateType.READ]:
            files: list[IFileInfo] = self.get_files(self._copied_per_run)
            self._logger.debug(f"Found files for copy: {len(files)}")
            for file in files:
                self._logger.debug(f"Read: [{file.fullname}]")
                content = self.file_read(file)
                file.metadata[ATTR_SOURCE_PLATFORM] = self.platform
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
