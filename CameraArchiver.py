from config.custom_components.camera_archiver.const import DEFAULT_SCAN_INTERVAL, HA_FILES_COPIED, HA_FILES_COPIED_24_HOURS, ICON_24HOURS, ICON_COPIED
from config.custom_components.camera_archiver.sensor import TransferSensor
from homeassistant.helpers.event import track_time_interval, call_later

class CameraArchive:
    def __init__(self, hass, config):
        self.sensors = []

        call_later(hass, 5, self.update_data)

        # Add sensors
        self._sensor_files_copied = TransferSensor(HA_FILES_COPIED, ICON_COPIED)
        self.sensors.append(self._sensor_files_copied)
        self._sensor_files_copied = TransferSensor(HA_FILES_COPIED_24_HOURS, ICON_24HOURS)
        self.sensors.append(self._sensor_files_copied)

        track_time_interval(hass, self.update_gazpar_data, DEFAULT_SCAN_INTERVAL)

