import json
import mimetypes
from datetime import datetime
from typing import cast

import pytz
from config.custom_components.camera_archiver.common.transfer_component import TransferComponentId
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_NAME
from homeassistant.core import HomeAssistant, callback

from ..const import (ATTR_CAMERA, ATTR_EXT, ATTR_ID, ATTR_MIMETYPE, ATTR_SIZE,
                     ATTR_SOURCE_FILE, ATTR_SOURCE_FILE_CREATED,
                     ATTR_TIMESTAMP, ATTR_TIMESTAMP_STR,
                     ATTR_TIMESTAMP_STR_UTC,
                     EVENT_CAMERA_ARCHIVER_FILE_COPIED)
from .helper import getLogger
from .ifile_info import IFileInfo

mimetypes.init()

class TransferRunner:

    def __init__(self, config: ConfigEntry, hass: HomeAssistant):
        self._config = config
        self._hass = hass
        self._name = config[CONF_NAME]
        self.local = pytz.timezone(hass.config.time_zone)
        self._logger = getLogger(__name__, self._name)

    @callback
    def fire_post_event(self, sender: TransferComponentId, file: IFileInfo):
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

        self._logger.debug(f"Fire event: ID# {id}")
        self._logger.debug(json.dumps(entry, indent=4))
        self._hass.bus.fire(EVENT_CAMERA_ARCHIVER_FILE_COPIED, entry)

    def to_utc(self, dt: datetime) -> datetime:
        #local_dt = self.local.localize(dt)
        return dt.astimezone(pytz.utc)

    def to_str_timestamp(self, dt: datetime) -> str:
        return dt.strftime('%Y-%m-%dT%H:%M:%S.000Z')
