from .FtpTransfer import FtpTransfer
from .const import DEFAULT_SCAN_INTERVAL, HA_FILES_COPIED, HA_FILES_COPIED_24_HOURS, ICON_24HOURS, ICON_COPIED
from .sensor import TransferSensor
from homeassistant.core import ServiceCall
from homeassistant.helpers.event import track_time_interval, call_later

class CameraArchive:
    def __init__(self, hass, config):
        self.sensors = []
        self.FileTransferCallback = None
        self.config = config

        #call_later(hass, 5, self.update_data)

        # Add sensors
        self._sensor_files_copied = TransferSensor(HA_FILES_COPIED, ICON_COPIED)
        self.sensors.append(self._sensor_files_copied)
        self._sensor_files_copied = TransferSensor(HA_FILES_COPIED_24_HOURS, ICON_24HOURS)
        self.sensors.append(self._sensor_files_copied)

        #track_time_interval(hass, self.update_gazpar_data, DEFAULT_SCAN_INTERVAL)

    def run(self, call: ServiceCall):

        tr = FtpTransfer(self.config)
        tr.OnFileTransferCallback(self.FileTransferCallback)
        tr.Copy(max=1)
