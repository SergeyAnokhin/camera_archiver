from typing import cast
from .ifile_info import IFileInfo
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import generate_entity_id
from .transfer_component import TransferComponent
from ..lib_directory.DirectoryTransfer import DirectoryTransfer
from ..lib_ftp.FtpTransfer import FtpTransfer
from .transfer_state import TransferState
from ..const import ATTR_CAMERA, ATTR_DESTINATION_FILE, ATTR_EXT, ATTR_LOCAL_FILE, ATTR_PATH, ATTR_TIMESTAMP, CONF_DIRECTORY, CONF_FROM, CONF_FTP, CONF_LOCAL_STORAGE, CONF_TO, EVENT_CAMERA_ARCHIVER_FILE_COPIED
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_NAME

class TransferRunner:

    def __init__(self, config: ConfigEntry, hass: HomeAssistant):
        self._config = config
        self._hass = hass
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

        for c in self._to_components:
            c.copiedFileCallback = self.fire_event

    def stat(self) -> TransferState:
        component_from = self._from_components[0]
        return component_from.state()

    def run(self) -> TransferState:
        entity_id = generate_entity_id("archiver_{}", self._config[CONF_NAME], current_ids=None, hass=self._hass)
        local_path_without_ext = f"{self._config[CONF_LOCAL_STORAGE]}/{entity_id}"

        component_from = self._from_components[0]
        return component_from.run(local_path_without_ext)

    def fire_event(self, data):
        localFile = cast(IFileInfo, data[ATTR_LOCAL_FILE])
        destFile = data[ATTR_DESTINATION_FILE]

        entry = localFile.metadata | {
            ATTR_TIMESTAMP: localFile.modif_datetime,
            ATTR_CAMERA: self._config[CONF_NAME],
            ATTR_EXT: localFile.ext,
            ATTR_PATH: destFile,
        }

        self._hass.bus.fire(EVENT_CAMERA_ARCHIVER_FILE_COPIED, entry)