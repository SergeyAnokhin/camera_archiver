from datetime import datetime
import logging, queue, io,threading
from typing import Any
from .mqtt_file_info import MqttFileInfo
from homeassistant.util.async_ import fire_coroutine_threadsafe
from ..const import CONF_TOPIC
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.components import mqtt
from ..common.ifile_info import IFileInfo
from ..common.transfer_component import TransferComponent

_LOGGER = logging.getLogger(__name__)
lock = threading.Lock()

class MqttTransfer(TransferComponent):

    def __init__(self, config: ConfigEntry, hass: HomeAssistant, new_data_callback = None):
        super().__init__(config)
        #self._state_topic = config.data[CONF_MQTT_PREFIX] + "/" + config.data[CONF_TOPIC_MOTION_DETECTION_IMAGE]
        self._state_topic = config[CONF_TOPIC]
        self._mqtt_subscription = None
        self._last_image = None
        self._last_updated = None
        self._hass = hass
        self._files: queue.Queue = queue.Queue()
        self._new_data_callback = new_data_callback
        fire_coroutine_threadsafe(self.subscribe_to_mqtt(), hass.loop)

    @callback
    def message_received(self, msg):
        """Handle new MQTT messages."""
        _LOGGER.debug(f"|{self._state_topic}| MQTT : {msg.topic}")
        data = msg.payload
        self._last_updated = datetime.now()
        self._last_image = data
        file = MqttFileInfo(data)
        self._files.en.put(file)
        self._new_data_callback(self)
        # self._run(with_transfer=True)

    async def subscribe_to_mqtt(self):
        self._subscription = await mqtt.async_subscribe(
            self._hass, self._state_topic, self.message_received, 0, None
        )
        return

    def get_files(self, max=None) -> list[IFileInfo]:
        ''' OVERRIDE '''
        with lock:
            result = []
            while self._files.qsize() > 0:
                result.append(self._files.get())
        return result

    def file_read(self, file: IFileInfo) -> Any:
        ''' OVERRIDE '''
        return io.BytesIO(self._last_image)

    def file_delete(self, file: IFileInfo):
        ''' OVERRIDE '''
        pass

    def file_save(self, file: IFileInfo, content) -> str:
        ''' OVERRIDE '''
        return ""

