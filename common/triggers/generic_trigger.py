from abc import abstractmethod


class GenericTrigger:
    platform = None

    def __init__(self, config) -> None:
        self._config = config

    @abstractmethod
    def enable(self, is_enable: bool):
        pass