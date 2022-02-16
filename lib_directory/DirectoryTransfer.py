import os
from typing import Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from ..common.helper import local_ip, mkdir_by
from ..common.ifile_info import IFileInfo
from ..common.component import Component
from ..const import ATTR_SOURCE_HOST, ATTR_TARGET_HOST, CONF_DATETIME_PATTERN, CONF_DIRECTORY
from .file_info import FileInfo


class DirectoryTransfer(Component):
    Platform = CONF_DIRECTORY

    def __init__(self, hass: HomeAssistant, config: ConfigEntry):
        super().__init__(hass, config)

    def get_files(self, max=None) -> list[IFileInfo]:
        ''' OVERRIDE '''
        files: list[IFileInfo] = []
        for root, dirs, walk_files in os.walk(self._path):
            if self._clean_dirs and len(dirs) == len(walk_files) == 0 and root != self._path:
                self._logger.debug(f"Remove empty directory: {root}")
                os.rmdir(root)
            for walk_file in walk_files:
                file = FileInfo(f"{root}/{walk_file}")
                if self.validate_file(file):
                    files.append(file)
                if max and len(files) >= max:
                    break
            if max and len(files) >= max:
                break

        return files

    def file_read(self, file: IFileInfo) -> Any:
        ''' OVERRIDE '''
        file.metadata[ATTR_SOURCE_HOST] = local_ip()

        with open(file.fullname, 'rb') as infile:
            return infile.read()

    def file_delete(self, file: IFileInfo):
        ''' OVERRIDE '''
        os.remove(file.fullname)

    def file_save(self, file: IFileInfo, content) -> IFileInfo:
        ''' OVERRIDE '''
        if not content:
            raise Exception(f"Content is empty. Component: {self.id}. Pipeline path: {self.pipeline_path}")
        file.metadata[ATTR_TARGET_HOST] = local_ip()
        rel_path = file.datetime.strftime(self._config[CONF_DATETIME_PATTERN])
        filename = f"{self._path}/{rel_path}.{file.ext}"
        mkdir_by(filename)
        if isinstance(content, bytes): 
            with open(filename, 'wb') as outfile:
                outfile.write(content)
        else:
            raise Exception(f'Unknown content type to save: {type(content)}')

        return FileInfo(filename)

