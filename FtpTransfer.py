from datetime import datetime
import os

from .FtpConn import FtpConn
from .FtpItem import FtpItem
from .FtpTransferStat import FtpTransferStat

class FtpTransfer:
    def __init__(self, config: dict):
        self.config = config

    def OnFileTransferCallback(self, callback):
        self.OnFileTransferCall = callback

    def Copy(self, max=100):
        cfrom = self.config["from"]

        with FtpConn(self.config["from"]["ftp"]) as srcFtp:
            srcFtp.cd(cfrom["ftp"]["path"])
            fs_items = srcFtp.GetFtpItems()
            files_counter = 0
            files_copied = 0
            for fs in fs_items:
                subitems = srcFtp.GetFtpItems(fs.name)
                #print(fs, f" ({len(subitems)} file)")

                for f in subitems:
                    # print(" / ", f, f" {files_counter}")
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

        # with FTP(host=cfrom["ftp"]["host"], user=cfrom["ftp"]["user"], passwd=cfrom["ftp"]["password"]) as srcFTP:
        #     srcFTP.cwd(cfrom["ftp"]["path"])
        #     fs_items = self.GetFtpItems(srcFTP)
        #     max = max if max != None else max(fs_items)
        #     for f in fs_items[0:max]:
        #         fs = FtpItem(cfrom, cfrom["ftp"]["path"], f)
        #         print(fs)
        #         subitems = fs.subitems(srcFTP)
        #         [print(x) for x in subitems]

        #         for f in subitems:
        #             f.download(self.localFileStorage(f), srcFTP)
        #             self.Upload(f, f.datetime())

        #     srcFTP.quit()
        print(f"🆗 Files transferring done. Copied: {files_copied} / {files_counter}")

    def datetime(self, item: FtpItem):
        #p = re.compile(".*(?P<year>\d{4})Y(?P<month>\d\d)M(?P<day>\d\d)D(?P<hour>\d\d)H/E1(?P<min>\d\d)M(?P<sec>\d\d)S(?P<msec>\d\d).*")
        #m = p.match(self.fullname())
        #d = m.groupdict()
        cfrom = self.config["from"]
        pattern = f'{cfrom["ftp"]["path"]}/{cfrom["datetime_parser"]}'
        try:
            return datetime.strptime(item.fullname, pattern)
        except Exception as e:
            print(f"❗ Can't parse datetime from: '{item.fullname}' pattern: '{pattern}' ❗ \n {e}")
    
    def localFileStorage(self, file: FtpItem) -> str:
        return f'{self.config["local_storage"]}/camera.{self.config["camera"]["name"]}.{file.extension}'

    def Upload(self, localfile: str, dt: datetime):
        cto = self.config["to"]
        fullpath = f"{cto['ftp']['path']}/{dt.strftime(cto['datetime_pattern'])}"

        with FtpConn(cto["ftp"]) as ftp:
            ftp.Upload(localfile, fullpath)

        return fullpath