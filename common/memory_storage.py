from typing import Any

from homeassistant.core import HomeAssistant

from ..const import (ATTR_HASS_STORAGE_COORDINATORS, ATTR_HASS_STORAGE_FILES,
                     ATTR_HASS_STORAGE_SENSORS, DOMAIN)
from .types import SensorConnector


class MemoryStorage: 

    def __init__(self, hass: HomeAssistant, instName: str) -> None:
        self._hass = hass
        if not DOMAIN in self._hass.data:
            self._hass.data[DOMAIN] = {}
        if not instName in self._hass.data[DOMAIN]:
            self._hass.data[DOMAIN][instName] = {}
        if not ATTR_HASS_STORAGE_FILES in self._hass.data[DOMAIN][instName]:
            self._hass.data[DOMAIN][instName][ATTR_HASS_STORAGE_FILES] = {}
        if not ATTR_HASS_STORAGE_COORDINATORS in self._hass.data[DOMAIN][instName]:
            self._hass.data[DOMAIN][instName][ATTR_HASS_STORAGE_COORDINATORS] = {}
        self._name = instName

    @property
    def sensors(self) -> list[SensorConnector]:
        return self._hass.data[DOMAIN][self._name][ATTR_HASS_STORAGE_SENSORS]

    @sensors.setter
    def sensors(self, value: list[SensorConnector]) -> None:
        self._hass.data[DOMAIN][self._name][ATTR_HASS_STORAGE_SENSORS] = value

    @property
    def files(self) -> dict:
        return self._hass.data[DOMAIN][self._name][ATTR_HASS_STORAGE_FILES]

    def get_file(self, id) -> Any:
        return self.files[id]

    def has_file(self, id) -> bool:
        return id in self.files \
            and self.files[id] is not None

    def append_file(self, id, content) -> Any:
        self.files[id] = content
