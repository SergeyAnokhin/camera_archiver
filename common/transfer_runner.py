from homeassistant.components.sensor import ENTITY_ID_FORMAT
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import generate_entity_id
from .transfer_component import TransferComponent
from ..lib_directory.DirectoryTransfer import DirectoryTransfer
from ..lib_ftp.FtpTransfer import FtpTransfer
from .transfer_state import TransferState
from ..const import CONF_DIRECTORY, CONF_FROM, CONF_FTP, CONF_LOCAL_STORAGE, CONF_TO, SENSOR_NAME_TO_COPY_FILES
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator
from homeassistant.const import CONF_NAME

class TransferRunner:

    def __init__(self, config: ConfigEntry, coordinator: DataUpdateCoordinator, hass: HomeAssistant):
        self._config = config
        self._hass = hass
        self._coordinator = coordinator
        self._from_components: list[TransferComponent] = []
        self._to_components: list[TransferComponent] = []

        cfrom = config[CONF_FROM]
        if CONF_DIRECTORY in cfrom:
            transfer = DirectoryTransfer(cfrom[CONF_DIRECTORY])
            self._from_components.append(transfer)
        if CONF_FTP in cfrom:
            transfer = FtpTransfer(cfrom[CONF_FTP])
            self._from_components.append(transfer)

        tfrom = config[CONF_TO]
        if CONF_DIRECTORY in tfrom:
            transfer = DirectoryTransfer(tfrom[CONF_DIRECTORY])
            transfer.set_from(self._from_components)
            self._to_components.append(transfer)
        if CONF_FTP in tfrom:
            transfer = FtpTransfer(tfrom[CONF_FTP])
            transfer.set_from(self._from_components)
            self._to_components.append(transfer)


    def stat(self):
        state: TransferState = None
        data = {}

        component_from = self._from_components[0]
        state = component_from.state()

        data[SENSOR_NAME_TO_COPY_FILES] = state

        return data

    def run(self):
        state: TransferState = None
        data = {}

        entity_id = generate_entity_id("archiver_{}", self._config[CONF_NAME], current_ids=None, hass=self._hass)
        local_path_without_ext = f"{self._config[CONF_LOCAL_STORAGE]}/{entity_id}"

        component_from = self._from_components[0]
        state = component_from.run(local_path_without_ext)

        data[SENSOR_NAME_TO_COPY_FILES] = state

        return data
