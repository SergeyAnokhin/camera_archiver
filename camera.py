# custom_components\yi_hack\camera.py

from typing import Dict

from homeassistant.components.camera import Camera
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_NAME
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.update_coordinator import CoordinatorEntity, DataUpdateCoordinator

from .common.transfer_component_id import TransferComponentId, TransferType
from .common.transfer_state import StateType
from .const import CONF_CAMERA, DOMAIN, ICON_CAMERA


async def async_setup_entry(hass: HomeAssistant, config: ConfigEntry, async_add_entities, discovery_info=None):
    entity_config = discovery_info
    instName = entity_config[CONF_NAME]
    coordinators: Dict[TransferComponentId: Dict[StateType: DataUpdateCoordinator]] = hass.data[DOMAIN][instName]

    cameras = []
    for comp_id, coords_by_state in coordinators.items():
        id: TransferComponentId = comp_id
        if id.TransferType == TransferType.FROM:
            coordinator = coords_by_state[StateType.READ]
            
        if id.TransferType == TransferType.TO and comp_id.Platfrom == CONF_CAMERA:
            coordinator = coords_by_state[StateType.SAVE]
            cameras.append(ToCamera(id, coordinator))

    async_add_entities(cameras)

class ToCamera(CoordinatorEntity, Camera):
    """Representation of a MQTT camera."""

    def __init__(self, id: TransferComponentId, coordinator: DataUpdateCoordinator):
        """Initialize the MQTT Camera."""
        CoordinatorEntity.__init__(self, coordinator)
        Camera().__init__(self)

        self._comp_id = id
        self._attr_name = f"{id.Entity}: {id.Name} last file"
        self._attr_icon = ICON_CAMERA
        self._last_image = None
        self._state = None

    def update(self):
        """Return the state of the camera (privacy off = state on)."""
        # self._state = not get_privacy(self.hass, self._device_name)
        pass

    async def async_added_to_hass(self):
        """Subscribe to MQTT events."""
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

    @callback
    def _handle_coordinator_update(self):
        """Call when the coordinator has an update."""
        if self.enabled and not self.has_transfer_state:
            self.coordinator.data[ATTR_TRANSFER_STATE] = TransferState(self._stateType)

        state: TransferState = self.coordinator.data[ATTR_TRANSFER_STATE]
        self.set_attr(ATTR_ENABLE, self.available)
        if state:
            self.coordinator_updated(state)
        super()._handle_coordinator_update()

    def coordinator_updated(self, state: TransferState):
        self._attr_native_value = state.files_count
        self.set_attr(ATTR_SIZE_MB, state.files_size_mb)
        self.set_attr(ATTR_EXTENSIONS, state.files_ext)
        self.set_attr(ATTR_LAST_IMAGE, state.last_image)
        self.set_attr(ATTR_LAST_VIDEO, state.last_video)
        last_time = to_short_human_readable(state.last_datetime)
        self.set_attr(ATTR_LAST_DATETIME, last_time)
        last_time = to_human_readable(state.last_datetime)
        self.set_attr(ATTR_LAST_DATETIME_FULL, last_time)

    async def async_camera_image(
        self, width: int = None, height: int = None
    ) -> bytes:
        """Return image response."""
        """Ignore width and height: camera component will resize it."""
        return self._last_image

    @property
    def is_on(self):
        """Determine whether the camera is on."""
        return self._last_image is not None

    @property
    def device_info(self):
        """Return device specific attributes."""
        return {
            "name": self._device_name,
            "toto": "tata",
            "model": DOMAIN,
        }
