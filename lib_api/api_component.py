from config.custom_components.camera_archiver.const import CONF_API
from homeassistant.core import HomeAssistant
from ..common.transfer_component import TransferComponent


class ApiComponent(TransferComponent):
    Platform = CONF_API

    def __init__(self, hass: HomeAssistant, config: dict) -> None:
        super().__init__(hass, config)