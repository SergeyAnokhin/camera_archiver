import asyncio
from datetime import datetime
from http import HTTPStatus
import json
import pytz
from homeassistant.async_timeout_backcompat import timeout

from homeassistant.helpers.aiohttp_client import async_get_clientsession
from ..common.ifile_info import IFileInfo
from homeassistant.const import CONF_HOST, CONF_NAME, CONF_PORT
from homeassistant.core import HomeAssistant
 

from ..common.component import Component
from ..const import (ATTR_CAMERA, ATTR_EXT, ATTR_ID, ATTR_MIMETYPE, ATTR_SIZE,
                     ATTR_SOURCE_FILE, ATTR_SOURCE_FILE_CREATED,
                     ATTR_TIMESTAMP, ATTR_TIMESTAMP_STR,
                     ATTR_TIMESTAMP_STR_UTC, CONF_ELASTICSEARCH, CONF_INDEX,
                     EVENT_CAMERA_ARCHIVER_FILE_COPIED)
from ..common.helper import to_str_timestamp, to_utc
from aiohttp import hdrs
import aiohttp


class ElasticsearchComponent(Component):
    Platform = CONF_ELASTICSEARCH

    def __init__(self, hass: HomeAssistant, config: dict) -> None:
        super().__init__(hass, config)
        self.local = pytz.timezone(hass.config.time_zone)
        self._port = config.get(CONF_PORT, 9200)
        self._host = config[CONF_HOST]
        self._index = config[CONF_INDEX]

    def file_save(self, file: IFileInfo, _) -> None:
        dt = file.datetime # .replace(year=2031)  # TODO: remove replace
        dt = self.local.localize(dt)
        dt_utc = to_utc(dt)
        timestamp = datetime.timestamp(dt)
        timestamp_str_utc = to_str_timestamp(dt_utc)
        timestamp_str = to_str_timestamp(dt)
        modif_timestamp_str = to_str_timestamp(file.modif_datetime)
        id = f"{self._config[CONF_NAME]}@{timestamp_str_utc}"

        # only python native types: https://github.com/home-assistant/core/pull/41227
        # entry = file.metadata | {
        #     ATTR_TIMESTAMP: timestamp,
        #     ATTR_TIMESTAMP_STR: timestamp_str,
        #     ATTR_TIMESTAMP_STR_UTC: timestamp_str_utc,
        #     ATTR_SOURCE_FILE_CREATED: modif_timestamp_str,
        #     ATTR_SOURCE_FILE: file.fullname,
        #     ATTR_CAMERA: self._config[CONF_NAME],
        #     ATTR_EXT: file.ext,
        #     ATTR_MIMETYPE: file.mimetype,
        #     ATTR_SIZE: file.size,
        #     ATTR_ID: id,
        # }

        # TODO : add to component on each event
        # self._logger.debug(f"Fire event: ID# {id}")
        # self._logger.debug(json.dumps(entry, indent=4))
        # self._hass.bus.fire(EVENT_CAMERA_ARCHIVER_FILE_COPIED, entry)

        ftp_date = "??????????"
        source_host = "????????????"
        target_host = "???????????"
        target_component = "???????????"
        camera = "????????"
        source_component = "????? ftp directory mqtt gmail etc"
        websession = async_get_clientsession(self._hass, False)
        method = "POST"
        index = datetime.strftime(dt_utc, self._index)
        url = f"http://{self._host}:{self._port}/{index}/_doc/{id}"
        timeout = 10
        headers = {
            "accept": "application/json, text/html",
            hdrs.CONTENT_TYPE: "application/json; charset=utf-8"
        } 

        origin = {
              "pipeline_path": self.pipeline_path,
              "modif_time": modif_timestamp_str,
              "host": source_host,
              "filename": file.source_file.fullname
            }
        if ftp_date:
            origin["ftp_date"] = ftp_date
        target = {
              "component": target_component,
              "host": target_host
            }
        payload = {
            "doc": "event",
            "@timestamp": timestamp_str_utc,
            "event_start": timestamp_str,
            "camera": camera,
            "ext": file.ext,
            "mimitype": file.mimetype,
            "path": file.fullname,
            "origin": origin,
            "target": target,
            "source_type": source_component,
            "tags": "synology_cameraarchive hassio",
            "value": file.size,
            "volume": "/volume2"
        }    
        json_data = json.dumps(payload, indent=4, sort_keys=True)
        self._logger.debug(json_data)
        # print('{}@{}'.format(config.camera, file.to.get_timestamp_utc()), json_data)
        # es = Elasticsearch([{'host': 'localhost', 'port': 9200}])
        # res = es.index(index="cameraarchive-" + file.to.get_month_id_utc(),
        #                doc_type='_doc',
        #                body=json_data,
        #                id='{}@{}'.format(config.camera, file.to.get_timestamp_utc()))

        # try:
        #     with getattr(websession, method)(
        #         url,
        #         data=payload,
        #         headers=headers,
        #         timeout=timeout
        #     ) as response:

        #         if response.status < HTTPStatus.BAD_REQUEST:
        #             self._logger.debug(
        #                 "Success. Url: %s. Status code: %d. Payload: %s",
        #                 response.url,
        #                 response.status,
        #                 payload,
        #             )
        #         else:
        #             self._logger.warning(
        #                 "Error. Url: %s. Status code %d. Payload: %s",
        #                 response.url,
        #                 response.status,
        #                 payload,
        #             )

        # except asyncio.TimeoutError:
        #     self._logger.warning("Timeout call %s", url)

        # except aiohttp.ClientError:
        #     self._logger.error("Client error %s", url)

