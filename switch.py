import logging
from abc import abstractmethod
from typing import Dict

from homeassistant.components.switch import DEVICE_CLASS_SWITCH
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_NAME, STATE_OFF, STATE_ON
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import ToggleEntity
from homeassistant.helpers.restore_state import RestoreEntity
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

from .common.memory_storage import MemoryStorage
from .common.transfer_component_id import TransferComponentId, TransferType
from .common.transfer_state import EventType
from .const import ATTR_ENABLE, ATTR_HASS_STORAGE_COORDINATORS, DOMAIN

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass: HomeAssistant, config: ConfigEntry, async_add_entities):
    pass


async def async_setup_platform(hass: HomeAssistant, config: ConfigEntry, add_entities, discovery_info=None):
    entity_config = discovery_info
    instName = entity_config[CONF_NAME]
    storage = MemoryStorage(hass, instName)
    
    switches = []
    coordinators_list = []

    for comp_id, coords_by_state in storage.coordinators.items():
        id: TransferComponentId = comp_id
        if id.TransferType == TransferType.FROM:
            coordinator = coords_by_state[EventType.REPOSITORY]
            switches.append(ComponentEnabler(id, EventType.REPOSITORY, coordinator))
            coordinators_list.append(coordinator)
            coordinator = coords_by_state[EventType.READ]
            switches.append(ComponentEnabler(id, EventType.READ, coordinator))
            coordinators_list.append(coordinator)
        elif id.TransferType == TransferType.TO:
            coordinator = coords_by_state[EventType.SAVE]
            switches.append(ComponentEnabler(id, EventType.SAVE, coordinator))
            coordinators_list.append(coordinator)

    # switches.append(CameraArchiverEnabler(entity_config, coordinators_list))
    add_entities(switches)


class GenericEnabler(RestoreEntity, ToggleEntity):

    def __init__(self):
        self._attr_state = None
        self._attr_is_on = False
        self._attr_available = True
        self._attr_device_class = DEVICE_CLASS_SWITCH

    async def async_turn_on(self, **kwargs):
        """Turn the light on."""
        self._attr_state = STATE_ON

    async def async_turn_off(self, **kwargs):
        """Turn the entity off."""
        self._attr_state = STATE_OFF

    async def async_added_to_hass(self):
        last_state = await self.async_get_last_state()
        if last_state and last_state.state:
            self._attr_state = last_state.state
            _LOGGER.debug(f"::{self._attr_name} STATE: '{self._attr_state.upper()}'")
            await self.async_update()

    @abstractmethod
    async def async_update(self, **kwargs):
        NotImplementedError()


class ComponentEnabler(GenericEnabler):

    def __init__(self, comp_id: TransferComponentId, stateType: EventType, coordinator: DataUpdateCoordinator):
        super().__init__()
        self.coordinator: DataUpdateCoordinator = coordinator
        self._device_name = f"{comp_id.Entity}: {comp_id.Name} {stateType.value}"
        self._attr_name = self._device_name

    async def async_update(self, **kwargs):
        self._attr_is_on = self._attr_state == STATE_ON
        # self.schedule_update_ha_state()
        self.coordinator.data[ATTR_ENABLE] = self._attr_is_on
        self.coordinator.async_set_updated_data(self.coordinator.data)


class CameraArchiverEnabler(GenericEnabler):
    """Representation of a Yi Camera Switch."""

    def __init__(self, config: dict, coordinators: list[DataUpdateCoordinator]):
        super().__init__()
        self.coordinators: list[DataUpdateCoordinator] = coordinators
        self._device_name = config[CONF_NAME]
        self._attr_name = self._device_name + " Enabler"

    async def async_update(self, **kwargs):
        self._attr_is_on = self._attr_state == STATE_ON
        # self.schedule_update_ha_state()
        for coord in self.coordinators:
            coord.data[ATTR_ENABLE] = self._attr_is_on
            if coord.update_method:  # check if already initialized
                await coord.async_request_refresh()

    # @property
    # def should_poll(self) -> bool:
    #     """No need to poll. Coordinator notifies entity of updates."""
    #     return False

    # @property
    # def device_info(self) -> DeviceInfo:
    #     """Device information."""
    #     return DeviceInfo(
    #         identifiers={
    #             # Unique identifiers within the domain
    #             (DOMAIN, self.unique_id)
    #         },
    #         manufacturer="TODO",
    #         model="TODO",
    #         name=self.name,
    #         sw_version="TODO",
    #     )
