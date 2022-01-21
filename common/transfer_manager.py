import logging

from .state_collector import StateCollector
from .transfer_component import TransferComponent
from ..lib_directory.DirectoryTransfer import DirectoryTransfer
from ..lib_ftp.FtpTransfer import FtpTransfer
from ..lib_mqtt.MqttTransfer import MqttTransfer
from homeassistant.const import CONF_NAME, CONF_PLATFORM
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from ..const import ATTR_ARCHIVER_STATE, CONF_ENABLE, CONF_FROM, CONF_TO, DOMAIN
from .transfer_runner import TransferRunner
from .transfer_state import TransferState

COMPONENTS_LIST = [
    FtpTransfer,
    DirectoryTransfer,
    MqttTransfer,
]

class TransferManager:

    def __init__(self, hass: HomeAssistant, platform_config: dict, config: dict) -> None:
        self._hass = hass
        self._config = config
        self._coordinator: DataUpdateCoordinator = None
        self._name = self._config[CONF_NAME]
        self.logger = logging.getLogger(f"{__name__}::{self._name}")
        self._runner: TransferRunner = TransferRunner(config, hass)
        self._from_comps: list[TransferComponent] = []
        self._to_comps: list[TransferComponent] = []
        self._collector: StateCollector = None

    @property
    def coordinator(self) -> DataUpdateCoordinator:
        return self._coordinator

    def build_transfer_components(self):
        self.logger.debug(f"Build transfer components")
        # Read config, create TransferComponents
        self._from_comps = self.build_components(self._config[CONF_FROM])
        self._to_comps = self.build_components(self._config[CONF_TO])

        # Link components 'From'TransferComponent 1<->n 'To'TransferComponent
        for to_comp in self._to_comps:
            for from_comp in self._from_comps:
                from_comp.add_listener(to_comp._new_file_readed)

        # Listen components by StateCollector
        for comp in [*self._to_comps, *self._from_comps]:
            comp.add_listener(self._collector_update)

        for comp in self._from_comps:
            comp.add_listener(to_comp._new_file_readed)

    @callback
    def _collector_update(self, state: TransferState):
        pass
        # self._coordinator.async_set_updated_data(self._coordinator.data)

    def build_components(self, config: list) -> list[TransferComponent]:
        components: list[TransferComponent] = []
        components_by_platform = {c.platform: c for c in COMPONENTS_LIST}

        for value in config:
            platform = value[CONF_PLATFORM]
            class_type = components_by_platform[platform]
            transfer = class_type(self._name, self._hass, value)
            components.append(transfer)
        return components      

    def build_coordinator(self):
        hass = self._hass
        config = self._config

        self.logger.debug(f"Build coordinator")

        coordinatorInst = DataUpdateCoordinator(
            hass,
            logging.getLogger(__name__),
            name=DOMAIN,
            # #update_interval = timedelta(days=10),
            # request_refresh_debouncer=Debouncer(
            #     hass, self.logger, cooldown=600, immediate=False
            # )
        )

        self._runner.coordinator = coordinatorInst
        self._cooridnator = coordinatorInst
        self._collector = StateCollector(self._collector)

        coordinatorInst.last_update_success = False
        coordinatorInst.data = {
            CONF_ENABLE: True,
            ATTR_ARCHIVER_STATE: self._collector
        }
        # hass.data[DOMAIN][self._name] = coordinatorInst


        # def _enable_scheduled_speedtests(*_):
        #     """Activate the data update coordinator."""
        #     coordinatorInst.update_interval = timedelta(days = 10)

        # coordinatorInst.update_interval = config[CONF_SCAN_INTERVAL]
        # coordinatorInst.update_method = self.async_get_status

        #await coordinatorInst.async_refresh()

        # if hass.state == CoreState.running:
        #     _enable_scheduled_speedtests()
        # else:
        #     # Running a speed test during startup can prevent
        #     # integrations from being able to setup because it
        #     # can saturate the network interface.
        #     hass.bus.async_listen_once(
        #         EVENT_HOMEASSISTANT_STARTED, _enable_scheduled_speedtests
        #     )

        # scan_interval = config.get(CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL)
        # await async_setup_sensor_registry_updates(hass, sensor_registry, scan_interval)

