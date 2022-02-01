# Camera archiver
Archive your ftp camera meadia files on other ftp with files renaming and event creation. Event can be used for send information to elasticsearch for example.

## Install
Copy files to /config/custom_components/camera_archiver

Add to your configuration.yaml file:

Config
```yaml
camera_archiver:
  components:
    - id: input local directory
      platform: directory
      path: ../home-assistant-core-data/input
      datetime_pattern: "%YY%mM%dD%HH/E1%MM%SS%f" # use python datetime format here
      copied_per_run: 2
      clean:
        empty_directories: True
    - id: Yi1080pWoodSouth ftp
      platform: ftp
      host: !secret Yi1080pWoodSouth_ip
      user: !secret Yi1080pWoodSouth_user
      password: !secret Yi1080pWoodSouth_pass
      path: /tmp/sd/record
      datetime_pattern: "%YY%mM%dD%HH/E1%MM%SS%f" # use python datetime format here
      copied_per_run: 2
      clean:
        empty_directories: True
        files:
          - index.dat
          - ".*\\.tmp"
    - id: Yi1080pWoodSouth mqtt
      platform: mqtt
      topic: yicam_1080p/motion_detection_image
    - id: output local directory
      platform: directory
      path: ../home-assistant-core-data
      datetime_pattern: "%Y-%m/%d/Yi1080pWoodSouth_%Y-%m-%d_%H-%M-%S" # use python datetime format here
    - id: elasticsearch
      platform: elasticsearch
      index: cameraarchivetest-*
    - id: OpenCV api
      platform: api
      url: http://winserver:0000/process
    - id: DiskStation ftp
      platform: ftp
      host: !secret server_ip
      user: !secret server_user
      password: !secret server_pass
      path: /CameraArchive/Yi1080pWoodSouth
      datetime_pattern: "%Y-%m/%d/Yi1080pWoodSouth_%Y-%m-%d_%H-%M-%S" # use python datetime format here
    - id: Coocheer mail
      platform: imap
      host: imap.gmail.com
      user: toto
      password: tata
      path: Camera/Coocheer
    - id: scheduler_3m
      platform: scheduler
      scan_interval: 
        minutes: 3

  sensors:
    - id: camera last
      platform: camera
    - id: repository_stat sensor
      platform: sensor
      type: repository_stat
    - id: transfer_stat sensor
      platform: sensor
      type: transfer_stat
    - id: timer sensor
      platform: sensor
      type: timer
    - id: last file sensor
      platform: sensor
      type: last_file
    - id: last time sensor
      platform: sensor
      type: last_time

  pipelines:
    - id: local
      component: scheduler_3m
      listeners:
        - sensor: timer sensor
        - component: input local directory
          listeners:
            - sensor: repository_stat sensor
            - component: output local directory
              listeners:
                - sensor: transfer_stat sensor
                - sensor: last file sensor
                - sensor: last time sensor

```

