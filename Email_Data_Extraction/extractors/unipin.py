import re
from decimal import Decimal
import datetime
from .base_extractor import BaseExtractor, EmailContent, TransactionData

class UniPinExtractor(BaseExtractor):
    def match(self, title: str, email_from: str) -> bool:
        """
        Check if the email matches the UniPin purchase format.
        """
        return email_from == "cs@unipin.com" and "UniPin" in title
    
    def extract(self, content: EmailContent) -> list[TransactionData]:
        """
        Extract the transaction data from the email.
        """
        email = content.get_plaintext()

        # Clean up email content (replace multiple spaces and newlines with a single space)
        email = re.sub(r"\s+", " ", email)

        # Debugging: Print cleaned-up email content to verify
        print("Cleaned email content:")
        print(email)
        print("\n" + "-"*50 + "\n")

        trx = TransactionData()
        trx.is_incoming = False
        trx.payment_method = "UniPin"
        trx.extra_data = {}

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

        # Extract reference number
        reference_match = re.search(r"Nomor Referensi\s*(\S+)", email)
        if reference_match:
            trx.extra_data["reference_number"] = reference_match.group(1)

        # Extract product name
        product_match = re.search(r"Nama Barang\s*(.*?)\s*Nominal Transaksi", email)
        if product_match:
            trx.description = product_match.group(1).strip()

        # Extract transaction amount
        amount_match = re.search(r"Nominal Transaksi\s*Rp\s*([\d,]+)", email)
        if amount_match:
            trx.amount = Decimal(amount_match.group(1).replace(",", ""))

        # Extract user name
        username_match = re.search(r"Nama Pengguna\s*(.*?)\s*ID Pengguna", email)
        if username_match:
            trx.extra_data["user_name"] = username_match.group(1).strip()

        # Extract user ID
        user_id_match = re.search(r"ID Pengguna\s*(\d+)", email)
        if user_id_match:
            trx.extra_data["user_id"] = user_id_match.group(1)

        # Extract zone ID
        zone_id_match = re.search(r"ID Zona\s*(\d+)", email)
        if zone_id_match:
            trx.extra_data["zone_id"] = zone_id_match.group(1)

        return [trx]