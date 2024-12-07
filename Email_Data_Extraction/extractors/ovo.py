import re
from decimal import Decimal
import datetime
from .base_extractor import BaseExtractor, EmailContent, TransactionData

class OVOExtractor(BaseExtractor):
    def match(self, title: str, email_from: str) -> bool:
        """
        Check if the email matches the OVO payment confirmation format.
        """
        return "Pembayaran Berhasil" in title and "OVO" in email_from
    
    def extract(self, content: EmailContent) -> list[TransactionData]:
        """
        Extract the transaction data from the email.
        """
        email = content.get_plaintext()

        # Clean up email content (replace multiple spaces and newlines with a single space)
        email = re.sub(r"\s+", " ", email)

        trx = TransactionData()
        trx.is_incoming = False
        trx.currency = "IDR"

        # Extract payment amount (and display in thousand Rupiah)
        amount_match = re.search(r"Pembayaran\s*Rp(\d{1,3}(?:.\d{3})*)", email)
        if amount_match:
            amount_str = amount_match.group(1).replace(".", "")
            trx.amount = Decimal(amount_str)

        # Extract transaction date
        date_match = re.search(r"(\d{1,2} \w{3} \d{4}, \d{2}:\d{2})", email)
        if date_match:
            trx.date = datetime.datetime.strptime(date_match.group(1), "%d %b %Y, %H:%M")

        # Extract merchant name
        merchant_match = re.search(r"Nama Toko\s([A-Za-z\s]+),\s", email)
        if merchant_match:
            trx.merchant = merchant_match.group(1).strip()

        # Extract transaction code (No. Resi)
        transaction_code_match = re.search(r"No\. Resi \(Kode Transaksi\)\s*(\S+)", email)
        if transaction_code_match:
            trx.trx_id = transaction_code_match.group(1)

        # Extract payment method
        if "OVO Cash" in email:
            trx.payment_method = "OVO Cash"
        else:
            trx.payment_method = "OVO Points"

        # Extract fees
        fees_match = re.search(r"Tip\sRp([\d,]+)", email)
        if fees_match:
            trx.fees = fees_match.group(1)

        return [trx]