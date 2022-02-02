from homeassistant.core import CALLBACK_TYPE


class GenericObservable:

    def __init__(self) -> None:
        self._listeners = []

    def add_listener(self, update_callback: CALLBACK_TYPE) -> None:
        self._listeners.append(update_callback)

    def invoke_listeners(self, event_content) -> bool:
        results: list = []
        for callback in self._listeners:
            result = callback(event_content)
            results.append(result)

        return False not in results # check if any component recieved and saved file