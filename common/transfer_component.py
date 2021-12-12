from datetime import datetime
import logging
from homeassistant import config_entries
from .ifile_info import IFileInfo
from ..const import CONF_DATETIME_PATTERN, CONF_PATH

_LOGGER = logging.getLogger(__name__)

class TransferComponent:

    def __init__(self, config: config_entries) -> None:
        self._on_file_transfer = None
        self._config = config

    def set_from(self, from_components: list['TransferComponent']) -> None:
        for c in from_components:
            c.OnFileTransferSetCallback(self.from_component_download_to_local_finished_callback)

    def from_component_download_to_local_finished_callback(self, callbackObject: IFileInfo) -> None:
        print(callbackObject)

    def OnFileTransferSetCallback(self, callback):
        self._on_file_transfer = callback

    def run(self):
        pass # TO OVERRIDE

    def filename_datetime(self, file: IFileInfo):
        #p = re.compile(".*(?P<year>\d{4})Y(?P<month>\d\d)M(?P<day>\d\d)D(?P<hour>\d\d)H/E1(?P<min>\d\d)M(?P<sec>\d\d)S(?P<msec>\d\d).*")
        #m = p.match(self.fullname())
        #d = m.groupdict()
        try:
            path = file.fullname.replace(self._config[CONF_PATH], '').lstrip('\\').lstrip('/')
            pattern = self._config[CONF_DATETIME_PATTERN]
            return datetime.strptime(path, pattern)
        except Exception as e:
            _LOGGER.warn(f"❗ Can't parse datetime from: '{path}' pattern: '{pattern}' ❗ \n {e}")
