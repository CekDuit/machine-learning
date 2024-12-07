import re
from decimal import Decimal
from typing import Optional
from datetime import datetime
from .base_extractor import BaseExtractor, EmailContent, TransactionData

class OCBCExtractor(BaseExtractor):

    def match(self, title: str, email_from: str) -> bool:
        """
        Check if the email matches the OCBC payment receipt format.
        """
        return title in ["Successful Bill Payment", "TRANSFER DANA"] and email_from == "onlinetransaction@ocbc.id"

    def extract(self, content: EmailContent) -> list[TransactionData]:
        """
        Extract transactions from the OCBC email content.
        """
        email = content.get_plaintext()

        # Normalize whitespace
        email = re.sub(r"\s+", " ", email)

        trx = TransactionData()
        trx.is_incoming = False
        trx.payment_method = "OCBC"

        if self._is_extract_transfer(email):
            self._extract_transfer(email, trx)
        elif self._is_extract_top_up(email):
            self._extract_top_up(email, trx)

        return [trx]
    
    def _is_extract_transfer(self, email: str) -> bool:
        """
        Check if the email is a transfer receipt.
        """
        return "TRANSFER DANA" in email
    
    def _is_extract_top_up(self, email: str) -> Optional[bool]:
        """
        Check if the email is in the 'Successful Bill Payment' format for top-up.
        """
        if "Successful Bill Payment" in email or "Top Up" in email:
            return True
        return False
    
    def _extract_transfer(self, email: str, trx: TransactionData) -> None:
        """
        Extract the transfer details from the OCBC email.
        """
        # 4. Extract Nominal (Amount)
        nominal_pattern = r"Nominal\s*:\s*Rp\s*([\d\.]+),(\d{2})\s*"
        nominal_match = re.search(nominal_pattern, email)
        if nominal_match:
            # Remove thousands separator (.) and ignore the decimal part
            nominal_value = nominal_match.group(1).replace(".", "")  # Remove periods
            trx.currency = "IDR"  # Set currency
            trx.amount = Decimal(nominal_value)  # Convert to Decimal

        # Description (can be customized if needed, currently we set it as 'Transfer Dana')
        trx.description = "Transfer Dana"

        merchant_pattern = r"Nama Penerima\s*:\s*(.*?)\s*(?=\n|No Rekening Penerima)"
        merchant_match = re.search(merchant_pattern, email)
        if merchant_match:
            trx.merchant = merchant_match.group(1)

        # 8. Extract Transaction Date
        date_pattern = r"Tanggal Transaksi\s*:\s*(\d{2} \w+ \d{4})\s*"
        date_match = re.search(date_pattern, email)
        if date_match:
            trx.date = datetime.strptime(date_match.group(1), "%d %B %Y")

        # 9. Extract Transaction Time
        time_pattern = r"Waktu Transaksi\s*:\s*(\d{2}:\d{2}:\d{2})\s*"
        time_match = re.search(time_pattern, email)
        if time_match:
            # Combine the date and time into a full datetime object
            if trx.date:
                time_str = time_match.group(1)
                trx.date = datetime.combine(trx.date, datetime.strptime(time_str, "%H:%M:%S").time())

    def _extract_top_up(self, email: str, trx: TransactionData) -> Optional[bool]:
        """
        Extract details from the top-up email format.
        """
        # Extract the amount (remove 'IDR', commas, and parse the number)
        amount_pattern = r"IDR\s*([\d,]+)"
        amount_match = re.search(amount_pattern, email)
        if amount_match:
            # Remove commas and convert to Decimal
            amount_str = amount_match.group(1).replace(",", "")
            # Set currency
            trx.currency = "IDR"
            trx.amount = Decimal(amount_str)

        # Set description
        trx.description = "Top-up Payment"

        # Set merchant name
        merchant_pattern = r"TO\s*(.*?)\s*\d{10,}"
        merchant_match = re.search(merchant_pattern, email)
        trx.merchant = merchant_match.group(1) if merchant_match else None

        # Extract transaction date
        date_pattern = r"PAYMENT DATE:\s*(\d{2} \w+ \d{4} \d{2}:\d{2}:\d{2})"
        date_match = re.search(date_pattern, email)
        if date_match:
            trx.date = datetime.strptime(date_match.group(1), "%d %b %Y %H:%M:%S")        

    def _extract_value(self, pattern: str, email: str) -> Optional[str]:
        """
        Helper function to extract the first match of a given regex pattern from the email content.
        """
        match = re.search(pattern, email)
        return match.group(1) if match else None
