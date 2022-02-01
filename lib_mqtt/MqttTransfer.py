import io
import queue
import threading
from datetime import datetime
from typing import Any

from homeassistant.components import mqtt
from homeassistant.components.mqtt.const import CONF_BROKER
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.util.async_ import fire_coroutine_threadsafe

from ..common.helper import local_ip
from ..common.ifile_info import IFileInfo
from ..common.component import Component, TransferComponentId
from ..common.transfer_state import TransferState
from ..const import ATTR_SOURCE_HOST, CONF_MQTT, CONF_TOPIC
from .mqtt_file_info import MqttFileInfo

lock = threading.Lock()

class MqttTransfer(Component):
    Platform = CONF_MQTT

    def __init__(self, hass: HomeAssistant, config: ConfigEntry):
        super().__init__(hass, config)
        #self._state_topic = config.data[CONF_MQTT_PREFIX] + "/" + config.data[CONF_TOPIC_MOTION_DETECTION_IMAGE]
        self._state_topic = config[CONF_TOPIC]
        self._path = self._state_topic
        self._mqtt_subscription = None
        self._last_image = None
        self._last_updated = None
        self._hass = hass
        self._broker = ""
        if CONF_MQTT in self._hass.data:
            self._broker = self._hass.data[CONF_MQTT].conf[CONF_BROKER]
        self._files: queue.Queue = queue.Queue()
        self._retained_message = True # ignore first message after initialisation
        fire_coroutine_threadsafe(self.subscribe_to_mqtt(), hass.loop)

    @callback
    def message_received(self, msg):
        """Handle new MQTT messages."""
        self._logger.debug(f"|{self._state_topic}| MQTT message received")
        data = msg.payload
        self._last_updated = datetime.now()
        self._last_image = data
        filename = f"{self._state_topic}/mqtt.jpg"
        file = MqttFileInfo(filename, data)
        file.metadata[ATTR_SOURCE_HOST] = self._broker
        self._files.put(file)
        if self._retained_message: # ignore first message after loading
            self._retained_message = False
        else:
            try:
                self._run()
            except Exception as ex:
                self._logger.exception(ex)

    async def subscribe_to_mqtt(self):
        self._subscription = await mqtt.async_subscribe(
            self._hass, self._state_topic, self.message_received, 0, None
        )
        return

    def _schedule_refresh(self):
        ''' OVERRIDE '''
        pass # not needed for mqtt

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
        file.metadata[ATTR_SOURCE_HOST] = local_ip()
        return self._last_image

    def file_delete(self, file: IFileInfo):
        ''' OVERRIDE '''
        pass

    def file_save(self, file: IFileInfo, content) -> str:
        ''' OVERRIDE '''
        return ""

