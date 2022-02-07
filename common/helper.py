import logging
import socket
from datetime import datetime, timedelta
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

def to_short_human_readable_delta(delta: timedelta) -> str:
    if not delta:
        return None
    if delta.days > 1:
        return f"{delta.days}d"
    if delta.days == 1:
        return f"<1d"

    hours = round(delta.seconds / 3600)
    if hours > 1:
        return f"{hours}h"
    if hours == 1:
        return f"<1h"

    mins = round(delta.seconds / 60)
    if mins > 1:
        return f"{mins}m"
    if hours == 1:
        return f"<1m"

    if delta.seconds > 1:
        return f"{delta.seconds}s"
    if delta.seconds == 1:
        return f"<1s"

    return "now"

def mkdir_by(filename: str):
    path = Path(Path(filename).parent)
    path.mkdir(parents=True, exist_ok=True)

def relative_name(fullname: str, root: str) -> str:
    return fullname.lstrip(root).lstrip("/").lstrip("\\")

def local_ip():
    hostname = socket.gethostname()
    return socket.gethostbyname(hostname)
