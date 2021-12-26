DOMAIN = "camera_archiver"


DEFAULT_TIME_INTERVAL = '00:01:00'

CONF_LOCAL_STORAGE = "local_storage"
CONF_USER = "user"
CONF_FROM = "from"
CONF_TO = "to"
CONF_FTP = "ftp"
CONF_DIRECTORY = "directory"
CONF_MQTT = "mqtt"
CONF_PATH = "path"
CONF_DATETIME_PATTERN = "datetime_pattern"
CONF_MAX_FILES = "max_files"
CONF_TRIGGERS = "triggers"
CONF_ENABLE = "enable"

# Sensors:
SENSOR_NAME_LAST_VIDEO = "Last video"
SENSOR_NAME_LAST_SCREENSHOT = "Last screenshot"
SENSOR_NAME_TO_COPY_FILES = "To copy files"
SENSOR_NAME_FILES_COPIED = "Files copied"
SENSOR_NAME_FILES_COPIED_24_HOURS = "Files copied 24 hours"
SENSOR_NAME_FILES_COPIED_LAST_7_DAYS = "Files copied last 7 days"
SENSOR_NAME_MEGABYTES_TO_COPY = "Mb to copy"
SENSOR_NAME_MEGABYTES_COPIED = "Mb copied"
SENSOR_NAME_MEGABYTES_COPIED_24_HOURS = "Mb copied 24 hours"
SENSOR_NAME_MEGABYTES_COPIED_LAST_7_DAYS = "Mb copied 7 days"

ICON_VIDEO = 'mdi:file-video'
ICON_SCREENSHOT = 'mdi:file-jpg-box'
ICON_COPIED = 'mdi:file-check'
ICON_TO_COPY = 'mdi:file-clock'
ICON_24HOURS = 'mdi:hours-24'
ICON_7DAYS = 'mdi:calendar-week'
ICON_DEFAULT = 'mdi:upload'

ATTR_FROM = "From"
ATTR_DURATION = "Duration"
ATTR_EXTENSIONS = "Extensions"
ATTR_SIZE = "Size"
ATTR_SOURCE_FILE = "SourceFile"
ATTR_SOURCE_FILE_CREATED = "SourceFileCreated"

EVENT_CAMERA_ARCHIVER_FILE_COPIED = "CameraArchiverFileCopied"

# ICONS_MAPPING = {
#     HA_LAST_VIDEO: ICON_VIDEO,
#     HA_LAST_SCREENSHOT: ICON_SCREENSHOT,
#     HA_NOT_PROCESSED_FILES: ICON_NOT_COPIED,
#     HA_FILES_COPIED: ICON_COPIED,
#     HA_FILES_COPIED_24_HOURS: ICON_24HOURS,
#     HA_FILES_COPIED_LAST_7_DAYS: ICON_7DAYS,
#     HA_MEGABYTES_COPIED: ICON_COPIED,
#     HA_MEGABYTES_COPIED_24_HOURS: ICON_24HOURS,
#     HA_MEGABYTES_COPIED_LAST_7_DAYS: ICON_7DAYS,
# }
