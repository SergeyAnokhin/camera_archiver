from datetime import datetime
import os, logging

from ..common.ifile_info import IFileInfo
from ..common.transfer_component import TransferComponent
from ..common.transfer_state import TransferState
from ..const import ATTR_DESTINATION_FILE, ATTR_LOCAL_FILE, CONF_DATETIME_PATTERN, CONF_FROM, CONF_FTP, CONF_PATH, CONF_TO

from .FtpConn import FtpConn
from .ftp_file_info import FtpFileInfo

_LOGGER = logging.getLogger(__name__)

class FtpTransfer(TransferComponent):
    def __init__(self, config: dict):
        self._config = config

    def list_files(self, onfileCallback = None) -> TransferState:
        startpath = self._config[CONF_PATH]
        _LOGGER.debug(f"Stat from [{startpath}]: START")
        state = TransferState()
        with FtpConn(self._config) as srcFtp:
            srcFtp.cd(self._config[CONF_PATH])
            fs_items = srcFtp.GetFtpItems()
            for fs in fs_items:
                dt = self.filename_datetime(fs)
                if dt == None:
                    continue # ignore file
                fs.datetime = dt

                state.add(fs)
                if onfileCallback:
                    onfileCallback(fs, srcFtp)
                
                if state.files_count >= self._copied_per_run:
                    break

        _LOGGER.debug(f"Stat from [{startpath}]: END, {state}")
        return state


    def state(self) -> TransferState:
        return self.list_files()

        # cftp = self._config
        # state = TransferState()

        # with FtpConn(cftp) as srcFtp:
        #     srcFtp.cd(cftp[CONF_PATH])
        #     fs_items = srcFtp.GetFtpItems()
        #     for fs in fs_items:
        #         subitems = srcFtp.GetFtpItems(fs.name)

        #         for f in subitems:
        #             state.add(f.relname(), f.size())
        #             # _LOGGER.debug(f"Found: {f}")

        # _LOGGER.info(f"Files check done. Found: {state}")
        # state.stop()
        # return state

    def run(self):
        def onfile(file: IFileInfo, srcFtp: FtpConn) -> None:
            srcFtp.Download(file)
            self._on_file_transfer(file)
        return self.list_files(onfile)


        # cftp = self._config

        # with FtpConn(cftp) as srcFtp:
        #     srcFtp.cd(cftp[CONF_PATH])
        #     fs_items = srcFtp.GetFtpItems()
        #     files_counter = 0
        #     files_copied = 0
        #     for fs in fs_items:
        #         subitems = srcFtp.GetFtpItems(fs.name)

        #         for f in subitems:
        #             files_counter = files_counter + 1
        #             if files_counter > max:
        #                 continue

        #             files_copied = files_copied + 1
        #             stat = TransferState()
        #             stat.add(f)

        #             srcFtp.Download(f)
        #             # dstFtpFile = self.Upload(localfile, self.datetime(f))

        #             # stat.info["path"] = dstFtpFile
        #             # stat.info["path_source"] = f.fullname
        #             # stat.info["value"] = os.path.getsize(localfile)
        #             self._on_file_transfer(f)

        # _LOGGER.info(f"Files transferring done. Copied: {files_copied} / {files_counter}")


    def localFileStorage(self, file: FtpFileInfo) -> str:
        return f'{self.config["local_storage"]}/camera.{self.config["camera"]["name"]}.{file.extension}'

    def Upload(self, localfile: str, dt: datetime):
        cftp = self._config
        fullpath = f"{cftp[CONF_PATH]}/{dt.strftime(cftp[CONF_DATETIME_PATTERN])}"

        with FtpConn(cftp) as ftp:
            ftp.Upload(localfile, fullpath)

        return fullpath

    def from_component_download_to_local_finished_callback(self, callbackObject: IFileInfo) -> None:
        rel_path = callbackObject.datetime.strftime(self._config[CONF_DATETIME_PATTERN])
        filename = f"{self._config[CONF_PATH]}/{rel_path}.{callbackObject.ext}"

        with callbackObject.Content:
            with FtpConn(self._config) as ftp:
                _LOGGER.debug(f"Save file: [memory] => [{filename}]")
                ftp.UploadBytes(callbackObject.Content, filename)
            callbackObject.Content.close()

        ''' File transffered declaration '''
        if self.copiedFileCallback:
            self.copiedFileCallback({
                ATTR_LOCAL_FILE: callbackObject,
                ATTR_DESTINATION_FILE: filename
            })


# # https://stackoverflow.com/questions/16991819/ftp-sending-python-bytesio-stream
# import ftplib as ftp
# from io import BytesIO

# with ftp.FTP("192.168.1.XX", "", "") as ftp_one:
#     with ftp.FTP("192.168.1.XX", "", "") as ftp_two:
#         with BytesIO() as myfile:
#             ftp_one.retrbinary ('RETR /tmp/sd/record/2021Y11M16D17H/E155M42S18.mp4', myfile.write)
#             myfile.seek(0)
#             ftp_two.storbinary('STOR /CameraArchive/virtualtest.mp4', myfile)
#             ftp_one.close()
#             ftp_two.close()
#             myfile.close()
