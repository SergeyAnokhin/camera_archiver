from datetime import datetime
import os, logging

from ..common.transfer_component import TransferComponent
from ..common.transfer_state import TransferState
from ..const import CONF_FROM, CONF_FTP, CONF_PATH

from .FtpConn import FtpConn
from .ftp_file_info import FtpFileInfo

_LOGGER = logging.getLogger(__name__)

class FtpTransfer(TransferComponent):
    def __init__(self, config: dict):
        self._config = config

    def state(self) -> TransferState:
        cftp = self._config
        state = TransferState()

        with FtpConn(cftp) as srcFtp:
            srcFtp.cd(cftp[CONF_PATH])
            fs_items = srcFtp.GetFtpItems()
            for fs in fs_items:
                subitems = srcFtp.GetFtpItems(fs.name)

                for f in subitems:
                    state.add(f.relname(), f.size())
                    # _LOGGER.debug(f"Found: {f}")

        _LOGGER.info(f"🆗 Files check done. Found: {state}")
        state.stop()
        return state

    def Copy(self, max=100):
        cftp = self.config

        with FtpConn(cftp) as srcFtp:
            srcFtp.cd(cftp[CONF_PATH])
            fs_items = srcFtp.GetFtpItems()
            files_counter = 0
            files_copied = 0
            for fs in fs_items:
                subitems = srcFtp.GetFtpItems(fs.name)

                for f in subitems:
                    files_counter = files_counter + 1
                    if files_counter > max:
                        continue

                    files_copied = files_copied + 1
                    stat = TransferState()
                    stat.add(f)
                    localfile = self.localFileStorage(f)

                    srcFtp.Download(f, localfile)
                    # dstFtpFile = self.Upload(localfile, self.datetime(f))

                    # stat.info["path"] = dstFtpFile
                    # stat.info["path_source"] = f.fullname
                    # stat.info["value"] = os.path.getsize(localfile)
                    self.OnFileTransferCall(stat)

        _LOGGER.info(f"🆗 Files transferring done. Copied: {files_copied} / {files_counter}")


    def localFileStorage(self, file: FtpFileInfo) -> str:
        return f'{self.config["local_storage"]}/camera.{self.config["camera"]["name"]}.{file.extension}'

    def Upload(self, localfile: str, dt: datetime):
        cto = self.config["to"]
        fullpath = f"{cto['ftp']['path']}/{dt.strftime(cto['datetime_pattern'])}"

        with FtpConn(cto["ftp"]) as ftp:
            ftp.Upload(localfile, fullpath)

        return fullpath
