import os, logging

from ftplib import FTP
from .FtpItem import FtpItem

_LOGGER = logging.getLogger(__name__)

class FtpConn:

    def __init__(self, config: dict) -> None:
        self.config = config
        self.host = config["host"]
        self.user = config["user"]
        self.passwd = config["password"]

    def __enter__(self):
        self.ftp = FTP(self.host, self.user, self.passwd)
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.ftp.quit()

    def cd(self, fullpath: str, withDirectoryCreation = False):
        if withDirectoryCreation:
            parts = fullpath.split('/')
            self.ftp.cwd('/')
            for p in parts[1:-1]:
                if not self.directory_exists(p):
                    self.ftp.mkd(p)
                    print(f"➕📁 Directory created: {p}")
                self.ftp.cwd(p)
        else:
            self.ftp.cwd(fullpath)

    def GetFtpItems(self, dir: str = None) -> list[FtpItem]:
        filelist = []
        newpath = self.config["path"]
        current_path = self.ftp.pwd()
        if dir:
            newpath = self.config["path"] + "/" + dir
            self.ftp.dir(dir, filelist.append)
        else:
            self.ftp.dir(filelist.append)
        return [FtpItem(self.config, newpath, x) for x in filelist]

    def directory_exists(self, directory: str) -> bool:
        filelist = self.GetFtpItems()
        for f in filelist:
            if f.name == directory and f.is_dir:
                return True
        return False

    def Upload(self, localfile: str, fullFtpPath: str):
        self.cd(fullFtpPath, withDirectoryCreation=True)
        filename = fullFtpPath.split('/')[-1]
        file = open(localfile, 'rb')
        self.ftp.storbinary('STOR ' + filename, file)

    def Download(self, fileFtp: FtpItem, localfilename: str):
        with open(localfilename, 'wb') as localfile:
            self.ftp.retrbinary(f'RETR {fileFtp.fullname}', localfile.write)
        filesize = os.path.getsize(localfilename)
        _LOGGER.debug(f'🗄️⏬ File downloaded : {fileFtp.fullname} ==> {localfilename} ({filesize}b)')

