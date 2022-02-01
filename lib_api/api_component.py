from config.custom_components.camera_archiver.const import CONF_API
from homeassistant.core import HomeAssistant
from ..common.component import Component


class ApiComponent(Component):
    Platform = CONF_API

    def __init__(self, hass: HomeAssistant, config: dict) -> None:
        super().__init__(hass, config)