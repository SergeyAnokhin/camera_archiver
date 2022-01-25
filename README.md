# Camera archiver
Archive your ftp camera meadia files on other ftp with files renaming and event creation. Event can be used for send information to elasticsearch for example.

## Install
Copy files to /config/custom_components/camera_archiver

Add to your configuration.yaml file:

Basic config
```yaml
sensor:
  - platform: camera_archiver
    name: Yi1080pWoodSouth
    from:
      ftp: 
        host: 192.168.1.XX
        user: USER
        password: !secret main
        path: /tmp/sd/record
        datetime_parser: "%YY%mM%dD%HH/E1%MM%SS%f" # use python datetime format here
    to:
      ftp:
        host: 192.168.1.XX
        user: USER
        password: !secret main
        path: /Camera/Yi1080pWoodSouth
        datetime_pattern: "%Y-%m/%d/Yi1080pWoodSouth_%Y-%m-%d_%H-%M-%S" # use python datetime format here
```

Advanced config
```yaml
camera_archiver:
  name: toto
  entities:
    - name: Yi1080pWoodSouth
      local_storage: ./config/www/snapshot # intermediate storage can be used for display 'last' record
      from: ### any in this list
        - name: directory
          platform: directory
          path: ../home-assistant-core-data/input
          datetime_pattern: "%YY%mM%dD%HH/E1%MM%SS%f" # use python datetime format here
          copied_per_run: 2
          scan_interval: 
            minutes: 1
        # - name: ftp
        #   platform: ftp
        #   host: !secret Yi1080pWoodSouth_ip
        #   user: !secret Yi1080pWoodSouth_user
        #   password: !secret Yi1080pWoodSouth_pass
        #   path: /tmp/sd/record
        #   datetime_pattern: "%YY%mM%dD%HH/E1%MM%SS%f" # use python datetime format here
        #   copied_per_run: 2
        #   scan_interval: 
        #     minutes: 1
        #   clean:
        #     empty_directories: True
        #     files:
        #       - index.dat
        #       - ".*\\.tmp"
        - name: mqtt
          platform: mqtt
          topic: yicam_1080p/motion_detection_image
      to: ### all in this list
        # - name: directory
        #   platform: directory
        #   path: ../home-assistant-core-data
        #   datetime_pattern: "%Y-%m/%d/Yi1080pWoodSouth_%Y-%m-%d_%H-%M-%S" # use python datetime format here
        - platform: camera
          filter: '.*\\.jpg'
        - name: ftp
          platform: ftp
          host: !secret server_ip
          user: !secret server_user
          password: !secret server_pass
          path: /CameraArchive/Yi1080pWoodSouth
          datetime_pattern: "%Y-%m/%d/Yi1080pWoodSouth_%Y-%m-%d_%H-%M-%S" # use python datetime format here

automation:
- alias: auto_CameraArchiverFileCopied
  mode: queued
  trigger:
  - platform: event
    event_type: CameraArchiverFileCopied
    id: Yi1080pWoodSouth
    event_data:
      camera: Yi1080pWoodSouth
  action:
  #- service: camera_archiver.run
  #- service: script.variable_test
  - service: rest_command.elastic_cameraarchive
    data_template:
      index: '{{ trigger.event.data.timestamp | timestamp_custom("%Y.%m", False) }}'
      tags: 'camera_archiver activity motion camera archive webcam wifi'
      ftp_date: '{{ trigger.event.data.ftp_date | default }}'
      trigger: '{{ this.entity_id }}'
      elasticsearch_point: !secret elasticsearch_point
      data_nature: >-
        {{ trigger.event.data }}
      customize_data: 
        position: 
          detail: cupboard
          floor: 2
          room: WoodSouth
          is_external: false
        sensor: 
          emoji: "🎥"
          icon: mdi:webcam
          type: CameraArchive
          unit: bytes
          is_external: false
          display: "{{ trigger.event.data.camera }} CameraArchive"
          id: "CameraArchive_{{ trigger.event.data.camera }}"

rest_command:
  elastic_cameraarchive:
    url: 'http://{{ elasticsearch_point }}/cameraarchive-{{ index }}/_create/{{ data_nature.id }}'
    method: POST
    content_type: "application/json; charset=utf-8"
    headers:
      accept: "application/json, text/html"
    payload: >
      {
        "@timestamp": "{{ data_nature.timestamp_str_utc }}",
        "camera": "{{ data_nature.camera }}",
        "doc": "event",
        "event_start": "{{ data_nature.timestamp_str }}",
        "ext": "{{ data_nature.ext }}",
        "path": "{{ data_nature.destination_file }}",
        "origin": {
          "type": "{{ data_nature.source_type }}",
          {% if ftp_date and ftp_date != '' %}"ftp_date": "{{ ftp_date }}",{% endif %}
          "modif_time": "{{ data_nature.source_file_created }}",
          "host": "{{ data_nature.source_host }}",
          "filename": "{{ data_nature.source_file }}"
        },
        "mimitype": "{{ data_nature.mimetype }}",
        {{ (customize_data | to_json | trim())[1:-1] }},
        "tags": "synology_cameraarchive hassio {{ tags }}",
        "value": {{ data_nature.size }},
        "volume": "/volume2"
      }  
```

## Entities

- _Switch_: 
    - Enable/Disable Global
    - Selector By component From: 'On/Off'
    - Selector By component To: 'On/Off'
- _Sensors_:
  - For each 'From' transfer component: 
    - In storage files
      - Attribute: Size
      - Attribute: Extensions
    - Copied files during last exec
      - Attribute: Size
    - Copied files 24 hours (statistics sensor)
    - Copied files 7 days (statistics sensor)
    - Health 24 hours (copied files > 0) (template sensor)
    - Health 7 days (copied files > 0) (template sensor)
  - For each 'To' transfer component: 
    - Copied files during last exec
      - Attribute: Size
    - Copied files 24 hours (statistics sensor)
    - Copied files 7 days (statistics sensor)
    - Last Image (to see)
    - Last Video (to play)

## TransferManager

    1. Read config, create TransferComponents
    2. Link components 'From'TransferComponent 1<->n 'To'TransferComponent
    3. Attach to events (DataUpdaterCoordinator, Mqtt, Service etc)
    4. Create Sensors and switchers 
    5. Update sensors with TransferState
    6. Setup platform not sensor???
