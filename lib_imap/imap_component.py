from homeassistant.core import HomeAssistant

from ..common.component import Component
from ..common.transfer_component_id import TransferComponentId
from ..const import CONF_IMAP


class ImapComponent(Component):
    Platform = CONF_IMAP

    def __init__(self, hass: HomeAssistant, config: dict) -> None:
        super().__init__(hass, config)
