import pytz, mimetypes, logging
from datetime import datetime, timedelta
from typing import cast
from .ifile_info import IFileInfo
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import generate_entity_id
from .transfer_component import TransferComponent
from ..lib_directory.DirectoryTransfer import DirectoryTransfer
from ..lib_ftp.FtpTransfer import FtpTransfer
from .transfer_state import TransferState
from ..const import ATTR_CAMERA, ATTR_EXT, ATTR_ID, ATTR_MIMETYPE, \
            ATTR_SIZE, ATTR_SOURCE_FILE, ATTR_SOURCE_FILE_CREATED, ATTR_TIMESTAMP, ATTR_TIMESTAMP_STR, ATTR_TIMESTAMP_STR_UTC, CONF_DIRECTORY, CONF_FROM, CONF_FTP, \
            CONF_TO, EVENT_CAMERA_ARCHIVER_FILE_COPIED
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_NAME

mimetypes.init()
_LOGGER = logging.getLogger(__name__)

class TransferRunner:

    def __init__(self, config: ConfigEntry, hass: HomeAssistant):
        self._config = config
        self._hass = hass
        self._name = config[CONF_NAME]
        self.local = pytz.timezone(hass.config.time_zone)
        self._from_components: list[TransferComponent] = []
        self._to_components: list[TransferComponent] = []

        cfrom = config[CONF_FROM]
        if CONF_DIRECTORY in cfrom:
            transfer = DirectoryTransfer(cfrom[CONF_DIRECTORY])
            self._from_components.append(transfer)
        if CONF_FTP in cfrom:
            transfer = FtpTransfer(cfrom[CONF_FTP])
            self._from_components.append(transfer)

        tfrom = config[CONF_TO]
        if CONF_DIRECTORY in tfrom:
            transfer = DirectoryTransfer(tfrom[CONF_DIRECTORY])
            transfer.set_from(self._from_components)
            self._to_components.append(transfer)
        if CONF_FTP in tfrom:
            transfer = FtpTransfer(tfrom[CONF_FTP])
            transfer.set_from(self._from_components)
            self._to_components.append(transfer)

        for c in self._to_components:
            c.copiedFileCallback = self.fire_event

    def stat(self) -> TransferState:
        component_from = self._from_components[0]
        return component_from.state()

    def run(self) -> TransferState:
        # entity_id = generate_entity_id("archiver_{}", self._config[CONF_NAME], current_ids=None, hass=self._hass)
        component_from = self._from_components[0]
        return component_from.run()

    def fire_event(self, file: IFileInfo):
        dt = file.datetime # .replace(year=2031)  # TODO: remove replace
        dt = self.local.localize(dt)
        dt_utc = self.to_utc(dt)
        timestamp = datetime.timestamp(dt)
        timestamp_str_utc = self.to_str_timestamp(dt_utc)
        timestamp_str = self.to_str_timestamp(dt)
        modif_timestamp_str = self.to_str_timestamp(file.modif_datetime)

        mimestart = mimetypes.guess_type(file.basename)[0] or "unknown/ext"
        mimestart = mimestart.split('/')[0]
        id = f"{self._config[CONF_NAME]}@{timestamp_str_utc}"

        # only python native types: https://github.com/home-assistant/core/pull/41227
        entry = file.metadata | {
            ATTR_TIMESTAMP: timestamp,
            ATTR_TIMESTAMP_STR: timestamp_str,
            ATTR_TIMESTAMP_STR_UTC: timestamp_str_utc,
            ATTR_SOURCE_FILE_CREATED: modif_timestamp_str,
            ATTR_SOURCE_FILE: file.fullname,
            ATTR_CAMERA: self._config[CONF_NAME],
            ATTR_EXT: file.ext,
            ATTR_MIMETYPE: mimestart,
            ATTR_SIZE: file.size,
            ATTR_ID: id,
        }

        _LOGGER.debug(f"|{self._name}| Fire event: ID# {id}")
        self._hass.bus.fire(EVENT_CAMERA_ARCHIVER_FILE_COPIED, entry)

    def to_utc(self, dt: datetime) -> datetime:
        #local_dt = self.local.localize(dt)
        return dt.astimezone(pytz.utc)

    def to_str_timestamp(self, dt: datetime) -> str:
        return dt.strftime('%Y-%m-%dT%H:%M:%S.000Z')
