from homeassistant.components.timer import EVENT_TIMER_FINISHED, Timer
from homeassistant.const import ATTR_ENTITY_ID
from homeassistant.core import HomeAssistant, callback, Event

from ..common.component import Component
from ..common.event_objects import (
    SetSchedulerEventObject,
    StartEventObject,
    EventObject,
)
from ..common.helper import register_entity, run_async
from ..const import CONF_SCHEDULER


class SchedulerComponent(Component):
    Platform = CONF_SCHEDULER

    def __init__(self, hass: HomeAssistant, config: dict) -> None:
        super().__init__(hass, config)
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
                self._logger.debug(f"Finished timer: ⏹ ⏱ {self._timer.entity_id}")
                if event.event_type == "timer.finished":
                    if self._is_enabled:
                        self._schedule_refresh()
                        evt = EventObject(self)
                        self.invoke_listeners(evt)

        # hass.bus.async_listen_once(EVENT_HOMEASSISTANT_STARTED, lambda *_: callback())
        self._hass.bus.async_listen(EVENT_TIMER_FINISHED, _loaded_event)

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
        def cancel():
            self._logger.debug(f"Cancel timer: ⛔ ⏱ {self._timer.entity_id}")
            self._timer.async_cancel()

        cancel()

        # run_async(cancel(), self._hass)

    @callback
    def _schedule_refresh(self):
        def start():
            self._logger.debug(f"Start timer: ⏩ ⏱ {self._timer.entity_id}")
            self._timer.async_start()

        start()

        # run_async(start(), self._hass)
