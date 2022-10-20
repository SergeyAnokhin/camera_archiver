from ..common.helper import run_async, run_async_asyncio

from ..common.abstract.listeners_components import ListenersComponent
from ..const import CONF_SERVICE_CALLER


class ServiceCallerComponent(ListenersComponent):
    Platform = CONF_SERVICE_CALLER

    # def __init__(self, hass: HomeAssistant, config: dict) -> None:
    #     super().__init__(hass, config)

    async def async_call_service(self):
        await self._hass.services.async_call(
            "system_log",
            "write",
            {
                "message": "Message from ServiceCallerComponent",
                "logger": "CamArc",
                "level": "warning",
            },
            blocking=True,
        )

    def process_item(self, input_data) -> object:
        super().process_item(input_data)
        run_async_asyncio(self.async_call_service(), self._hass.loop)
