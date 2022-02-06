from typing import Any

from config.custom_components.camera_archiver.lib_service.service_component import \
    ServiceComponent
from homeassistant.const import CONF_ID, CONF_PLATFORM, CONF_SENSORS, CONF_TYPE
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

    def build_pipeline(self, pipeline_config: dict) -> list[SensorConnector]:
        id = pipeline_config[CONF_ID]
        sensors = self.get_pipeline(pipeline_config)
        return sensors

    def get_component(self, comp_config) -> Component:
        return self._comp_constructor_by_platform(self._hass, comp_config)

    def get_sensor(self, sensor_config) -> SensorConnector:
        return SensorConnector(sensor_config)

    def get_pipeline(self, pipe_config) -> list[SensorConnector]:
        pipelineBuilder = PipelineBuilder(pipe_config, self._components, self._sensors)
        sensors = pipelineBuilder.build()
        root_component = pipelineBuilder.component
        switch = SensorConnector({
            CONF_ID: f"Pipeline {id}",
            CONF_PLATFORM: SensorPlatforms.switch
        })
        switch.add_listener(root_component.callback)
        sensors.append(switch)
        return sensors
