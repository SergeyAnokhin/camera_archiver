from datetime import datetime
import logging
from typing import Any

from homeassistant.util.async_ import fire_coroutine_threadsafe

from ..const import CONF_TOPIC
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.components import mqtt
from ..common.ifile_info import IFileInfo
from ..common.transfer_component import TransferComponent

_LOGGER = logging.getLogger(__name__)

class MqttTransfer(TransferComponent):

    def __init__(self, config: ConfigEntry, hass: HomeAssistant):
        super().__init__(config)
        #self._state_topic = config.data[CONF_MQTT_PREFIX] + "/" + config.data[CONF_TOPIC_MOTION_DETECTION_IMAGE]
        self._state_topic = config[CONF_TOPIC]
        self._mqtt_subscription = None
        self._last_image = None
        self._last_updated = None
        self._hass = hass
        fire_coroutine_threadsafe(self.subscribe_to_mqtt(), hass.loop)

    @callback
    def message_received(self, msg):
        """Handle new MQTT messages."""
        data = msg.payload
        self._last_updated = datetime.now()
        self._last_image = data

    async def subscribe_to_mqtt(self):
        self._subscription = await mqtt.async_subscribe(
            self._hass, self._state_topic, self.message_received
        )
        return

    def get_files(self, max=None) -> list[IFileInfo]:
        ''' OVERRIDE '''
        files: list[IFileInfo] = []
        return files

    def file_read(self, file: IFileInfo) -> Any:
        ''' OVERRIDE '''
        return None

    def file_delete(self, file: IFileInfo):
        ''' OVERRIDE '''
        pass

    def file_save(self, file: IFileInfo, content) -> str:
        ''' OVERRIDE '''
        return ""

