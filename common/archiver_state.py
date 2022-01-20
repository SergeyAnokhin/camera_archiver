from .transfer_state import TransferState


class ArchiverState:
    ''' Current camera archiver state '''

    def __init__(self) -> None:
        pass

    def append(self, transfer_state: TransferState):
        ''' Append last transfer to history '''   
        pass