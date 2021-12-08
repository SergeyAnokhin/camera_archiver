from ..TransferState import TransferState
from ..const import CONF_DIRECTORY, CONF_FROM, CONF_PATH
import os
import logging

_LOGGER = logging.getLogger(__name__)

class DirectoryTransfer:
    def __init__(self, config: dict):
        self._config = config

    def state(self) -> TransferState:
        path = self._config[CONF_PATH]
        return self.list_files(path)

    def list_files(self, startpath) -> TransferState:
        _LOGGER.debug(f"Stat from [{startpath}]: START")
        state = TransferState()
        for root, dirs, files in os.walk(startpath):
            # os.path.basename(root)
            for f in files:
                rel_path = root.replace(startpath, '').lstrip('/').lstrip('\\')  # .count(os.sep)
                full_path = f"{root}/{f}"
                size = os.path.getsize(full_path)

                state.add(rel_path, size)

        _LOGGER.debug(f"Stat from [{startpath}]: END, {state}")
        return state
