from .lib_directory.DirectoryTransfer import DirectoryTransfer
from .lib_ftp.FtpTransfer import FtpTransfer
from .transfer_state import TransferState
from .const import CONF_DIRECTORY, CONF_FROM, CONF_FTP, CONF_TO
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator


class TransferRunner:

    def __init__(self, config: ConfigEntry, coordinator: DataUpdateCoordinator):
        self._config = config
        self._coordinator = coordinator
        self._from_components = []
        self._to_components = []

        cfrom = config[CONF_FROM]
        if CONF_DIRECTORY in cfrom:
            transfer = DirectoryTransfer(cfrom[CONF_DIRECTORY])
            self._from_components.append(transfer)
        if CONF_FTP in cfrom:
            transfer = FtpTransfer(cfrom[CONF_FTP])
            self._from_components.append(transfer)

        tfrom = config[CONF_TO]
        # if CONF_DIRECTORY in tfrom:
        #     transfer = DirectoryTransfer(tfrom[CONF_DIRECTORY])
        #     self._to_components.append(transfer)
        if CONF_FTP in tfrom:
            transfer = FtpTransfer(tfrom[CONF_FTP])
            self._from_components.set_from(self._from_components)
            self._to_components.append(transfer)


    def stat(self):
        state: TransferState = None

        component_from = self._from_components[0]
        component_to = self._from_components[0]
        state = component_from.run(component_to)

        data[SENSOR_NAME_TO_COPY_FILES] = state

    def run(self):
        pass
