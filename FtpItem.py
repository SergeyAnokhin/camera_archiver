from ftplib import FTP

class FtpItem:
    
    def __init__(self, config: dict, path: str, dirline: str):
        self.parts = dirline.split()
        self.path = path
        self.ftp_config = config
        self.ftp_root = config["path"]
        self.name = self.parts[-1]
        self.fullname = f'{self.path}/{self.parts[-1]}'
        self.is_dir = self.parts[0].startswith('d')
        self.is_file = self.parts[0].startswith('-')
        self.icon = '📁' if self.is_dir else '🖼️'
        self.size = self.parts[4]
        self.extension = self.name.split('.')[-1]
    
    def relname(self):
        return self.fullname.lstrip(self.ftp_root).lstrip("/")

    def subitems(self, ftp: FTP):
        fs = []
        newpath = f'{self.path}/{self.name}'
        ftp.dir(self.name, lambda x: fs.append(FtpItem(self.ftp_config, newpath, x)))
        return fs
    
    def __str__(self):
         return f"{self.icon} {self.name}"