
from datetime import datetime, timedelta
from sys import platform
from config.custom_components.camera_archiver.common.transfer_state import EventType
from homeassistant.const import CONF_SCAN_INTERVAL

from homeassistant.core import CALLBACK_TYPE, HomeAssistant
from homeassistant.helpers.event import async_track_point_in_time

from ...const import CONF_SCHEDULER


class SchedulerTrigger:
    platform = CONF_SCHEDULER

    def __init__(self, hass: HomeAssistant, config: dict) -> None:
        self._hass = hass
        self._config = config
        self._unsub_refresh: CALLBACK_TYPE = None
        self._next_run = None

    def schedule_off(self):
        self._schedule_off()
        self._invoke_scheduler_listeners()
        
    def _schedule_off(self):
        if self._unsub_refresh:
            self._unsub_refresh()
            self._unsub_refresh = None
        self._next_run = None

    def _schedule_refresh(self):
        self._schedule_off()
        if not self.has_scheduler \
            or not self._is_enabled[EventType.REPOSITORY]:
            return

        scan_interval: timedelta = self._config[CONF_SCAN_INTERVAL]
        self._next_run = datetime.now().replace(microsecond=0) + scan_interval
        self._unsub_refresh = async_track_point_in_time(
            self._hass, self._job, self._next_run,
        )
        self._invoke_scheduler_listeners()

