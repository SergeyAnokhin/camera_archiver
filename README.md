# Camera archiver
Archive your ftp camera meadia files on other ftp with files renaming and event creation. Event can be used for send information to elasticsearch for example.

## Install
Copy files to /config/custom_components/camera_archiver

Add to your configuration.yaml file:
```yaml
sensor:
  - platform: camera_archiver
    local_storage: ./config/www/snapshot # intermediate storage can be used for display 'last' record
    name: Yi1080pWoodSouth Camera
    from:
      directory:
        path: ../home-assistant-core-data/input
        datetime_pattern: "%YY%mM%dD%HH/E1%MM%SS%f.mp4" # use python datetime format here
      # ftp: 
      #   host: 192.168.1.58
      #   user: root
      #   password: !secret main
      #   path: /tmp/sd/record
      #   datetime_parser: "%YY%mM%dD%HH/E1%MM%SS%f.mp4" # use python datetime format here
    to:
      directory:
        path: ../home-assistant-core-data/
        datetime_pattern: "%Y-%m/%d/Yi1080pWoodSouth_%Y-%m-%d_%H-%M-%S.mp4" # use python datetime format here
      # ftp:
      #   host: 192.168.1.16
      #   user: camera
      #   password: !secret main
      #   path: /Camera/Yi1080pWoodSouth
```
