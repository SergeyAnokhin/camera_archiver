import copy
from typing import Any

from homeassistant.const import CONF_ID
from homeassistant.core import HomeAssistant

from ..const import CONF_COMPONENT, CONF_LISTENERS, CONF_SENSOR
from .component import Component
from .helper import getLogger
from .types import COMPONENTS_LIST, ComponentDescriptor, SensorConnector


class PipelineBuilder:

    def __init__(self, hass: HomeAssistant, config, components: dict[str, ComponentDescriptor], sensors: dict[str, SensorConnector]) -> None:
        self._config = config
        self._hass = hass
        self.component: Component = None
        self._components: dict[str, ComponentDescriptor] = components
        self._sensors: dict[str, SensorConnector] = sensors
        self._id = self._config[CONF_ID]
        self._logger = getLogger(__name__, self._id)
        self._sensors_to_create: list[SensorConnector] = []
        self._comp_constructor_by_platform: dict[str, Any] = {c.Platform: c for c in COMPONENTS_LIST}

    def build(self) -> list[SensorConnector]:
        self.component = self.get_component(self._config, f"{self._id}::")
        self.build_listeners(self.component, self._config)
        return self._sensors_to_create

    def build_listeners(self, parent: Component, config: dict):
        if CONF_LISTENERS not in config:
            return

        listeners = config[CONF_LISTENERS]
        for l in listeners:
            if CONF_SENSOR in l:
                sensor = self.get_sensor(l, parent)
                self._sensors_to_create.append(sensor)
            if CONF_COMPONENT in l:
                component = self.get_component(l, parent)
                self.build_listeners(component, l)
                
    def get_sensor(self, config, parent: Component) -> SensorConnector:
        sensor_id = config[CONF_SENSOR]
        if sensor_id not in self._sensors:
            error = f"Cant found sensor id '{sensor_id}' in sensor list. Pipeline: {self._id}"
            self._logger.error(error)
            raise Exception(error)
        sensor = self._sensors[sensor_id]
        clone: SensorConnector = copy.deepcopy(sensor)
        clone.pipeline_path = f"{parent.pipeline_path}/{sensor_id}"
        clone.parent = parent.id
        clone.pipeline_id = self._id
        parent.add_listener(clone.callback)
        return clone

    def get_component(self, config, parent: Component) -> Component:
        component_id = config[CONF_COMPONENT]

        if component_id not in self._components:
            error = f"Cant found component id '{component_id}' in component list. Pipeline: {self._id}"
            self._logger.error(error)
            raise Exception(error)
        desc = self._components[component_id]
        comp: Component = self._comp_constructor_by_platform[desc.Platform](self._hass, desc.config) 
        comp.pipeline_path = f"{parent.pipeline_path}/{comp.id}"
        comp.pipeline_id = self._id
        comp.parent = parent
        parent.add_listener(comp.callback)
        return comp
