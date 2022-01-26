from io import BytesIO
import os, logging

from ftplib import FTP

from ..const import CONF_USER
from .FtpDirLine import FtpDirLine

from homeassistant.const import CONF_HOST, CONF_PASSWORD, CONF_PATH

_LOGGER = logging.getLogger(__name__)

class FtpConn:

    def __init__(self, config: dict) -> None:
        self.config = config
        self.host = config[CONF_HOST]
        self.user = config[CONF_USER]
        self.passwd = config[CONF_PASSWORD]

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
                    print(f"Directory created: {p}")
                self.ftp.cwd(p)
        else:
            self.ftp.cwd(fullpath)

    def GetFtpDir(self, dir: str = None) -> list[str]:
        fileline: list[str] = []
        if dir:
            self.ftp.dir(dir, fileline.append)
        else:
            self.ftp.dir(fileline.append)
        return fileline

    def directory_exists(self, directory: str) -> bool:
        for line in self.GetFtpDir():
            ftpLine = FtpDirLine(line)
            if ftpLine.name == directory and ftpLine.is_dir:
                return True
        return False

    def Upload(self, localfile: str, fullFtpPath: str):
        self.cd(fullFtpPath, withDirectoryCreation=True)
        filename = fullFtpPath.split('/')[-1]
        file = open(localfile, 'rb')
        self.ftp.storbinary('STOR ' + filename, file)

    def Download(self, from_file: str, to_file: str) -> BytesIO:
        with open(to_file, 'wb') as localfile:
            self.ftp.retrbinary(f'RETR {from_file}', localfile.write)
        filesize = os.path.getsize(to_file)
        _LOGGER.debug(f'File downloaded : {from_file} ==> {to_file} ({filesize}b)')

    def Delete(self, filename: str):
        # self.ftp.delete(filename)
        return

    def DeleteDir(self, dirname: str):
        self.ftp.rmd(dirname)

    def UploadBytes(self, bytes: bytes, fullFtpPath: str):
        self.cd(fullFtpPath, withDirectoryCreation=True)
        filename = fullFtpPath.split('/')[-1]
        bytesIo = BytesIO(bytes)
        bytesIo.seek(0)
        self.ftp.storbinary(f'STOR {filename}', bytesIo)

    def DownloadBytes(self, fullname: str) -> bytes:
        buffer = BytesIO()
        self.ftp.retrbinary(f"RETR {fullname}", buffer.write)
        filesize = buffer.getbuffer().nbytes
        buffer.seek(0)
        _LOGGER.debug(f'File downloaded : [{fullname}] ==> [memory] ({filesize}b)')
        return buffer.getvalue()

