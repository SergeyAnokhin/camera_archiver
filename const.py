DOMAIN = "camera_archiver"

DEFAULT_TIME_INTERVAL = '00:01:00'

CONF_LOCAL_STORAGE = "local_storage"
CONF_COPIED_PER_RUN = "copied_per_run"
CONF_USER = "user"
CONF_FROM = "from"
CONF_TO = "to"
CONF_FTP = "ftp"
CONF_DIRECTORY = "directory"
CONF_MQTT = "mqtt"
CONF_TOPIC = "topic"
CONF_PATH = "path"
CONF_DATETIME_PATTERN = "datetime_pattern"
CONF_TRIGGERS = "triggers"
CONF_ENABLE = "enable"
CONF_CLEAN = "clean"
CONF_EMPTY_DIRECTORIES = "empty_directories"
CONF_FILES = "files"

# Sensors:
SENSOR_NAME_FILES_COPIED = "Files copied"
SENSOR_NAME_FILES_COPIED_LAST = "Files copied last"
SENSOR_NAME_TO_COPY_FILES = "To copy files"

SENSOR_NAME_LAST_VIDEO = "Last video"
SENSOR_NAME_LAST_SCREENSHOT = "Last screenshot"
SENSOR_NAME_TO_COPY_EXTENSIONS = "To copy extensions"
SENSOR_NAME_PROCESSING_TIME = "Time processing"
SENSOR_NAME_FILES_COPIED_24_HOURS = "Files copied 24 hours"
SENSOR_NAME_FILES_COPIED_LAST_7_DAYS = "Files copied last 7 days"
SENSOR_NAME_MEGABYTES_TO_COPY = "Mb to copy"
SENSOR_NAME_MEGABYTES_COPIED = "Mb copied"
SENSOR_NAME_MEGABYTES_COPIED_LAST = "Mb copied"
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
ATTR_SIZE = "size"
ATTR_ID = "id"
ATTR_SOURCE_HOST = "source_host"
ATTR_SOURCE_FILE = "source_file"
ATTR_SOURCE_PLATFORM = "source_platform"
ATTR_SOURCE_COMPONENT = "source_component"
ATTR_SOURCE_TYPE = "XXXXX"
ATTR_SOURCE_FILE_CREATED = "source_file_created"
ATTR_LOCAL_FILE = "localFile"
ATTR_DESTINATION_FILE = "destination_file"
ATTR_DESTINATION_PLATFORM = "destination_platform"
ATTR_DESTINATION_COMPONENT = "destination_component"
ATTR_TIMESTAMP = "timestamp"
ATTR_TIMESTAMP_STR = "timestamp_str"
ATTR_TIMESTAMP_STR_UTC = "timestamp_str_utc"
ATTR_CAMERA = "camera"
ATTR_EXT = "ext"
ATTR_MIMETYPE = "mimetype"
ATTR_PATH = "path"
ATTR_LAST = "Last"
ATTR_TRANSFER_RESULT = "TransferResult"
ATTR_ARCHIVER_STATE = "ArchiverState"
ATTR_COLLECTOR_LAST_STATE_TYPE_UPDATED = "CollectorLastStateTypeUpdated"
ATTR_COLLECTOR_LAST_SENDER_COMPONENT = "CollectorLastSenderComponent"
ATTR_INSTANCE_NAME = "instance_name"
ATTR_FILES = "files"
ATTR_SIZE_MB = "SizeMb"
ATTR_EXTENSIONS = "Extensions"
ATTR_DURATION = "Duration"
ATTR_LAST_FILE = "LastFile"
ATTR_TRANSFER_STATE = "TransferState"


EVENT_CAMERA_ARCHIVER_FILE_COPIED = "CameraArchiverFileCopied"

SERVICE_RUN = "run"
SERVICE_FIELD_INSTANCE = "instance"
SERVICE_FIELD_COMPONENT = "component"
SERVICE_FIELD_DIRECTION = "direction"
