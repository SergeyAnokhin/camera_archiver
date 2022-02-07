from datetime import datetime
import json
import pytz
from ..common.ifile_info import IFileInfo
from homeassistant.const import CONF_NAME
from homeassistant.core import HomeAssistant, callback

from ..common.component import Component
from ..const import (ATTR_CAMERA, ATTR_EXT, ATTR_ID, ATTR_MIMETYPE, ATTR_SIZE,
                     ATTR_SOURCE_FILE, ATTR_SOURCE_FILE_CREATED,
                     ATTR_TIMESTAMP, ATTR_TIMESTAMP_STR,
                     ATTR_TIMESTAMP_STR_UTC, CONF_ELASTICSEARCH,
                     EVENT_CAMERA_ARCHIVER_FILE_COPIED)
from ..common.helper import to_str_timestamp, to_utc

class ElasticsearchComponent(Component):
    Platform = CONF_ELASTICSEARCH

    def __init__(self, hass: HomeAssistant, config: dict) -> None:
        super().__init__(hass, config)
        self.local = pytz.timezone(hass.config.time_zone)

    @callback
    def fire_post_event(self, file: IFileInfo) -> None:
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
            ATTR_MIMETYPE: file.mimetype,
            ATTR_SIZE: file.size,
            ATTR_ID: id,
        }

        self._logger.debug(f"Fire event: ID# {id}")
        self._logger.debug(json.dumps(entry, indent=4))
        self._hass.bus.fire(EVENT_CAMERA_ARCHIVER_FILE_COPIED, entry)
