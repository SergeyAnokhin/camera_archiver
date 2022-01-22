import logging

from homeassistant.components.switch import DEVICE_CLASS_SWITCH
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_NAME, STATE_OFF, STATE_ON
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import ToggleEntity
from homeassistant.helpers.restore_state import RestoreEntity
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

from .const import CONF_ENABLE, DOMAIN
from .common.transfer_builder import TransferBuilder

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass: HomeAssistant, config: ConfigEntry, async_add_entities):
    pass

async def async_setup_platform(hass: HomeAssistant, config: ConfigEntry, add_entities, discovery_info=None):
    config = discovery_info
    instName = config[CONF_NAME]
    manager: TransferBuilder = hass.data[DOMAIN][instName]
    coordinator = manager.coordinator

    add_entities([
        CameraArchiverEnabler(coordinator, config),
    ])

class CameraArchiverEnabler(RestoreEntity, ToggleEntity):
    """Representation of a Yi Camera Switch."""

    def __init__(self, coordinator: DataUpdateCoordinator, config):
        self._attr_state = None
        self._attr_is_on = False
        self.coordinator: DataUpdateCoordinator = coordinator
        self._device_name = config[CONF_NAME]
        self._attr_name = self._device_name + " Enabler"
        self._attr_available = True
        self._attr_device_class = DEVICE_CLASS_SWITCH


    async def async_turn_on(self, **kwargs):
        """Turn the light on."""
        self._attr_state = STATE_ON

    async def async_turn_off(self, **kwargs):
        """Turn the entity off."""
        self._attr_state = STATE_OFF

    async def async_update(self, **kwargs):
        self._attr_is_on = self._attr_state == STATE_ON
        # self.schedule_update_ha_state()
        self.coordinator.data[CONF_ENABLE] = self._attr_is_on
        if self.coordinator.update_method: # check if already initialized
            await self.coordinator.async_request_refresh()

    async def async_added_to_hass(self):
        last_state = await self.async_get_last_state()
        _LOGGER.debug(f"#{self._attr_name}# call async_get_last_state STATE={self._attr_state}")
        if last_state and last_state.state:
            self._attr_state = last_state.state
            _LOGGER.debug(f"#{self._attr_name}# NEW_STATE={self._attr_state}")
            await self.async_update()

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

