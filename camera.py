from io import BytesIO
from homeassistant.components.camera import Camera
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_NAME
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.update_coordinator import (CoordinatorEntity,
                                                      DataUpdateCoordinator)

from .common.memory_storage import MemoryStorage
from .common.transfer_component_id import TransferComponentId, TransferType
from .common.transfer_state import StateType
from .const import (ATTR_ENABLE, CONF_CAMERA, DOMAIN, ICON_CAMERA)

# async def async_setup_entry(hass: HomeAssistant, config: ConfigEntry, async_add_entities, discovery_info=None):
async def async_setup_platform(hass: HomeAssistant, config: ConfigEntry, add_entities, discovery_info=None):

    entity_config = discovery_info
    instName = entity_config[CONF_NAME]
    storage = MemoryStorage(hass, instName)

    cameras = []
    for comp_id, coords_by_state in storage.coordinators.items():
        id: TransferComponentId = comp_id
        if id.TransferType == TransferType.TO and id.Platform == CONF_CAMERA:
            coordinator = coords_by_state[StateType.SAVE]
            cameras.append(ToCamera(hass, id, coordinator))

    add_entities(cameras)

class ToCamera(Camera):
    """Representation of a MQTT camera."""

    def __init__(self, hass: HomeAssistant, id: TransferComponentId, coordinator: DataUpdateCoordinator):
        """Initialize the MQTT Camera."""
        # CoordinatorEntity.__init__(self, coordinator)
        Camera.__init__(self)

        self.coordinator = coordinator
        self._comp_id = id
        self._attr_name = f"{id.Entity}: {id.Name} last file"
        self._attr_icon = ICON_CAMERA
        self._last_image: BytesIO = None
        self._state = None
        self._hass = hass
        self._storage = MemoryStorage(hass, id.Entity)

    def update(self):
        """Return the state of the camera (privacy off = state on)."""
        # self._state = not get_privacy(self.hass, self._device_name)
        pass

        # @callback
        # def message_received(msg):
        #     """Handle new MQTT messages."""
        #     data = msg.payload

        #     self._last_image = data

        # self._mqtt_subscription = await mqtt.async_subscribe(
        #     self.hass, self._state_topic, message_received, 1, None
        # )

    # async def async_will_remove_from_hass(self):
    #     """Unsubscribe from MQTT events."""
    #     if self._mqtt_subscription:
    #         self._mqtt_subscription()

    async def async_added_to_hass(self) -> None:
        """When entity is added to hass."""
        await super().async_added_to_hass()
        self.async_on_remove(
            self.coordinator.async_add_listener(self._handle_coordinator_update)
        )

    @property
    def enabled(self) -> bool:
        return self.coordinator.data[ATTR_ENABLE] and self.has_file

    @property
    def has_file(self) -> bool:
        return self._storage.has_file(self._comp_id.id)

    @callback
    def _handle_coordinator_update(self):
        """Call when the coordinator has an update."""
        if not self.enabled:
            return

        self._last_image = self._storage.get_file(self._comp_id.id)
        # super()._handle_coordinator_update()

    async def async_camera_image(
        self, width: int = None, height: int = None
    ) -> bytes:
        """Return image response."""
        """Ignore width and height: camera component will resize it."""
        bytes: BytesIO = self._storage.get_file(self._comp_id.id)
        #bytes.seek(0)
        return bytes.getvalue()
        

    @property
    def is_on(self):
        """Determine whether the camera is on."""
        return self._storage.has_file(self._comp_id.id)

    @property
    def device_info(self):
        """Return device specific attributes."""
        return {
            "name": self._device_name,
            "toto": "tata",
            "model": DOMAIN,
        }

    # @property
    # def available(self) -> bool:
    #     """Return if entity is available."""
    #     return False
