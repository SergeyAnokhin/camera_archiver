# Camera archiver
Archive your ftp camera meadia files on other ftp with files renaming and event creation. Event can be used for send information to elasticsearch for example.

## Install
Copy files to /config/custom_components/camera_archiver

Add to your configuration.yaml file:
```yaml
sensor:
  - platform: camera_archiver
    local_storage: ./config/www/snapshot # intermediate storage can be used for display 'last' record
    scan_interval: "00:01:00"
    name: Yi1080pWoodSouth
    from:
      directory:
        path: ../home-assistant-core-data/input
        datetime_pattern: "%YY%mM%dD%HH/E1%MM%SS%f" # use python datetime format here
        copied_per_run: 2
        clean:
          empty_directories: True
          files:
            - index.dat
            - ".*\\.tmp"
      # ftp: 
      #   host: 192.168.1.XX
      #   user: USER
      #   password: !secret main
      #   path: /tmp/sd/record
      #   datetime_parser: "%YY%mM%dD%HH/E1%MM%SS%f.mp4" # use python datetime format here
        # copied_per_run: 2
      mqtt:
        topic: /yicam_1080p/motion_detection_image
    to:
      directory:
        path: ../home-assistant-core-data
        datetime_pattern: "%Y-%m/%d/Yi1080pWoodSouth_%Y-%m-%d_%H-%M-%S" # use python datetime format here
      # ftp:
      #   host: 192.168.1.XX
      #   user: USER
      #   password: !secret main
      #   path: /Camera/Yi1080pWoodSouth

switch:
  - platform: camera_archiver
    name: Yi1080pWoodSouth

automation:
- alias: auto_CameraArchiverFileCopied
  mode: queued
  trigger:
    - platform: event
      event_type: CameraArchiverFileCopied
      id: Yi1080pWoodSouth
      event_data:
        camera: Yi1080pWoodSouth
    - platform: event
      event_type: CameraArchiverFileCopied
      id: Yi1080pWoodNorth
      event_data:
        camera: Yi1080pWoodNorth
  action:
  - service: notify.elastic_input
    data_template:
      message: >

          "url": "http://192.168.1.XX:9200/cameraarchive-{{ trigger.event.data.DateTimeUtc.strftime("%Y.%m") }}/_create/{{ trigger.event.data.id }}"

          "doc": "event",

          "source_type": "ftp",

          "tags": "camera_archiver synology_cameraarchive"

          "volume": "/volume2"

          "_id": "{{ trigger.event.data.id }}",

          "path_source": "{{ trigger.event.data.SourceFile }}",

          "@timestamp": "{{ trigger.event.data.DateTimestampStrUtc }}",

          "event_start": "{{ trigger.event.data.DateTimestampStr }}",

          "ext": "{{ trigger.event.data.ext }}",

          "source_file_created": "{{ trigger.event.data.SourceFileCreated }}",

          "execution_time": "{{ as_timestamp(now()) | timestamp_custom('%Y-%m-%dT%H:%M:%S.000+00:00', False) }}",

          "camera": "{{ trigger.event.data.camera }}",

          "ext": "{{ trigger.event.data.ext }}",

          "path": "{{ trigger.event.data.path }}"

          "value": "{{ trigger.event.data.size }}"

          "sensor.type": "CameraArchive"

          "sensor.unit": "bytes"

          "trigger.id": "{{ trigger.id }}"

notify:
  - name: elastic_input
    platform: file
    timestamp: True
    filename: elastic_input.log
```
