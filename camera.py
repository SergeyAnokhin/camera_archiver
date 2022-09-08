from io import BytesIO
from homeassistant.components.camera import Camera
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_NAME
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.update_coordinator import (
    CoordinatorEntity,
    DataUpdateCoordinator,
)

from .common.memory_storage import MemoryStorage
from .common.transfer_state import EventType
from .const import ATTR_ENABLE, CONF_CAMERA, DOMAIN, ICON_CAMERA

# async def async_setup_entry(hass: HomeAssistant, config: ConfigEntry, async_add_entities, discovery_info=None):
async def async_setup_platform(
    hass: HomeAssistant, config: ConfigEntry, add_entities, discovery_info=None
):

    # entity_config = discovery_info
    # instName = entity_config[CONF_NAME]
    # storage = MemoryStorage(hass, instName)

    cameras = []
    # for comp_id, coords_by_state in storage.coordinators.items():
    #     id: TransferComponentId = comp_id
    #     if id.TransferType == TransferType.TO and id.Platform == CONF_CAMERA:
    #         coordinator = coords_by_state[EventType.SAVE]
    #         cameras.append(ToCamera(hass, id, coordinator))

    add_entities(cameras)


class ToCamera(CoordinatorEntity, Camera):
    """Representation of a MQTT camera."""

    def __init__(
        self,
        hass: HomeAssistant,
        # id,
        coordinator: DataUpdateCoordinator,
    ):
        """Initialize the MQTT Camera."""
        CoordinatorEntity.__init__(self, coordinator)
        Camera.__init__(self)

        # self._comp_id = id
        self._attr_name = f"{id.Entity}: {id.Name} last file"
        self._attr_icon = ICON_CAMERA
        self._last_image: bytes = None
        self._state = None
        self._hass = hass
        self._storage = MemoryStorage(hass, id.Entity)

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
        super()._handle_coordinator_update()

    def camera_image(self, width: int = None, height: int = None) -> bytes:
        self._last_image = self._storage.get_file(self._comp_id.id)
        bytes = self._last_image
        return bytes

    # async def async_camera_image(
    #     self, width: int = None, height: int = None
    # ) -> bytes:
    #     """Return image response."""
    #     """Ignore width and height: camera component will resize it."""
    #     self._last_image = self._storage.get_file(self._comp_id.id)
    #     bytes = self._last_image.getvalue()
    #     return bytes

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
