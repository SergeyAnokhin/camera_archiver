import json
import mimetypes
from datetime import datetime
from typing import cast

import pytz
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_NAME
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

from ..const import (ATTR_CAMERA, ATTR_EXT, ATTR_ID, ATTR_MIMETYPE, ATTR_SIZE,
                     ATTR_SOURCE_FILE, ATTR_SOURCE_FILE_CREATED,
                     ATTR_TIMESTAMP, ATTR_TIMESTAMP_STR,
                     ATTR_TIMESTAMP_STR_UTC, EVENT_CAMERA_ARCHIVER_FILE_COPIED)
from .helper import file_mimetype, getLogger, to_str_timestamp, to_utc
from .ifile_info import IFileInfo
from .transfer_component import TransferComponentId
from .transfer_state import TransferState

mimetypes.init()

class TransferEntityContext:

    def __init__(self, config: ConfigEntry, hass: HomeAssistant):
        self._config = config
        self._hass = hass
        self._name = config[CONF_NAME]
        self.local = pytz.timezone(hass.config.time_zone)
        self._logger = getLogger(__name__, self._name)

    @callback
    def fire_post_event(self, sender: TransferComponentId, file: IFileInfo) -> None:
        dt = file.datetime # .replace(year=2031)  # TODO: remove replace
        dt = self.local.localize(dt)
        dt_utc = to_utc(dt)
        timestamp = datetime.timestamp(dt)
        timestamp_str_utc = to_str_timestamp(dt_utc)
        timestamp_str = to_str_timestamp(dt)
        modif_timestamp_str = to_str_timestamp(file.modif_datetime)

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
            ATTR_MIMETYPE: file_mimetype(file.basename),
            ATTR_SIZE: file.size,
            ATTR_ID: id,
        }

        self._logger.debug(f"Fire event: ID# {id}")
        self._logger.debug(json.dumps(entry, indent=4))
        self._hass.bus.fire(EVENT_CAMERA_ARCHIVER_FILE_COPIED, entry)
