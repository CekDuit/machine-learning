from decimal import Decimal
from .base_extractor import BaseExtractor, EmailContent, TransactionData
import re
import datetime

class OVOExtractor(BaseExtractor):
    def match(self, title: str, email_from: str) -> bool:
        return title == "OVO QR Payment Receipt" and email_from == "noreply@ovo.co.id"
    
    def extract(self, content: EmailContent) -> list[TransactionData]:
        # Extract payment details from OVO email content
        email = content.get_plaintext()

        trx = TransactionData()

        # Extract trx details
        trx.is_incoming = False
        trx.payment_method = "OVO"

        # Extracting Amount and Currency
        amount_match = re.search(r"Pembayaran\s+Rp([\d,\.]+)", email)
        if amount_match:
            trx.currency = "IDR"
            trx.amount = Decimal(amount_match.group(1).replace(",", "").replace(".", ""))

        # Extract merchant name
        trx.merchant = re.search(r"Nama Toko\s+(.+)", email).group(1)

        # Extract transaction date
        date_match = re.search(r"(\d{2} \w+ \d{4}, \d{2}:\d{2})", email)
        if date_match:
            trx.date = datetime.datetime.strptime(date_match.group(1), "%d %b %Y, %H:%M")

        # Extract location (optional)
        location_match = re.search(r"Lokasi\s+(.+)", email)
        if location_match:
            trx.description = f"Location: {location_match.group(1)}"

        # Additional details if needed
        trx.extra_data = {
            "Approval Code": re.search(r"Kode Approval\s+(.+)", email).group(1),
            "Payment Method": re.search(r"Metode Pembayaran\s+(.+)", email).group(1),
        }

        return [trx]