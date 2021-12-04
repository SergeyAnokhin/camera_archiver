# Camera archiver
Archive your ftp camera meadia files on other ftp with files renaming and event creation. Event can be used for send information to elasticsearch for example.

## Install
Copy files to /config/custom_components/camera_archiver

Add to your configuration.yaml file:
```yaml
camera_archiver:
  local_storage: ./config/www/snapshot # intermediate storage can be used for display 'last' record
  name: CAMERA NAME
  from:
    ftp: 
      host: YOUR_FTP_HOST
      user: YOUR_FTP_USERNAME
      password: YOUR_FTP_PASSWORD
      path: FTP_PATH_TO_RECORDED_FILES
    datetime_parser: "%YY%mM%dD%HH/E1%MM%SS%f.mp4" # use python datetime format here
  to:
    ftp:
      host: YOUR_FTP_HOST
      user: YOUR_FTP_USERNAME
      password: YOUR_FTP_PASSWORD
      path: FTP_PATH_TO_ARCHIVE_FILES
    datetime_pattern: "%Y-%m/%d/Yi1080pWoodSouth_%Y-%m-%d_%H-%M-%S.mp4" # use python datetime format here
```
