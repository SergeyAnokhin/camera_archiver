import logging
from .common.archiver_state import ArchiverState
from .common.transfer_component import TransferComponent
from .lib_directory.DirectoryTransfer import DirectoryTransfer
from .lib_ftp.FtpTransfer import FtpTransfer
from .lib_mqtt.MqttTransfer import MqttTransfer
from homeassistant.const import CONF_NAME
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from .const import ATTR_ARCHIVER_STATE, CONF_DIRECTORY, CONF_ENABLE, CONF_FROM, CONF_FTP, CONF_MQTT, CONF_TO, DOMAIN
from .common.transfer_runner import TransferRunner
from .common.transfer_state import TransferState


class TransferManager:
    ''' 
        1. Read config, create TransferComponents
        2. Link components 'From'TransferComponent 1<->n 'To'TransferComponent
        3. Attach to events (DataUpdaterCoordinator, Mqtt, Service etc)
        4. Create Sensors and switchers 
        5. Update sensors with TransferState
    '''

    def __init__(self, hass: HomeAssistant, platform_config: dict, config: dict) -> None:
        self._hass = hass
        self._config = config
        self._coordinator: DataUpdateCoordinator = None
        self._name = self._config[CONF_NAME]
        self.logger = logging.getLogger(f"{__name__}::{self._name}")
        self._runner: TransferRunner = TransferRunner(config, hass)

    def build_transfer_components(self):
        # 1. Read config, create TransferComponents
        from_comps = self.build_components(self._config[CONF_FROM])
        to_comps = self.build_components(self._config[CONF_TO])

        # 2. Link components 'From'TransferComponent 1<->n 'To'TransferComponent
        for to_comp in to_comps:
            for from_comp in from_comps:
                from_comp.add_listener(to_comp._new_file_readed)

        # 3. Attach to events (DataUpdaterCoordinator, Mqtt, Service etc)
        # -- (Obsolete) 3.1 Listen dataUpdater by 'from components'
        # -- (Obsolete)for from_comp in from_comps:
        # -- (Obsolete)    self._coordinator.async_add_listener(from_comp.run)
        # 3.2 Listen 'to components' by DataUpdater
        for to_comp in to_comps:
            to_comp.add_listener(self._coordinator_async_refresh)

    def _coordinator_async_refresh(self, state: TransferState):
        archiverState: ArchiverState = self._coordinator.data[ATTR_ARCHIVER_STATE]
        archiverState.append(state)
        self._coordinator.async_set_updated_data(self._coordinator.data)

    def build_components(self, config: dict) -> list[TransferComponent]:
        components: list[TransferComponent] = []
        if CONF_DIRECTORY in config:
            transfer = DirectoryTransfer(self._hass, config[CONF_DIRECTORY])
            components.append(transfer)
        if CONF_FTP in config:
            transfer = FtpTransfer(self._hass, config[CONF_FTP])
            components.append(transfer)
        if CONF_MQTT in config:
            transfer = MqttTransfer(self._hass, config[CONF_MQTT], self.new_data_callback)
            components.append(transfer)        

    def setup_ha_entries(self, hass: HomeAssistant, config: ConfigEntry, add_entities):
        pass

    def update_sensors(self, state: TransferState):
        pass

    # async def async_get_status(self):
    #     self.logger.info(f"Call Callback sensor.py:get_coordinator.async_get_status() ")
    #     coordinatorInst = self._hass.data[DOMAIN][self._name]
    #     if not self._hass.is_running:
    #         raise UpdateFailed(f"Hass starting in progress")

    #     result: TransferState = None
    #     if not coordinatorInst.data.get(CONF_ENABLE, False):
    #         result = self._runner.stat()
    #     else:
    #         result = self._runner.run()
    #     coordinatorInst.data[ATTR_TRANSFER_RESULT] = result
    #     return coordinatorInst.data

    def build_coordinator(self):
        hass = self._hass
        config = self._config

        self.logger.debug(f"Call sensor.py:get_coordinator() {self._name} HasConfig:{'Yes' if config else 'No'}")

        # self.logger.debug(f"Check coordinator existing")
        # if self._name in hass.data[DOMAIN]:
        #     coordinatorInst = hass.data[DOMAIN][self._name]
        #     self.logger.debug(f"Coordinator reuse Succes: ID# {id(coordinatorInst)}")
        # else:
        coordinatorInst = DataUpdateCoordinator(
            hass,
            logging.getLogger(__name__),
            name=DOMAIN,
            # #update_interval = timedelta(days=10),
            # request_refresh_debouncer=Debouncer(
            #     hass, self.logger, cooldown=600, immediate=False
            # )
        )
        self.logger.debug(f"Coordinator created: ID# {id(coordinatorInst)}")
        coordinatorInst.last_update_success = False
        coordinatorInst.data = {
            CONF_ENABLE: True,
            ATTR_ARCHIVER_STATE: ArchiverState()
        }
        # hass.data[DOMAIN][self._name] = coordinatorInst

        self._runner.coordinator = coordinatorInst
        # def _enable_scheduled_speedtests(*_):
        #     """Activate the data update coordinator."""
        #     coordinatorInst.update_interval = timedelta(days = 10)

        # coordinatorInst.update_interval = config[CONF_SCAN_INTERVAL]
        # coordinatorInst.update_method = self.async_get_status

        coordinatorInst.async_refresh()

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

        self._cooridnator = coordinatorInst
