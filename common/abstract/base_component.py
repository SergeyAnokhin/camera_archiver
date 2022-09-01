from homeassistant.const import CONF_ID
from homeassistant.core import HomeAssistant

from ...common.helper import getLogger
from ...const import CONF_FILTER
from .concept_component import ConceptComponent


class BaseComponent(ConceptComponent):
    """Implement technical functionality"""

    def __init__(self, hass: HomeAssistant, config: dict) -> None:
        super().__init__()
        self._id = config[CONF_ID]
        self._pipeline_path: str = None
        self._is_enabled: bool = True
        self._logger = getLogger(__name__, self._id)

        self._hass = hass
        self._config = config
        self._filter = config.get(CONF_FILTER, {})

    @property
    def id(self):
        return self._id
