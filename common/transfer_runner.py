import pytz
from datetime import datetime, timedelta
from typing import cast
from .ifile_info import IFileInfo
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import generate_entity_id
from .transfer_component import TransferComponent
from ..lib_directory.DirectoryTransfer import DirectoryTransfer
from ..lib_ftp.FtpTransfer import FtpTransfer
from .transfer_state import TransferState
from ..const import ATTR_CAMERA, ATTR_DESTINATION_FILE, ATTR_EXT, ATTR_ID, ATTR_LOCAL_FILE, ATTR_MODIF_DATETIME, ATTR_MODIF_DATETIME_UTC, \
            ATTR_MODIF_TIMESTAMP_STR, ATTR_MODIF_TIMESTAMP_STR_UTC, ATTR_PATH, ATTR_SIZE, CONF_DIRECTORY, CONF_FROM, CONF_FTP, CONF_LOCAL_STORAGE, \
            CONF_TO, EVENT_CAMERA_ARCHIVER_FILE_COPIED
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_NAME

class TransferRunner:

    def __init__(self, config: ConfigEntry, hass: HomeAssistant):
        self._config = config
        self._hass = hass
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
        entity_id = generate_entity_id("archiver_{}", self._config[CONF_NAME], current_ids=None, hass=self._hass)
        local_path_without_ext = f"{self._config[CONF_LOCAL_STORAGE]}/{entity_id}"

        component_from = self._from_components[0]
        return component_from.run(local_path_without_ext)

    def fire_event(self, data):
        localFile = cast(IFileInfo, data[ATTR_LOCAL_FILE])
        destFile = data[ATTR_DESTINATION_FILE]

        modif_datetime = localFile.datetime.replace(year=2031)  # TODO: remove replace
        modif_datetime_utc = self.to_utc(modif_datetime)
        modif_timestamp_str_utc = self.to_str_timestamp(modif_datetime_utc)
        modif_timestamp_str = self.to_str_timestamp(modif_datetime)

        entry = localFile.metadata | {
            ATTR_MODIF_DATETIME: modif_datetime,  # "2021-12-27T14:24:40.417330"
            ATTR_MODIF_DATETIME_UTC: modif_datetime_utc,
            ATTR_MODIF_TIMESTAMP_STR: modif_timestamp_str,
            ATTR_MODIF_TIMESTAMP_STR_UTC: modif_timestamp_str_utc,

            ATTR_CAMERA: self._config[CONF_NAME],
            ATTR_EXT: localFile.ext,
            ATTR_PATH: destFile,
            ATTR_SIZE: localFile.size,
            ATTR_ID: f"{self._config[CONF_NAME]}@{modif_timestamp_str_utc}",
        }

        # "SourceFile": "../home-assistant-core-data/input/2021Y11M30D15H/E152M00S60.mp4",
        # "SourceFileCreated": "2021-11-30T23:29:22.485693",
        # "SourceHost": "10.11.118.238",
        # "ModifDateTime": "2031-11-30T15:52:00.600000",
        # "ModifDateTimeUtc": "2031-11-30T14:52:00.600000+00:00",
        # "ModifDateTimestampStr": "2031-11-30T15:52:00.000Z",
        # "ModifDateTimestampStrUtc": "2031-11-30T14:52:00.000Z",
        # "camera": "Yi1080pWoodSouth",
        # "ext": "mp4",
        # "path": "../home-assistant-core-data/2021-11/30/Yi1080pWoodSouth_2021-11-30_15-52-00.mp4",
        # "Size": 1146320,
        # "id": "Yi1080pWoodSouth@2031-11-30T14:52:00.000Z"

        self._hass.bus.fire(EVENT_CAMERA_ARCHIVER_FILE_COPIED, entry)

    def to_utc(self, dt: datetime) -> datetime:
        local_dt = self.local.localize(dt)
        return local_dt.astimezone(pytz.utc)

    def to_str_timestamp(self, dt: datetime) -> str:
        return dt.strftime('%Y-%m-%dT%H:%M:%S.000Z')
