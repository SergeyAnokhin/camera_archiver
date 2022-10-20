from typing import cast
from homeassistant.core import split_entity_id
from homeassistant.helpers.template import Template, render_complex
from ..common.helper import run_async_asyncio

from ..common.abstract.listeners_components import ListenersComponent
from ..const import CONF_DATA, CONF_SERVICE, CONF_SERVICE_CALLER


class ServiceCallerComponent(ListenersComponent):
    Platform = CONF_SERVICE_CALLER

    # def __init__(self, hass: HomeAssistant, config: dict) -> None:
    #     super().__init__(hass, config)

    async def async_call_service(self):
        data = {}
        domain_service = self._config[CONF_SERVICE]
        domain, service = split_entity_id(domain_service)
        data_template: Template = cast(Template, self._config[CONF_DATA])
        data_template.hass = self._hass

        cmplx = render_complex(self._config[CONF_DATA])

        newdata = data_template.async_render(parse_result=False)
        data.update(newdata)

        await self._hass.services.async_call(domain, service, data)

    def process_item(self, input_data) -> object:
        super().process_item(input_data)
        run_async_asyncio(self.async_call_service())
