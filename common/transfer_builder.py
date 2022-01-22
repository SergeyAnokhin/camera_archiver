import logging

from homeassistant.const import CONF_NAME, CONF_PLATFORM
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

from ..const import CONF_FROM, CONF_TO
from ..lib_directory.DirectoryTransfer import DirectoryTransfer
from ..lib_ftp.FtpTransfer import FtpTransfer
from ..lib_mqtt.MqttTransfer import MqttTransfer
from .helper import getLogger
from .state_collector import StateCollector
from .transfer_component import TransferComponent, TransferComponentId
from .transfer_component_id import TransferType
from .transfer_entity_context import TransferEntityContext
from .transfer_state import StateType

COMPONENTS_LIST = [
    FtpTransfer,
    DirectoryTransfer,
    MqttTransfer,
]

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
        self._collectors: dict[TransferComponentId:  dict[StateType: StateCollector]] = {}

    def build(self):
        self.logger.debug(f"Build transfer components")
        # Read config, create TransferComponents
        self._from_comps = self.build_components(self._config, TransferType.FROM)
        self._to_comps = self.build_components(self._config, TransferType.TO)
        self._collectors = self.build_collectors([*self._from_comps, *self._to_comps])

        # Link components 'From'TransferComponent 1<->n 'To'TransferComponent (READ)
        for to_comp in self._to_comps:
            for from_comp in self._from_comps:
                from_comp.add_listener(StateType.READ, to_comp._new_file_readed)

        collector: StateCollector = None
        # Listen components by StateCollector
        for comp in self._from_comps:
            collector = self._collectors[comp.Id][StateType.READ]
            comp.add_listener(StateType.READ, collector.append)
            collector = self._collectors[comp.Id][StateType.REPOSITORY]
            comp.add_listener(StateType.REPOSITORY, collector.set)
        for comp in self._to_comps:
            collector = self._collectors[comp.Id][StateType.SAVE]
            comp.add_listener(StateType.SAVE, collector.append)

        # Listen from DataUpdateCoordinator by component
        for comp in self._from_comps:
            collector = self._collectors[comp.Id][StateType.READ]
            collector.add_listener(comp.settings_changed)
            collector = self._collectors[comp.Id][StateType.REPOSITORY]
            collector.add_listener(comp.settings_changed)
        for comp in self._to_comps:
            collector = self._collectors[comp.Id][StateType.SAVE]
            collector.add_listener(comp.settings_changed)


        # Listen from components SAVE by runner
        for comp in self._to_comps:
            comp.add_listener(StateType.SAVE, self._context.fire_post_event)


    def build_coordinators_dict(self) -> dict[TransferComponentId:  dict[StateType: DataUpdateCoordinator]]:
        return { 
            key: { # TransferComponentId:
                key1: value1.coordinator # StateType: DataUpdateCoordinator
                for key1, value1 in value.items()    
            }
            for key, value in self._collectors.items()
        }
            
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

    def build_collectors(self, comps: list[TransferComponent]) -> dict[TransferComponentId:  dict[StateType: StateCollector]]:
        return {
            comp.Id: self.build_collectors_by_state(comp.Id) 
            for comp in comps
        }

    def build_collectors_by_state(self, id: TransferComponentId) -> dict[StateType: StateCollector]:
        return {
            type: self.build_collector(id, type) 
            for type in StateType
        }

    def build_collector(self, id: TransferComponentId, type: StateType) -> StateCollector:
        coordinator = DataUpdateCoordinator(
            self._hass,
            logging.getLogger(__name__),
            name=f"{id.id}({type.value})",
            # request_refresh_debouncer=Debouncer(
            #     hass, self.logger, cooldown=600, immediate=False
            # )
        )

        return StateCollector(id, type, coordinator)


        # hass.data[DOMAIN][self._name] = coordinatorInst
        # def _enable_scheduled_speedtests(*_):
        #     """Activate the data update coordinator."""
        #     coordinatorInst.update_interval = timedelta(days = 10)

        # if hass.state == CoreState.running:
        #     _enable_scheduled_speedtests()
        # else:
        #     # Running a speed test during startup can prevent
        #     # integrations from being able to setup because it
        #     # can saturate the network interface.
        #     hass.bus.async_listen_once(
        #         EVENT_HOMEASSISTANT_STARTED, _enable_scheduled_speedtests
        #     )

        # await async_setup_sensor_registry_updates(hass, sensor_registry, scan_interval)
