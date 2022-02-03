from typing import Any

from config.custom_components.camera_archiver.lib_service.service_component import \
    ServiceComponent
from homeassistant.const import CONF_ID, CONF_SENSORS
from homeassistant.core import HomeAssistant, callback

from .. import SensorPlatforms
from ..const import CONF_COMPONENTS
from ..lib_api.api_component import ApiComponent
from ..lib_directory.DirectoryTransfer import DirectoryTransfer
from ..lib_elasticsearch.elasticsearch_component import ElasticsearchComponent
from ..lib_ftp.FtpTransfer import FtpTransfer
from ..lib_imap.imap_component import ImapComponent
from ..lib_mqtt.MqttTransfer import MqttTransfer
from .component import Component
from .pipeline_builder import PipelineBuilder
from .types import SensorConnector

COMPONENTS_LIST: list[Component] = [
    FtpTransfer,
    DirectoryTransfer,
    MqttTransfer,
    ElasticsearchComponent,
    ApiComponent,
    ImapComponent,
    ServiceComponent
]

class Builder:

    def __init__(self, hass: HomeAssistant, config: dict) -> None:
        self._hass = hass
        self._config = config
        self._components: dict[str, Component] = {}
        self._sensors: dict[str, SensorConnector] = {}
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
        self.get_pipeline(pipeline_config)
        # return pipeline

    def get_component(self, comp_config) -> Component:
        return self._comp_constructor_by_platform(self._hass, comp_config)

    def get_sensor(self, sensor_config) -> SensorConnector:
        return SensorConnector(sensor_config)

    def get_pipeline(self, pipe_config) -> PipelineBuilder:
        pipelineBuilder = PipelineBuilder(pipe_config, self._components, self._sensors)
        root_component = pipelineBuilder.component
        switch = SensorConnector(SensorPlatforms.switch)
        switch.add_listener(root_component.callback)
        self._sensors[f"Pipeline {id}"] = switch

