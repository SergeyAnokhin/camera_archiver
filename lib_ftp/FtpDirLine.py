from datetime import datetime, timedelta
from dateutil import parser

class FtpDirLine:

    def __init__(self, dirline: str):
        # -rw-r--r-- 1 user group           4467 Mar 27  2018  file1.zip
        # -rw-r--r-- 1 user group         124529 Jun 18 15: 31 file2.zip
        super().__init__()
        self.parts = dirline.split(maxsplit=9)
        self._name = self.parts[-1]
        self._time_str = self.parts[5] + " " + self.parts[6] + " " + self.parts[7]
        self.is_dir = self.parts[0].startswith('d')
        self.is_file = self.parts[0].startswith('-')
        self._size = int(self.parts[4])
    
    @property
    def size(self) -> int:
        return self._size

    @property
    def name(self) -> str:
        return self._name

    @property
    def modif_datetime_source(self) -> str:
        return self._time_str

    @property
    def modif_datetime(self) -> datetime:
        # https://stackoverflow.com/questions/29026709/how-to-get-ftp-files-modify-time-using-python-ftplib
        result = parser.parse(self._time_str)
        result -= timedelta(hours=1)
        if result > datetime.now():
            ''' wrong year ''' 
            result = result.replace(year=result.year-1)
        return result