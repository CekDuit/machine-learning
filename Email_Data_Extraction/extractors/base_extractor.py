from abc import abstractmethod
from datetime import datetime
from decimal import Decimal
from enum import Enum
from io import StringIO
import pandas as pd
from collections import defaultdict

import email
import email.parser
import email.message
import email.policy
import html2text
import email.utils
import string
from typing import Any

def to_ascii(s: Any) -> str:
    return str(s).encode("ascii", errors="ignore").decode()

class TransactionData:
    # Expected columns
    trx_id: str
    date: datetime
    merchant: str
    fees: Decimal = Decimal(0)
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

    def is_proper(self):
        mandatory_fields = ["trx_id", "date", "merchant", "amount", "currency", "payment_method", "is_incoming", "description"]
        return all(hasattr(self, field) for field in mandatory_fields)
    
    def to_formatted_dict(self):
        return {
            "Datetime": self.date,
            "Merchant Name": to_ascii(self.merchant),
            "Transaction ID": to_ascii(self.trx_id),
            "Amount": self.amount,
            "Currency": self.currency,
            "Payment Method": self.payment_method,
            "Transaction Type": "INCOME" if self.is_incoming else "EXPENSE",
            "Notes": to_ascii(self.description),
        }

h = html2text.HTML2Text()
h.ignore_links = True
h.ignore_emphasis = True
h.ignore_mailto_links = True
h.ignore_images = True
h.ignore_tables = True

class EmailContent:

    # Plaintext / markdown-formatted
    _md_str: str | None = None

    # As list of Pandas DataFrame
    _dfs: list[pd.DataFrame] | None = None
    
    # As HTML
    _html: str | None = None
    
    # Raw email message
    email_message: email.message.EmailMessage

    def __init__(self, message: email.message.EmailMessage):
        self.title: str = message.get("subject", "Unknown Subject")
        self.from_email: str = email.utils.parseaddr(message.get("from", "Unknown Sender <unknown@unknown.com>"))[1]
        self.email_message = message

    def _get_content(self) -> str:
        body = self.email_message.get_body()
        if not body:
            raise ValueError("Email body is empty")

        return str(body.get_content())

    def get_html(self) -> str:
        """
        Obtain formatted as HTML
        """
        if not self._html:
            self._html = self._get_content()
        return self._html

    def get_plaintext(self) -> str:
        """
        Obtain formatted as plaintext
        """
        if not self._md_str:
            self._md_str = h.handle(self._get_content())
        return self._md_str

    def get_dfs(self, **kwargs) -> list[pd.DataFrame]:
        """
        Obtain HTML tables formatted as a list of Pandas DataFrame
        """
        if not self._dfs:
            # Refuse to parse numbers, as thousands separators can be really different in different locales
            self._dfs = pd.read_html(StringIO(self.get_html()), **kwargs) # type: ignore
        return self._dfs

    def __str__(self):
        return f"EmailContent(title={self.title}, from_email={self.from_email})"

    def __repr__(self):
        return str(self)


class BaseExtractor:
    @abstractmethod
    def match(self, title: str, email_from: str) -> bool:
        """
        Test if the email matches the extractor
        """
        pass

    @abstractmethod
    def extract(self, content: EmailContent) -> list[TransactionData]:
        """
        Extract transactions from the email content
        """
        pass

    @abstractmethod
    def _extract_title(self, email: str, title: str) -> list[TransactionData]:
        """
        Extract transactions from the email content
        """
        pass
