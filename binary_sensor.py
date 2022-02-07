# from typing import Dict

# from homeassistant.components.binary_sensor import BinarySensorEntity
# from homeassistant.config_entries import ConfigEntry
# from homeassistant.const import CONF_NAME
# from homeassistant.core import HomeAssistant
# from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

# from .common.transfer_component_id import TransferComponentId, TransferType
# from .common.transfer_state import EventType
# from .const import ATTR_HASS_STORAGE_COORDINATORS, DOMAIN


# async def async_setup_platform(hass: HomeAssistant, config: ConfigEntry, add_entities, discovery_info=None):
#     entity_config = discovery_info
#     instName = entity_config[CONF_NAME]
#     coordinators: Dict[TransferComponentId: Dict[EventType: DataUpdateCoordinator]] = hass.data[DOMAIN][instName][ATTR_HASS_STORAGE_COORDINATORS]

#     switches = []
#     coordinators_list = []

#     for comp_id, coords_by_state in coordinators.items():
#         id: TransferComponentId = comp_id
#         if id.TransferType == TransferType.FROM:
#             coordinator = coords_by_state[EventType.REPOSITORY]
#             switches.append(ActivityBinarySensor(id, EventType.REPOSITORY, coordinator))
#             coordinators_list.append(coordinator)
#             coordinator = coords_by_state[EventType.READ]
#             switches.append(ActivityBinarySensor(id, EventType.READ, coordinator))
#             coordinators_list.append(coordinator)
#         elif id.TransferType == TransferType.TO:
#             coordinator = coords_by_state[EventType.SAVE]
#             switches.append(ActivityBinarySensor(id, EventType.SAVE, coordinator))
#             coordinators_list.append(coordinator)

#     # switches.append(CameraArchiverEnabler(entity_config, coordinators_list))
#     add_entities(switches)

# class ActivityBinarySensor(BinarySensorEntity):
    
#     def __init__(self, config: dict) -> None:
#         super().__init__()
#         self._attr_name = config[CONF_NAME]
