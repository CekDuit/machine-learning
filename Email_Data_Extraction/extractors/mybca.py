from decimal import Decimal
from .base_extractor import BaseExtractor, EmailContent, TransactionData
import re
import datetime


class MyBCAExtrator(BaseExtractor):
    def match(self, title: str, email_from: str) -> bool:
        return title == "Internet Transaction Journal" and email_from == "bca@bca.co.id"

    def extract(self, content: EmailContent) -> list[TransactionData]:
        email = content.get_plaintext()
        # Example format:
        # Status 	: 	Successful
        # Transaction Date 	: 	19 Nov 2024 17:52:19
        # Transfer Type 	: 	Transfer to BCA Account
        # Source of Fund 	: 	7625xxxx00
        # Source Currency 	: 	IDR - Indonesian Rupiah
        # Beneficiary Account 	: 	0000000000
        # Target Currency 	: 	IDR - Indonesian Rupiah
        # Beneficiary Name 	: 	[REDACTED]
        # Target Amount 	: 	IDR 1,000,000.00
        # Remarks 	: 	-
        # Reference No. 	: 	C000000-50000-400000-0000-BE000000

        trx = TransactionData()
        trx.is_incoming = False
        trx.payment_method = "myBCA"

        # Split per line and match
        currency, amount = re.search(
            r"(?:Target Amount|Total Payment|Amount)\s*:\s*(\w{3})\s*([\d,\.]+)", email
        ).groups()
        
        fee_search = re.search(
            r"(?:Fees|Fee)\s*:\s*(\w{3})\s*([\d,\.]+)", email
        )
        
        if fee_search:
            currency, fee = fee_search.groups()
            trx.fees = Decimal(fee.replace(",", ""))
            trx.fees = Decimal(fee.replace(",", ""))
        
        trx.currency = currency
        trx.amount = Decimal(amount.replace(",", ""))

        trx.description = re.search(r"(?:Remarks|Description)\s*:\s*(.+)", email).group(1)
        trx.merchant = re.search(r"(?:Beneficiary Name|Company/Product Name)\s*:\s*(.+)", email).group(1)
        trx.trx_id = re.search(r"Reference No\.\s*:\s*(.+)", email).group(1)
        trx.date = datetime.datetime.strptime(
            re.search(r"Transaction Date\s*:\s*(.+)", email).group(1).strip(),
            "%d %b %Y %H:%M:%S",
        )
        
        return [trx]
