from datetime import datetime, timedelta

from homeassistant.components.timer import EVENT_TIMER_FINISHED, Timer
from homeassistant.const import ATTR_ENTITY_ID, CONF_SCAN_INTERVAL
from homeassistant.core import CALLBACK_TYPE, HassJob, HomeAssistant, callback, Event
from homeassistant.helpers.event import async_track_point_in_time

from ..common.component import Component
from ..common.event_objects import SetSchedulerEventObject, StartEventObject
from ..common.helper import register_entity, run_async, start_after_ha_started
from ..const import CONF_SCHEDULER


class SchedulerComponent(Component):
    Platform = CONF_SCHEDULER

    def __init__(self, hass: HomeAssistant, config: dict) -> None:
        super().__init__(hass, config)
        # self._unsub_refresh: CALLBACK_TYPE = None
        # self._next_run = None
        # self._job = HassJob(self._invoke_start_listeners)
        # start_after_ha_started(self._hass, self._schedule_refresh)
        self.create_timer()

    def create_timer(self):
        self._timer = Timer(
            {
                "id": "ca_timer",
                "name": "ca_timer",
                "icon": "mdi:youtube",
                "duration": "00:00:10",
            }
        )
        self._timer.entity_id = "timer.ca_timer"

        async def async_create_timer():
            await register_entity(self._hass, "timer", self._timer)

        run_async(async_create_timer(), self._hass)

        async def _loaded_event(event: Event) -> None:
            """Call the callback if we loaded the expected component."""
            if event.data[ATTR_ENTITY_ID] == self._timer.entity_id:
                pass

        # hass.bus.async_listen_once(EVENT_HOMEASSISTANT_STARTED, lambda *_: callback())
        self._hass.bus.listen(EVENT_TIMER_FINISHED, _loaded_event)

    def _invoke_set_listeners(self, next_run=None) -> None:
        eventObj = SetSchedulerEventObject(self)
        eventObj.NextRun = next_run if next_run else self._next_run
        super().invoke_listeners(eventObj)

    @callback
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
        # if self._unsub_refresh:
        #     self._unsub_refresh()
        #     self._unsub_refresh = None
        # self._next_run = None
        # self._invoke_set_listeners(None)
        async def cancel():
            self._timer.async_cancel()

        run_async(cancel(), self._hass)

    @callback
    def _schedule_refresh(self):
        async def start():
            await self._timer.async_start()

        run_async(start(), self._hass)

        # self._schedule_off()
        # if not self._is_enabled:
        #     return

        # scan_interval: timedelta = self._config[CONF_SCAN_INTERVAL]
        # next_run = self._next_run = (
        #     datetime.now().replace(microsecond=0) + scan_interval
        # )
        # self._logger.debug(f"Set next run @ {self._next_run.strftime('%H:%M:%S')}")
        # self._unsub_refresh = async_track_point_in_time(
        #     self._hass,
        #     self._invoke_start_listeners,
        #     self._next_run,
        # )

        # self._invoke_set_listeners(next_run)
