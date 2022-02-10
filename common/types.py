from enum import Enum
from .component import Component
from ..lib_api.api_component import ApiComponent
from ..lib_directory.DirectoryTransfer import DirectoryTransfer
from ..lib_elasticsearch.elasticsearch_component import ElasticsearchComponent
from ..lib_filter.filter_component import FilterComponent
from ..lib_ftp.FtpTransfer import FtpTransfer
from ..lib_imap.imap_component import ImapComponent
from ..lib_mqtt.MqttTransfer import MqttTransfer
from ..lib_scheduler.scheduler_component import SchedulerComponent
from ..lib_service.service_component import ServiceComponent

from homeassistant.const import CONF_ICON, CONF_ID, CONF_PLATFORM, CONF_TYPE

from ..const import (CONF_API, CONF_CAMERA, CONF_DIRECTORY, CONF_ELASTICSEARCH,
                     CONF_FTP, CONF_IMAP, CONF_MQTT, CONF_SCHEDULER,
                     CONF_SENSOR, CONF_SWITCH, ICON_DEFAULT)
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

class ComponentDescriptor:

    def __init__(self, config) -> None:
        self.config = config
        self.id = config[CONF_ID]
        self.Platform = config[CONF_PLATFORM]

    def __str__(self):
         return f"CompDesc: #{self.id} @{self.Platform}"

    def __repr__(self):
        return self.__str__()


class SensorConnector(GenericObservable):

    def __init__(self, config: dict) -> None:
        GenericObservable.__init__(self)
        self.id = config[CONF_ID]
        self.platform: SensorPlatforms = config[CONF_PLATFORM]
        self.icon = config.get(CONF_ICON, ICON_DEFAULT)
        self.type = config.get(CONF_TYPE, "")
        self.pipeline_path: str = None
        self.parent: str = None
        self.pipeline_id: str = None

    def callback(self, eventObject: EventObject):
        self.invoke_listeners(eventObject)

    def __str__(self):
         return f"#{self.id} [{self.platform}] Listeners:{len(self._listeners)} Path: {self.pipeline_path}"

    def __repr__(self):
        return self.__str__()


COMPONENTS_LIST: list[Component] = [
    FtpTransfer,
    DirectoryTransfer,
    MqttTransfer,
    ElasticsearchComponent,
    ApiComponent,
    ImapComponent,
    ServiceComponent,
    SchedulerComponent,
    FilterComponent
]
