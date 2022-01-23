import logging
from datetime import datetime
import mimetypes
from pathlib import Path
import socket

import pytz

mimetypes.init()

def getLogger(name: str, instance: str = "", component: str = "") -> logging.Logger:
    name = name.replace("custom_components.camera_archiver", "CamArc")
    instance = ('::' + instance) if instance else ""
    component = ('.' + component) if component else ""
    return logging.getLogger(f"{name}{instance}{component}")

def to_utc(dt: datetime) -> datetime:
    #local_dt = self.local.localize(dt)
    return dt.astimezone(pytz.utc)

def to_str_timestamp(dt: datetime) -> str:
    return dt.strftime('%Y-%m-%dT%H:%M:%S.000Z')

def to_human_readable(dt: datetime) -> str:
    if not dt:
        return
    return dt.strftime('%d.%m.%Y %H:%M:%S')

def to_short_human_readable(dt: datetime) -> str:
    if not dt:
        return
    now = datetime.now()
    if dt.year != now.year:
        return dt.strftime('%d/%m/%Y')
    if dt.month != now.month or dt.day != now.day:
        return dt.strftime('%d/%m %H:%M')
    return dt.strftime('%H:%M:%S')

def mkdir_by(filename: str):
    path = Path(Path(filename).parent)
    path.mkdir(parents=True, exist_ok=True)

def relative_name(fullname: str, root: str) -> str:
    return fullname.lstrip(root).lstrip("/").lstrip("\\")

def local_ip():
    hostname = socket.gethostname()
    return socket.gethostbyname(hostname)

def file_mimetype(filename: str) -> str:
    ''' video or image '''
    if not filename:
        return "unknown"
    mimestart = mimetypes.guess_type(filename)[0] or "unknown/ext"
    return mimestart.split('/')[0]
