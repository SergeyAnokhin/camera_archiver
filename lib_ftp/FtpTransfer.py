from datetime import datetime
import os, logging
from ..TransferState import TransferState
from ..const import CONF_FROM, CONF_FTP, CONF_PATH

from .FtpConn import FtpConn
from .FtpItem import FtpItem
from .FtpTransferStat import FtpTransferStat

_LOGGER = logging.getLogger(__name__)

class FtpTransfer:
    def __init__(self, config: dict):
        self.config = config

    def OnFileTransferCallback(self, callback):
        self.OnFileTransferCall = callback

    def state(self) -> TransferState:
        cfrom = self.config[CONF_FROM]
        state = TransferState()

        with FtpConn(cfrom[CONF_FTP]) as srcFtp:
            srcFtp.cd(cfrom[CONF_FTP][CONF_PATH])
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
        cfrom = self.config["from"]

        with FtpConn(self.config["from"]["ftp"]) as srcFtp:
            srcFtp.cd(cfrom["ftp"]["path"])
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
                    stat = FtpTransferStat(f, self.config)
                    localfile = self.localFileStorage(f)

                    srcFtp.Download(f, localfile)
                    dstFtpFile = self.Upload(localfile, self.datetime(f))

                    stat.info["path"] = dstFtpFile
                    stat.info["path_source"] = f.fullname
                    stat.info["value"] = os.path.getsize(localfile)
                    self.OnFileTransferCall(stat)

        _LOGGER.info(f"🆗 Files transferring done. Copied: {files_copied} / {files_counter}")

    def datetime(self, item: FtpItem):
        #p = re.compile(".*(?P<year>\d{4})Y(?P<month>\d\d)M(?P<day>\d\d)D(?P<hour>\d\d)H/E1(?P<min>\d\d)M(?P<sec>\d\d)S(?P<msec>\d\d).*")
        #m = p.match(self.fullname())
        #d = m.groupdict()
        cfrom = self.config["from"]
        pattern = f'{cfrom["ftp"]["path"]}/{cfrom["datetime_parser"]}'
        try:
            return datetime.strptime(item.fullname, pattern)
        except Exception as e:
            _LOGGER.warn(f"❗ Can't parse datetime from: '{item.fullname}' pattern: '{pattern}' ❗ \n {e}")
    
    def localFileStorage(self, file: FtpItem) -> str:
        return f'{self.config["local_storage"]}/camera.{self.config["camera"]["name"]}.{file.extension}'

    def Upload(self, localfile: str, dt: datetime):
        cto = self.config["to"]
        fullpath = f"{cto['ftp']['path']}/{dt.strftime(cto['datetime_pattern'])}"

        with FtpConn(cto["ftp"]) as ftp:
            ftp.Upload(localfile, fullpath)

        return fullpath
