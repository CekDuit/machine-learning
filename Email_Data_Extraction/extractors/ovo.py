from decimal import Decimal
from .base_extractor import BaseExtractor, TransactionData
import re
import datetime

class OvoExtractor(BaseExtractor):
    def match(self, title: str, email_from: str) -> bool:
        return title == "OVO QR Payment Receipt" and email_from == "noreply@ovo.co.id"
    
    def extract(self, email: str) -> list[TransactionData]:
        # Extract payment details from OVO email content

        trx = TransactionData()

        # Extract trx details
        trx.is_incoming = False
        trx.payment_method = "OVO"

        # Extracting Amount and Currency
        amount_match = re.search(r"Pembayaran\s*-\s*Rp([\d,\.]+)", email)
        if amount_match:
            trx.currency = "IDR"
            trx.amount = Decimal(amount_match.group(1).replace(",", "").replace(".", ""))

        # Extract merchant name
        trx.merchant = re.search(r"Nama Toko\s*:\s*(.+)", email).group(1)

        # Extract transaction date
        date_match = re.search(r"(\d{2} \w+ \d{4}, \d{2}:\d{2})", email)
        if date_match:
            trx.date = datetime.datetime.strptime(date_match.group(1), "%d %b %Y, %H:%M")

        # Extract location (optional)
        location_match = re.search(r"Lokasi\s*:\s*(.+)", email)
        if location_match:
            trx.description = f"Location: {location_match.group(1)}"

        # Additional details if needed
        trx.extra_data = {
            "Approval Code": re.search(r"Kode Approval\s*:\s*(.+)", email).group(1),
            "Payment Method": re.search(r"Metode Pembayaran\s*:\s*(.+)", email).group(1),
        }

        return [trx]


''' Usage Example
email_body = """
Nama Acquirer    : BCA
Nama Toko        : TRUSTEA
Lokasi           : SURABAYA, 60293 ID
No. Referensi    : p01-240917-fd2f8c4f-f6aa-491b-9149-31beeb122126
No. Resi (Kode Transaksi) : 072bbc31f9ba
Kode Approval    : 634065
Metode Pembayaran: OVO Cash
Pembayaran       - Rp6.000
"""

extractor = OvoExtractor()
if extractor.match("OVO QR Payment Receipt", "noreply@ovo.co.id"):
    transactions = extractor.extract(email_body)
    for transaction in transactions:
        print(transaction)

'''