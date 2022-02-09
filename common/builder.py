from typing import Any

from homeassistant.const import CONF_ID, CONF_PLATFORM, CONF_SENSORS
from homeassistant.core import HomeAssistant

from .. import SensorPlatforms
from ..const import CONF_COMPONENTS
from .pipeline_builder import PipelineBuilder
from .types import ComponentDescriptor, SensorConnector

class Builder:

    def __init__(self, hass: HomeAssistant, config: dict) -> None:
        self._hass = hass
        self._config = config
        self._components: dict[str, ComponentDescriptor] = {}
        self._sensors: dict[str, SensorConnector] = {}

    def build_components(self):
        for value in self._config[CONF_COMPONENTS]:
            comp = self.get_component(value)
            id = value[CONF_ID]
            self._components[id] = comp

    def build_sensors(self):
        self._sensors = {
            value[CONF_ID]: self.get_sensor(value) 
            for value in self._config[CONF_SENSORS]
        }

    def build_pipeline(self, pipeline_config: dict) -> list[SensorConnector]:
        id = pipeline_config[CONF_ID]
        sensors = self.get_pipeline(pipeline_config)
        return sensors

    def get_component(self, comp_config) -> ComponentDescriptor:
        return ComponentDescriptor(comp_config)

    def get_sensor(self, sensor_config) -> SensorConnector:
        return SensorConnector(sensor_config)

    def get_pipeline(self, pipe_config) -> list[SensorConnector]:
        pipelineBuilder = PipelineBuilder(self._hass, pipe_config, self._components, self._sensors)
        sensors = pipelineBuilder.build()
        root_component = pipelineBuilder.component
        switch = SensorConnector({
            CONF_ID: f"Pipeline {id}",
            CONF_PLATFORM: SensorPlatforms.switch
        })
        switch.add_listener(root_component.callback)
        sensors.append(switch)
        return sensors
