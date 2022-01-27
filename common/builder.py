from homeassistant.core import HomeAssistant


class Builder:

    def __init__(self, hass: HomeAssistant, archiver_config: dict, config: dict) -> None:
        self._hass = hass
        self._config = config

    def build_pipeline(self):
        pass