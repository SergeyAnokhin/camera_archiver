from abc import abstractmethod
from datetime import datetime
import logging

from voluptuous.validators import Any
from .transfer_state import TransferState
from homeassistant.config_entries import ConfigEntry
from .ifile_info import IFileInfo
from ..const import ATTR_DESTINATION_FILE, ATTR_PATH, CONF_CLEAN, CONF_COPIED_PER_RUN, CONF_DATETIME_PATTERN, CONF_EMPTY_DIRECTORIES, CONF_FILES, CONF_PATH

_LOGGER = logging.getLogger(__name__)

class TransferComponent:

    def __init__(self, config: dict) -> None:
        self._transfer_file = None
        self._config = config
        self._copied_per_run = config.get(CONF_COPIED_PER_RUN, 100)
        self._path = config.get(CONF_PATH, "")
        self.copiedFileCallback = None
        self._clean = config.get(CONF_CLEAN, {})
        self._clean_dirs = self._clean.get(CONF_EMPTY_DIRECTORIES, False)
        self._clean_files = self._clean.get(CONF_FILES, list[str])

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
        _LOGGER.debug(f"Delete: [{file.basename}] @ {file.dirname}")
        self.file_delete(file)

    def _file_save(self, file: IFileInfo, content):
        if not content:
            raise Exception('Content is empty')
        file.metadata[ATTR_DESTINATION_FILE] = self.file_save(file, content)
        _LOGGER.debug(f"Saved: [{file.metadata[ATTR_DESTINATION_FILE]}] content type: {type(content)}")
        self.copiedFileCallback(file)

    def set_source(self, from_components: list['TransferComponent']) -> None:
        for c in from_components:
            c.SetTransferFileCallback(self._file_save)

    def SetTransferFileCallback(self, callback):
        self._transfer_file = callback

    def _run(self, with_transfer=False) -> TransferState:
        action_log = "Copy" if with_transfer else "Stat"
        _LOGGER.debug(f"{action_log} from [{self._path}]: START")
        state = TransferState()

        if with_transfer:
            files = self.get_files(self._copied_per_run)
            _LOGGER.debug(f"Found files for copy: {len(files)}")
            for file in files:
                _LOGGER.debug(f"Read: [{file.fullname}]")
                content = self.file_read(file)
                self._transfer_file(file, content)
                self.file_delete(file)
                state.Copy.append(file)

        state.Read.start()
        files = self.get_files(max=100)
        state.Read.extend(files)
        state.Read.stop()
        state.Copy.stop()
        _LOGGER.debug(f"Found: {state.Read}")
        _LOGGER.debug(f"{action_log} from [{self._path}]: END, {state.Read}")
        return state

    def state(self) -> TransferState:
        return self._run(with_transfer=False)

    def run(self) -> TransferState:
        return self._run(with_transfer=True)

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
            _LOGGER.warn(f"Can't parse datetime from: '{path}' pattern: '{pattern}' Exception: {e}")
            return None
