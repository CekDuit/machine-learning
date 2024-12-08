import re
from decimal import Decimal
from datetime import datetime
from .base_extractor import BaseExtractor, EmailContent, TransactionData

class OVOExtractor(BaseExtractor):
    def match(self, title: str, email_from: str) -> bool:
        """
        Check if the email matches the OVO payment confirmation format.
        """
        return title == "OVO QR Payment Receipt" and email_from == "noreply@ovo.co.id"
    
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
        trx.description = "OVO"

        # Extract payment amount (and display in thousand Rupiah)
        amount_match = re.search(r"Pembayaran\s*Rp(\d{1,3}(?:.\d{3})*)", email)
        if amount_match:
            amount_str = amount_match.group(1).replace(".", "")
            trx.amount = Decimal(amount_str)

        # Extract transaction date
        date_match = re.search(r"(\d{2})\s([A-Za-z]{3})\s(\d{2,4})(?:,\s(\d{2}):(\d{2})(?::(\d{2}))?)?", email)
        if date_match:
            # Extract day, month, year, and time components
            day = date_match.group(1)
            month = date_match.group(2)
            year = date_match.group(3)
            hour = date_match.group(4) or '00'  # Default to '00' if time is not provided
            minute = date_match.group(5) or '00'  # Default to '00' if time is not provided
            second = date_match.group(6) or '00'  # Default to '00' if time is not provided

            # Convert 2-digit year to 4-digit year
            if len(year) == 2:
                year = "20" + year

            # Mapping months to their numeric equivalents
            month_translation = {
                "Jan": "01", "Feb": "02", "Mar": "03", "Apr": "04", "May": "05", "Jun": "06",
                "Jul": "07", "Aug": "08", "Sep": "09", "Oct": "10", "Nov": "11", "Dec": "12"
            }

            # Convert month to its numeric representation
            month_numeric = month_translation.get(month, month)

            # Construct the final formatted date string
            formatted_date_str = f"{year}-{month_numeric}-{day} {hour}:{minute}:{second}"

            # Convert to datetime object
            trx.date = datetime.strptime(formatted_date_str, "%Y-%m-%d %H:%M:%S")

        # Extract merchant name
        merchant_match = re.search(r"Nama Toko\s*([^\n]+?)\s+Lokasi", email)
        r"Nama Toko\s+([^\n]+?)\s+Lokasi"
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
        fees_match = re.search(r"Tip\s*Rp([\d,]+)", email)
        if fees_match:
            trx.fees = fees_match.group(1)

        return [trx]