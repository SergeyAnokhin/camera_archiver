from datetime import datetime
import logging
import queue
import io
import threading
import socket
from typing import Any

from ..common.transfer_state import TransferState
from .mqtt_file_info import MqttFileInfo
from homeassistant.util.async_ import fire_coroutine_threadsafe
from ..const import ATTR_SOURCE_HOST, ATTR_SOURCE_TYPE, CONF_MQTT, CONF_TOPIC
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.components import mqtt
from ..common.ifile_info import IFileInfo
from ..common.transfer_component import TransferComponent

_LOGGER = logging.getLogger(__name__)
lock = threading.Lock()

class MqttTransfer(TransferComponent):
    name = CONF_MQTT

    def __init__(self, instName: str, hass: HomeAssistant, config: ConfigEntry):
        super().__init__(instName, hass, config)
        #self._state_topic = config.data[CONF_MQTT_PREFIX] + "/" + config.data[CONF_TOPIC_MOTION_DETECTION_IMAGE]
        self._state_topic = config[CONF_TOPIC]
        self._mqtt_subscription = None
        self._last_image = None
        self._last_updated = None
        self._hass = hass
        self._files: queue.Queue = queue.Queue()
        fire_coroutine_threadsafe(self.subscribe_to_mqtt(), hass.loop)

    @callback
    def message_received(self, msg):
        """Handle new MQTT messages."""
        _LOGGER.debug(f"|{self._state_topic}| MQTT : {msg.topic}")
        data = msg.payload
        self._last_updated = datetime.now()
        self._last_image = data
        file = MqttFileInfo(data)
        self._files.put(file)
        # REACTIVATE! self._run(with_transfer=True)

    async def subscribe_to_mqtt(self):
        self._subscription = await mqtt.async_subscribe(
            self._hass, self._state_topic, self.message_received, 0, None
        )
        return

    def run(self) -> TransferState:
        ''' OVERRIDE '''
        pass # nothinf to do if in case of external call. 

    def get_files(self, max=None) -> list[IFileInfo]:
        ''' OVERRIDE '''
        with lock:
            result = []
            while self._files.qsize() > 0:
                result.append(self._files.get())
        return result

    def file_read(self, file: IFileInfo) -> Any:
        ''' OVERRIDE '''
        hostname = socket.gethostname()
        local_ip = socket.gethostbyname(hostname)
        self._file.metadata[ATTR_SOURCE_HOST] = local_ip
        self._file.metadata[ATTR_SOURCE_TYPE] = "mqtt"
        return io.BytesIO(self._last_image)

    def file_delete(self, file: IFileInfo):
        ''' OVERRIDE '''
        pass

    def file_save(self, file: IFileInfo, content) -> str:
        ''' OVERRIDE '''
        return ""

