from abc import abstractmethod
from homeassistant.core import CALLBACK_TYPE

from .event_objects import EventObject


class GenericObservable:
    def __init__(self) -> None:
        self._listeners = []
        self.id = None

    def add_listener(self, listener: CALLBACK_TYPE) -> None:
        """
        Add listeners to component. each listener will be call after data processing
        """
        self._listeners.append(listener)

    def invoke_listeners(self, event_object: EventObject) -> bool:
        """
        Call each listener after data processing
        """
        results: list = []
        for listener in self._listeners:
            result = listener(event_object)
            results.append(result)

        return False not in results  # check if any component recieved and saved file

    @abstractmethod
    def callback(self, event_object: EventObject) -> object:
        """
        Data processing
        """
