from .event_objects import EventObject
from generic_observable import GenericObservable
from homeassistant.const import CONF_ICON, CONF_ID, CONF_PLATFORM, CONF_TYPE


class Pipeline:

    def __init__(self, config: dict) -> None:
        self.id = config[CONF_ID]
        self.component = None

class SensorConnector(GenericObservable):

    def __init__(self, config) -> None:
        GenericObservable.__init__(self)
        self.id = config[CONF_ID]
        self.platform = config[CONF_PLATFORM]
        self.icon = config[CONF_ICON]
        self.type = config[CONF_TYPE]
        self.pipeline_path: str = None
        self.parent: str = None
        self.pipeline_id: str = None

    def callback(self, eventObject: EventObject):
        self.invoke_listeners(eventObject)