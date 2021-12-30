import logging
from typing import Any
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from ..common.ifile_info import IFileInfo
from ..common.transfer_component import TransferComponent

_LOGGER = logging.getLogger(__name__)

class MqttTransfer(TransferComponent):

    def __init__(self, config: ConfigEntry):
        super().__init__(config)
        #self._state_topic = config.data[CONF_MQTT_PREFIX] + "/" + config.data[CONF_TOPIC_MOTION_DETECTION_IMAGE]
        self._mqtt_subscription = None
        self._last_image = None

        @callback
        def message_received(msg):
            """Handle new MQTT messages."""
            data = msg.payload

            self._last_image = data

        # self._mqtt_subscription = await mqtt.async_subscribe(
        #     self.hass, self._state_topic, message_received, 1, None
        # )


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

