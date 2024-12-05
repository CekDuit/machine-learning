from decimal import Decimal
from .base_extractor import BaseExtractor, TransactionData
import re
import datetime

class OVOExtractor(BaseExtractor):
    def match(self, title: str, email_from: str) -> bool:
        return title == "OVO QR Payment Receipt" and email_from == "noreply@ovo.co.id"
    
    def extract(self, content: str) -> list[TransactionData]:
        # Extract payment details from OVO email content

        trx = TransactionData()

        # Extract trx details
        trx.is_incoming = False
        trx.payment_method = "OVO"

        # Extracting Amount and Currency
        amount_match = re.search(r"Pembayaran\s*-\s*Rp([\d,\.]+)", content)
        if amount_match:
            trx.currency = "IDR"
            trx.amount = Decimal(amount_match.group(1).replace(",", "").replace(".", ""))

        # Extract merchant name
        merchant_match = re.search(r"Nama Toko\s*:\s*(.+)", content)
        if merchant_match:
            trx.merchant = merchant_match.group(1)

        # Extract transaction date
        date_match = re.search(r"(\d{2} \w+ \d{4}, \d{2}:\d{2})", content)
        if date_match:
            trx.date = datetime.datetime.strptime(date_match.group(1), "%d %b %Y, %H:%M")

        # Extract location (optional)
        location_match = re.search(r"Lokasi\s*:\s*(.+)", content)
        if location_match:
            trx.description = f"Location: {location_match.group(1)}"

        # Additional details if needed
        approval_code_match = re.search(r"Kode Approval\s*:\s*(.+)", content)
        payment_method_match = re.search(r"Metode Pembayaran\s*:\s*(.+)", content)

        trx.extra_data = {
            "Approval Code": approval_code_match.group(1) if approval_code_match else None,
            "Payment Method": payment_method_match.group(1) if payment_method_match else None,
        }

        return [trx]