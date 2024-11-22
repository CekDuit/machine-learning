from abc import abstractmethod
from datetime import datetime
from decimal import Decimal
from enum import Enum


class TransactionData:
    # Expected columns
    trx_id: str
    date: datetime
    merchant: str
    amount: Decimal
    currency: str
    payment_method: str

    is_incoming: bool
    description: str

    def __str__(self):
        s = self.__class__.__name__ + "("
        for k, v in self.__dict__.items():
            s += f"{k}={v}, "
        s += ")"

        return s

    def __repr__(self):
        return str(self)


class BaseExtractor:
    @abstractmethod
    def match(self, title: str, email_from: str) -> bool:
        pass

    @abstractmethod
    def extract(self, email: str) -> list[TransactionData]:
        pass
