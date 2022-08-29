from datetime import datetime, timedelta

from homeassistant.const import CONF_SCAN_INTERVAL
from homeassistant.core import CALLBACK_TYPE, HassJob, HomeAssistant
from homeassistant.helpers.event import async_track_point_in_time

from ..common.component import Component
from ..common.event_objects import SetSchedulerEventObject, StartEventObject
from ..common.helper import start_after_ha_started
from ..const import CONF_SCHEDULER


class SchedulerComponent(Component):
    Platform = CONF_SCHEDULER

    def __init__(self, hass: HomeAssistant, config: dict) -> None:
        super().__init__(hass, config)
        self._unsub_refresh: CALLBACK_TYPE = None
        self._next_run = None
        self._job = HassJob(self._invoke_start_listeners)
        start_after_ha_started(self._hass, lambda: self._schedule_refresh())

    def _invoke_set_listeners(self, next_run=None) -> None:
        eventObj = SetSchedulerEventObject(self)
        eventObj.NextRun = next_run if next_run else self._next_run
        super().invoke_listeners(eventObj)

    def _invoke_start_listeners(self, args) -> None:
        eventObj = StartEventObject(self)
        super().invoke_listeners(eventObj)
        self._schedule_refresh()

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
        next_run = self._next_run = (
            datetime.now().replace(microsecond=0) + scan_interval
        )
        self._logger.debug(f"Set next run @ {self._next_run.strftime('%H:%M:%S')}")
        self._unsub_refresh = async_track_point_in_time(
            self._hass,
            self._job,
            self._next_run,
        )

        self._invoke_set_listeners(next_run)
