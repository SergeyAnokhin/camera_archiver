
import json

from .FtpItem import FtpItem

class FtpTransferStat:
    STR_TOTAL = "Total"

    def __init__(self, file: FtpItem, config: dict):
        self.info = {
            "ext": file.extension,
            "camera": config["camera"]["name"],
        }
        self.file = file

    def __str__(self):
         return f'🗄️🔼 File uploaded ==> {self.info["path"]} ({self.info["value"]}b) \n {json.dumps(self.info, indent=3)}'