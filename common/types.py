from enum import Enum

from homeassistant.const import CONF_ICON, CONF_ID, CONF_PLATFORM, CONF_TYPE

from ..const import (CONF_API, CONF_CAMERA, CONF_DIRECTORY, CONF_ELASTICSEARCH,
                     CONF_FTP, CONF_IMAP, CONF_MQTT, CONF_SCHEDULER,
                     CONF_SENSOR, CONF_SWITCH)
from .event_objects import EventObject
from .generic_observable import GenericObservable


class Pipeline:

    def __init__(self, config: dict) -> None:
        self.id = config[CONF_ID]
        self.component = None

class ComponentPlatforms(Enum):
    MQTT = CONF_MQTT
    DIRECTORY: CONF_DIRECTORY
    FTP = CONF_FTP
    ELASTICSEARCH = CONF_ELASTICSEARCH
    API = CONF_API
    IMAP = CONF_IMAP


class SensorPlatforms(Enum):
    camera = CONF_CAMERA
    sensor = CONF_SENSOR
    switch = CONF_SWITCH


class TriggerPlatforms(Enum):
    SCHEDULER = CONF_SCHEDULER
    MQTT = CONF_MQTT
    SENSOR = CONF_SENSOR

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
