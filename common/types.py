from generic_observable import GenericObservable
from homeassistant.const import CONF_ID, CONF_PLATFORM, CONF_TYPE


class Pipeline:

    def __init__(self, config: dict) -> None:
        self.id = config[CONF_ID]
        self.component = None

class SensorConnector(GenericObservable):

    def __init__(self, config) -> None:
        GenericObservable.__init__(self)
        self.platform = config[CONF_PLATFORM]
        self.type = config[CONF_TYPE]