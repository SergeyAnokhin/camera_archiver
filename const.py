DOMAIN = "camera_archiver"


DEFAULT_SCAN_INTERVAL = 300

CONF_LOCAL_STORAGE = "local_storage"
CONF_USER = "user"
CONF_FROM = "from"
CONF_TO = "to"
CONF_FTP = "ftp"
CONF_DATETIME_PARSER = "datetime_parser"
CONF_DATETIME_PATTERN = "datetime_pattern"

# Sensors:
HA_LAST_VIDEO = "Last video"
HA_LAST_SCREENSHOT = "Last screenshot"
HA_NOT_PROCESSED_FILES = "Not processed files"
HA_FILES_COPIED = "Files copied"
HA_FILES_COPIED_24_HOURS = "Files copied 24 hours"
HA_FILES_COPIED_LAST_7_DAYS = "Files copied last 7 days"
HA_MEGABYTES_COPIED = "MB copied"
HA_MEGABYTES_COPIED_24_HOURS = "MB copied 24 hours"
HA_MEGABYTES_COPIED_LAST_7_DAYS = "MB copied 7 days"

ICON_VIDEO = 'mdi:file-video'
ICON_SCREENSHOT = 'mdi:file-jpg-box'
ICON_COPIED = 'mdi:file-check'
ICON_NOT_COPIED = 'mdi:file-clock'
ICON_24HOURS = 'mdi:hours-24'
ICON_7DAYS = 'mdi:calendar-week'
ICON_DEFAULT = 'mdi:upload'

ICONS_MAPPING = {
    HA_LAST_VIDEO: ICON_VIDEO,
    HA_LAST_SCREENSHOT: ICON_SCREENSHOT,
    HA_NOT_PROCESSED_FILES: ICON_NOT_COPIED,
    HA_FILES_COPIED: ICON_COPIED,
    HA_FILES_COPIED_24_HOURS: ICON_24HOURS,
    HA_FILES_COPIED_LAST_7_DAYS: ICON_7DAYS,
    HA_MEGABYTES_COPIED: ICON_COPIED,
    HA_MEGABYTES_COPIED_24_HOURS: ICON_24HOURS,
    HA_MEGABYTES_COPIED_LAST_7_DAYS: ICON_7DAYS,
}
