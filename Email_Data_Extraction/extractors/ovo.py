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
        trx.payment_method = "OVO"
        trx.extra_data = {}

        # Extract payment amount (and display in thousand Rupiah)
        amount_match = re.search(r"Pembayaran Berhasil\s*-\s*(Rp[\d,]+)", email)
        if amount_match:
            amount_str = amount_match.group(1).replace("Rp", "").replace(",", "").strip()
            trx.amount = Decimal(amount_str)  # Remove dividing by 1000
            trx.currency = "IDR"

        # Extract transaction date
        date_match = re.search(r"(\d{1,2} \w{3} \d{4}, \d{2}:\d{2})", email)
        if date_match:
            trx.date = datetime.datetime.strptime(date_match.group(1), "%d %b %Y, %H:%M")

        # Extract merchant name
        merchant_match = re.search(r"Nama Toko\s*(.*?)\s*Lokasi", email)
        if merchant_match:
            trx.merchant = merchant_match.group(1).strip()

        # Extract reference number
        trx_id_match = re.search(r"No\. Referensi\s*(\S+)", email)
        if trx_id_match:
            trx.trx_id = trx_id_match.group(1)

        # Extract transaction code (No. Resi)
        transaction_code_match = re.search(r"No\. Resi \(Kode Transaksi\)\s*(\S+)", email)
        if transaction_code_match:
            trx.extra_data["transaction_code"] = transaction_code_match.group(1)

        # Extract approval code
        approval_code_match = re.search(r"Kode Approval\s*(\d+)", email)
        if approval_code_match:
            trx.extra_data["approval_code"] = approval_code_match.group(1)

        # Extract payment method
        payment_method_match = re.search(r"Metode Pembayaran\s*(.*)", email)
        if payment_method_match:
            trx.payment_method = payment_method_match.group(1).strip()

        # Extract issuer name
        issuer_match = re.search(r"Nama Issuer\s*(.*)", email)
        if issuer_match:
            trx.extra_data["issuer"] = issuer_match.group(1).strip()

        # Extract OVO ID
        ovo_id_match = re.search(r"OVO ID\s*(\d+)", email)
        if ovo_id_match:
            trx.extra_data["ovo_id"] = ovo_id_match.group(1)

        # Extract customer PAN
        customer_pan_match = re.search(r"Customer PAN\s*(\d+)", email)
        if customer_pan_match:
            trx.extra_data["customer_pan"] = customer_pan_match.group(1)

        return [trx]