import logging
from datetime import datetime
from pathlib import Path

import pytz


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

def mkdir_by(filename: str):
    path = Path(Path(filename).parent)
    path.mkdir(parents=True, exist_ok=True)

def relative_name(fullname: str, root: str) -> str:
    return fullname.lstrip(root).lstrip("/").lstrip("\\")
