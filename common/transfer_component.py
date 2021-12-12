from .ifile_info import IFileInfo


class TransferComponent:

    def __init__(self) -> None:
        pass

    def set_from(self, from_components: list[TransferComponent]) -> None:
        pass

    def OnFileTransferCallback(self, callback):
        self.OnFileTransferCall = callback

    def on_file_downloaded(self, file: IFileInfo):
        pass
