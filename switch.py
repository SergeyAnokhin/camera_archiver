from homeassistant.components.switch import DEVICE_CLASS_SWITCH
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import ATTR_NAME, STATE_OFF, STATE_ON
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import ToggleEntity
from homeassistant.helpers.restore_state import RestoreEntity

from .common.event_objects import SwitchEventObject
from .common.helper import getLogger
from .common.types import SensorConnector
from .const import ATTR_PIPELINE_PATH, ATTR_SENSORS

_PLATFORM = "switch"

class GenericEnabler(RestoreEntity, ToggleEntity):

    def __init__(self, connector: SensorConnector):
        self.connector = connector
        self._attr_extra_state_attributes = {}
        self._attr_state = None
        self._attr_is_on = False
        self._attr_available = True
        self._attr_device_class = DEVICE_CLASS_SWITCH
        self._device_name = f"{connector.id}"
        self._attr_name = self._device_name
        self.set_attr(ATTR_PIPELINE_PATH, connector.pipeline_path)
        self._logger = getLogger(__name__, connector.pipeline_id, connector.id)

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
            self._logger.debug(f"Restored state: '{self._attr_state.upper()}'")
            await self.async_update(force_update=True)

    def set_attr(self, key: str, value) -> None:
        if value:
            self._attr_extra_state_attributes[key] = value
        elif key in self._attr_extra_state_attributes:
            del(self._attr_extra_state_attributes[key])

    async def async_update(self, force_update = False):
        curr_state = self._attr_state == STATE_ON
        if curr_state != self._attr_is_on or force_update:
            self._attr_is_on = curr_state
            self._logger.debug(f"Switch state to '{self._attr_is_on}'")
            # self.schedule_update_ha_state()
            switchEO = SwitchEventObject(self)
            switchEO.enable = self._attr_is_on
            self.connector.invoke_listeners(switchEO)

class ComponentEnabler(GenericEnabler):

    def __init__(self, connector: SensorConnector):
        super().__init__(connector)

_SWITCH_TYPES = {
    "": ComponentEnabler,
}


async def async_setup_platform(hass: HomeAssistant, config: ConfigEntry, add_entities, discovery_info=None):
    sensors_desc: list[SensorConnector] = discovery_info[ATTR_SENSORS]
    instName = discovery_info[ATTR_NAME]
    logger = getLogger(__name__, instName)

    switches = []
    for desc in sensors_desc:
        if desc.platform.value != _PLATFORM:
            continue

        ctor = _SWITCH_TYPES[desc.type]
        switch: GenericEnabler = ctor(desc)
        switches.append(switch)
        logger.debug(f"Add switch -> path: '{desc.pipeline_path}'; name: '{switch.name}'")

    add_entities(switches)

#     storage = MemoryStorage(hass, instName)
    
#     switches = []
#     coordinators_list = []

#     for comp_id, coords_by_state in storage.coordinators.items():
#         id: TransferComponentId = comp_id
#         if id.TransferType == TransferType.FROM:
#             coordinator = coords_by_state[EventType.REPOSITORY]
#             switches.append(ComponentEnabler(id, EventType.REPOSITORY, coordinator))
#             coordinators_list.append(coordinator)
#             coordinator = coords_by_state[EventType.READ]
#             switches.append(ComponentEnabler(id, EventType.READ, coordinator))
#             coordinators_list.append(coordinator)
#         elif id.TransferType == TransferType.TO:
#             coordinator = coords_by_state[EventType.SAVE]
#             switches.append(ComponentEnabler(id, EventType.SAVE, coordinator))
#             coordinators_list.append(coordinator)

#     # switches.append(CameraArchiverEnabler(entity_config, coordinators_list))
#     add_entities(switches)


# class CameraArchiverEnabler(GenericEnabler):
#     """Representation of a Yi Camera Switch."""

#     def __init__(self, config: dict, coordinators: list[DataUpdateCoordinator]):
#         super().__init__()
#         self.coordinators: list[DataUpdateCoordinator] = coordinators
#         self._device_name = config[CONF_NAME]
#         self._attr_name = self._device_name + " Enabler"

#     async def async_update(self, **kwargs):
#         self._attr_is_on = self._attr_state == STATE_ON
#         # self.schedule_update_ha_state()
#         for coord in self.coordinators:
#             coord.data[ATTR_ENABLE] = self._attr_is_on
#             if coord.update_method:  # check if already initialized
#                 await coord.async_request_refresh()

#     # @property
#     # def should_poll(self) -> bool:
#     #     """No need to poll. Coordinator notifies entity of updates."""
#     #     return False

#     # @property
#     # def device_info(self) -> DeviceInfo:
#     #     """Device information."""
#     #     return DeviceInfo(
#     #         identifiers={
#     #             # Unique identifiers within the domain
#     #             (DOMAIN, self.unique_id)
#     #         },
#     #         manufacturer="TODO",
#     #         model="TODO",
#     #         name=self.name,
#     #         sw_version="TODO",
#     #     )
