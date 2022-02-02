from homeassistant.core import HomeAssistant, ServiceCall

from ..common.component import Component
from ..const import CONF_SERVICE, DOMAIN, SERVICE_FIELD_COMPONENT, SERVICE_RUN


class ServiceComponent(Component):
    Platform = CONF_SERVICE

    def __init__(self, hass: HomeAssistant, config: dict) -> None:
        super().__init__(hass, config)
        self.subscribe_to_service()

    def subscribe_to_service(self) -> None:
        async def _service_run(call: ServiceCall) -> None:
            self._logger.info("service camera archive call")
            data = dict(call.data)
            if self._id != data[SERVICE_FIELD_COMPONENT]:
                return
            self.invoke_listeners()

        self._hass.services.async_register(DOMAIN, SERVICE_RUN, _service_run)

