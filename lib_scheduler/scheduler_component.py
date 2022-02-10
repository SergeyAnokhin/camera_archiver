from datetime import datetime, timedelta

from homeassistant.const import CONF_SCAN_INTERVAL
from homeassistant.helpers.event import async_track_point_in_time
from ..common.event_objects import SetSchedulerEventObject, StartEventObject
from ..const import CONF_SCHEDULER
from homeassistant.core import CALLBACK_TYPE, HassJob, HomeAssistant
from ..common.component import Component


class SchedulerComponent(Component):
    Platform = CONF_SCHEDULER

    def __init__(self, hass: HomeAssistant, config: dict) -> None:
        super().__init__(hass, config)
        self._unsub_refresh: CALLBACK_TYPE = None
        self._next_run = None
        self._job = HassJob(self._invoke_start_listeners)
        self._schedule_refresh()

    def _invoke_set_listeners(self, nextRun: datetime) -> None:
        eventObj = SetSchedulerEventObject(self)
        eventObj.NextRun = nextRun
        super().invoke_listeners(eventObj)

    async def _invoke_start_listeners(self, args) -> None:
        eventObj = StartEventObject(self)
        super().invoke_listeners(eventObj)

    def enabled_changed(self):
        if self._is_enabled:
            self._schedule_refresh()
        else:
            self._schedule_off()
        
    def _schedule_off(self):
        if self._unsub_refresh:
            self._unsub_refresh()
            self._unsub_refresh = None
        self._next_run = None
        self._invoke_set_listeners(None)

    def _schedule_refresh(self):
        self._schedule_off()
        if not self._is_enabled:
            return

        scan_interval: timedelta = self._config[CONF_SCAN_INTERVAL]
        self._next_run = datetime.now().replace(microsecond=0) + scan_interval
        self._unsub_refresh = async_track_point_in_time(
            self._hass, self._job, self._next_run,
        )
        self._invoke_set_listeners(self._next_run)

