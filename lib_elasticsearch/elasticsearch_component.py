from homeassistant.core import HomeAssistant

from ..common.component import Component
from ..const import CONF_ELASTICSEARCH


class ElasticsearchComponent(Component):
    Platform = CONF_ELASTICSEARCH

    def __init__(self, hass: HomeAssistant, config: dict) -> None:
        super().__init__(hass, config)
