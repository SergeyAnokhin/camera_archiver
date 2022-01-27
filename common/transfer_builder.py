import logging

from homeassistant.const import CONF_NAME, CONF_PLATFORM
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

from ..const import CONF_FROM, CONF_TO
from ..lib_camera.camera_transfer import CameraTransfer
from ..lib_directory.DirectoryTransfer import DirectoryTransfer
from ..lib_ftp.FtpTransfer import FtpTransfer
from ..lib_mqtt.MqttTransfer import MqttTransfer
from .helper import getLogger
from .state_collector import (AbstractCollector, FileAppenderCollector,
                              FilesSetCollector, SetObjectCollector)
from .transfer_component import TransferComponent, TransferComponentId
from .transfer_component_id import TransferType
from .transfer_entity_context import TransferEntityContext
from .transfer_state import EventType

COMPONENTS_LIST = [
    FtpTransfer,
    DirectoryTransfer,
    MqttTransfer
]

COLLECTOR_STATE_TYPES = { 
    EventType.READ: FileAppenderCollector, 
    EventType.SAVE: FileAppenderCollector,
    EventType.REPOSITORY: FilesSetCollector,
    EventType.SET_SCHEDULER: SetObjectCollector,
 }

class TransferBuilder:

    def __init__(self, hass: HomeAssistant, platform_config: dict, config: dict) -> None:
        self._hass = hass
        self._config = config
        self._coordinator: DataUpdateCoordinator = None
        self._name = self._config[CONF_NAME]
        self.logger = getLogger(__name__, self._name)
        self._context: TransferEntityContext = TransferEntityContext(config, hass)
        self._from_comps: list[TransferComponent] = []
        self._to_comps: list[TransferComponent] = []
        self._collectors: dict[TransferComponentId:  dict[EventType: AbstractCollector]] = {}

    def build(self):
        self.logger.debug(f"Build transfer components")
        # Read config, create TransferComponents
        self._from_comps = self.build_components(self._config, TransferType.FROM)
        self._to_comps = self.build_components(self._config, TransferType.TO)
        self._collectors = self.build_collectors([*self._from_comps, *self._to_comps])

        # Link components 'From'TransferComponent 1<->n 'To'TransferComponent (READ)
        for to_comp in self._to_comps:
            for from_comp in self._from_comps:
                from_comp.add_listener(EventType.READ, to_comp._new_file_readed)

        collector: AbstractCollector = None
        # Listen components by collectors
        for comp in self._from_comps:
            collector = self._collectors[comp.Id][EventType.READ]
            comp.add_listener(EventType.READ, collector.append)
            collector = self._collectors[comp.Id][EventType.REPOSITORY]
            comp.add_listener(EventType.REPOSITORY, collector.append)
        for comp in self._to_comps:
            collector = self._collectors[comp.Id][EventType.SAVE]
            comp.add_listener(EventType.SAVE, collector.append)

        # Listen from DataUpdateCoordinator by component
        for comp in self._from_comps:
            collector = self._collectors[comp.Id][EventType.READ]
            collector.add_listener(comp.settings_changed)
            collector = self._collectors[comp.Id][EventType.REPOSITORY]
            collector.add_listener(comp.settings_changed)
        for comp in self._to_comps:
            collector = self._collectors[comp.Id][EventType.SAVE]
            collector.add_listener(comp.settings_changed)

        # Listen from components SAVE by runner
        for comp in self._to_comps:
            comp.add_listener(EventType.SAVE, self._context.fire_post_event)

        # Listen from components scheduler next run by coordinator
        for comp in self._from_comps:
            if comp.has_scheduler:
                collector = self._collectors[comp.Id][EventType.SET_SCHEDULER]
                comp.add_listener(EventType.SET_SCHEDULER, collector.append)


    def build_coordinators_dict(self) -> dict[TransferComponentId:  dict[EventType: DataUpdateCoordinator]]:
        result = { 
            key: { # TransferComponentId:
                key1: value1.coordinator # StateType: DataUpdateCoordinator
                for key1, value1 in value.items()    
            }
            for key, value in self._collectors.items()
        }
        return result
            
    def build_components(self, config: dict, transferType: TransferType) -> list[TransferComponent]:
        components: list[TransferComponent] = []
        components_by_platform = {c.platform: c for c in COMPONENTS_LIST}

        for value in config[transferType.value]:
            platform = value[CONF_PLATFORM]
            class_type = components_by_platform[platform]
            id = TransferComponentId(self._name, transferType)
            transfer = class_type(id, self._hass, value)
            components.append(transfer)
        return components      

    def build_collectors(self, comps: list[TransferComponent]) -> dict[TransferComponentId:  dict[EventType: AbstractCollector]]:
        return {
            comp.Id: self.build_collectors_by_state(comp.Id) 
            for comp in comps
        }

    def build_collectors_by_state(self, id: TransferComponentId) -> dict[EventType: AbstractCollector]:
        return {
            type: self.build_collector(id, type) 
            for type in EventType
        }

    def build_collector(self, id: TransferComponentId, type: EventType) -> AbstractCollector:
        coordinator = DataUpdateCoordinator(
            self._hass,
            logging.getLogger(__name__),
            name=f"{id.id}({type.value})",
        )
        
        collector = COLLECTOR_STATE_TYPES[type](id, type, coordinator)
        return collector
