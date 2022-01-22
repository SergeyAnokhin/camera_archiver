from enum import Enum

from ..const import CONF_FROM, CONF_TO


class TransferType(Enum):
    FROM = CONF_FROM
    TO = CONF_TO


class TransferComponentId:
    Entity: str = None
    TransferType: TransferType = None
    Name: str = None

    def __init__(self, entity: str, transferType: str) -> None:
        self.TransferType = TransferType.FROM if transferType == CONF_FROM else TransferType.TO
        self.Entity = entity

    @property
    def id(self):
        return f"{self.Entity}.{self.TransferType.value}.{self.Name}"

    def __str__(self):
        return self.id
