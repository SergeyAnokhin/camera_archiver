from homeassistant.core import HomeAssistant

from ..common.transfer_component import TransferComponent
from ..const import CONF_ELASTICSEARCH


class ElasticsearchComponent(TransferComponent):
    Platform = CONF_ELASTICSEARCH

    def __init__(self, hass: HomeAssistant, config: dict) -> None:
        super().__init__(hass, config)
