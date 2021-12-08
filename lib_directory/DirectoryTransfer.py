from ..TransferState import TransferState
from ..const import CONF_DIRECTORY, CONF_FROM, CONF_PATH
import os
import logging

_LOGGER = logging.getLogger(__name__)

class DirectoryTransfer:
    def __init__(self, config: dict):
        self.config = config

    def state(self) -> TransferState:
        cfrom = self.config[CONF_FROM]

        path = cfrom[CONF_DIRECTORY][CONF_PATH]

        return self.list_files(path)

    def list_files(self, startpath) -> TransferState:
        state = TransferState()
        for root, dirs, files in os.walk(startpath):
            # os.path.basename(root)
            for f in files:
                # rel_path = root.replace(startpath, '').trim('/').trim('\\') # .count(os.sep)
                full_path = f"{root}/{f}"
                size = os.path.getsize(full_path)

                state.add(full_path, size)

        return state
