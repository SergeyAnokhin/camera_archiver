import logging

def getLogger(name: str, instance: str = "", component: str = "") -> logging.Logger:
    name = name.replace("custom_components.camera_archiver", "CamArc")
    instance = ('::' + instance) if instance else ""
    component = ('.' + component) if component else ""
    return logging.getLogger(f"{name}{instance}{component}")
