import re
from decimal import Decimal
import datetime
from .base_extractor import BaseExtractor, EmailContent, TransactionData

class UniPinExtractor(BaseExtractor):
    def match(self, title: str, email_from: str) -> bool:
        """
        Check if the email matches the UniPin purchase format.
        """
        return title == "UniPin :: Success Flash Top Up Transaction" and email_from == "do_not_reply@unipin.com"
    
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
        trx.fees = 0 # No fees for UniPin transactions

        if "UniPin" in email:
            trx.merchant = "UniPin"

        # Extract transaction time
        time_match = re.search(r"Waktu Pembayaran\s*(\d{1,2} \w{3} \d{4} \d{2}:\d{2}) \(\w{3} \+\d{1,2}\)", email)
        if time_match:
            trx.date = datetime.datetime.strptime(time_match.group(1), "%d %b %Y %H:%M")

        # Extract payment method
        payment_method_match = re.search(r"Metode Pembayaran\s*(.*?)\s*Nomor Transaksi", email)
        if payment_method_match:
            trx.payment_method = payment_method_match.group(1).strip()

        # Extract transaction number
        trx_id_match = re.search(r"Nomor Transaksi\s*(\S+)", email)
        if trx_id_match:
            trx.trx_id = trx_id_match.group(1)

        # Extract product name
        product_match = re.search(r"Nama Barang\s*(.*?)\s*Nominal Transaksi", email)
        if product_match:
            trx.description = product_match.group(1).strip()

        # Extract transaction amount
        amount_match = re.search(r"Nominal Transaksi\s*Rp\s*([\d,]+)", email)
        if amount_match:
            trx.amount = Decimal(amount_match.group(1).replace(",", ""))

        return [trx]