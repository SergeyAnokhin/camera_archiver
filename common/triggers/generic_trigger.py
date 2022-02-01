from abc import abstractmethod

from homeassistant.core import CALLBACK_TYPE


class GenericTrigger:
    platform = None

    def __init__(self, config) -> None:
        self._config = config
        self._listeners = []

    @abstractmethod
    def enable(self, is_enable: bool):
        pass

    def add_listener(self, callback: CALLBACK_TYPE) -> None:
        """Listen for data updates."""
        self._listeners.append(callback)

    def _invoke_read_listeners(self, file: IFileInfo, content) -> bool:
        results: list = []
        for callback in self._listeners[EventType.READ]:
            results.append(callback(self._id, file, content))

        return True in results # check if any compinent recieved and saved file
