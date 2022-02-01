from abc import abstractmethod
from sys import platform
from typing import Any, cast

from .. import SensorPlatforms
from .generic_listener import GenericListener
from ..lib_api.api_component import ApiComponent
from ..lib_directory.DirectoryTransfer import DirectoryTransfer
from ..lib_elasticsearch.elasticsearch_component import ElasticsearchComponent
from ..lib_ftp.FtpTransfer import FtpTransfer
from ..lib_imap.imap_component import ImapComponent
from ..lib_mqtt.MqttTransfer import MqttTransfer
from .transfer_component import TransferComponent
from ..const import CONF_COMPONENTS, CONF_PIPELINES, CONF_TRIGGERS
from homeassistant.const import CONF_ID, CONF_PLATFORM, CONF_SENSORS
from homeassistant.core import HomeAssistant, callback

COMPONENTS_LIST = [
    FtpTransfer,
    DirectoryTransfer,
    MqttTransfer,
    ElasticsearchComponent,
    ApiComponent,
    ImapComponent
]

TRIGGERS_LIST = [

]

class SensorConnector(GenericListener):

    def __init__(self, config) -> None:
        GenericListener.__init__(self)
        self._platform = config[CONF_PLATFORM]

    def __init__(self, platform: SensorPlatforms) -> None:
        GenericListener.__init__(self)
        self._platform = platform.value

class PipelineBuilder:

    def __init__(self, config) -> None:
        self._config = config
        self._triggers = [GenericTrigger(c) for c in config[CONF_TRIGGERS]]

    @callback
    def enable(self, event_content):
        enable = cast(bool, event_content)
        [trigger.enable(enable) for trigger in self._triggers]

class Builder:

    def __init__(self, hass: HomeAssistant, config: dict) -> None:
        self._hass = hass
        self._config = config
        self._components: dict[str, Any] = {}
        self._sensors: dict[str, Any] = {}
        self._comp_constructor_by_platform: dict[str, Any] = {c.Platform: c for c in COMPONENTS_LIST}

    def build_components(self):
        self._components = {
            value[CONF_ID]: self.get_component(value) 
            for value in self._config[CONF_COMPONENTS]
        }

    def build_sensors(self):
        self._sensors = {
            value[CONF_ID]: self.get_sensor(value) 
            for value in self._config[CONF_SENSORS]
        }

    def build_pipeline(self, pipeline_config: dict):
        id = pipeline_config[CONF_ID]
        pipeline = self.get_pipeline(pipeline_config)
        switch = SensorConnector(SensorPlatforms.switch)
        switch.add_listener(pipeline.enable)
        self._sensors[f"Pipeline {id}"] = switch
        return pipeline

    def get_component(self, comp_config) -> TransferComponent:
        return self._comp_constructor_by_platform(self._hass, comp_config)

    def get_sensor(self, sensor_config) -> SensorConnector:
        return SensorConnector(sensor_config)

    def get_pipeline(self, pipe_config) -> PipelineBuilder:
        return PipelineBuilder(pipe_config)