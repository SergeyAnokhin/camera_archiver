from typing import cast

from homeassistant.core import HomeAssistant

from ..common.component import Component
from ..common.event_objects import FileEventObject
from ..const import CONF_FILTER, CONF_MIMETYPE


class FilterComponent(Component):
    Platform = CONF_FILTER

    def __init__(self, hass: HomeAssistant, config: dict) -> None:
        super().__init__(hass, config)

    def callback(self, eventObj) -> bool:
        if isinstance(eventObj, FileEventObject):
            readEO = cast(FileEventObject, eventObj)
            mimetype = self._config[CONF_MIMETYPE]
            if mimetype and mimetype == readEO.File.mimetype:
                self.invoke_listeners(readEO)


